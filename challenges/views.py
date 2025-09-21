import os
import subprocess
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import CTFChallenge, CompletedChallenge, ActiveContainer
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from .utils import generate_project_name, find_free_port, create_temp_compose_with_port
from django.contrib import messages
from user_management.models import UserProfile
import time


@login_required
def spawn_challenge(request, pk):
    challenge = get_object_or_404(CTFChallenge, pk=pk)
    base_dir = os.path.abspath(challenge.compose_path)
    compose_file = os.path.join(base_dir, "docker-compose.yml")

    # print("compose_dir =", base_dir)
    # print("compose_file =", compose_file)

    # Static challenges: nothing to spawn, just show files/URL
    if challenge.is_static or not challenge.compose_path:
        messages.info(request, "This challenge does not require starting a container.")
        return redirect('challenge_detail', pk=pk)

    # Shared challenge: run shared compose once and show its host_port
    if not challenge.is_isolated:
        # optional: only bring up if not already up
        project_name = f"shared_ch{challenge.id}"
        try:
            subprocess.run(
                ["docker-compose", "-p", project_name, "-f", compose_file, "up", "-d"],
                cwd=base_dir,
                check=True,
                # stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            messages.success(request, "Shared challenge environment started (if not already).")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Error starting shared container: {e.stderr.decode() if e.stderr else str(e)}")
        return redirect('challenge_detail', pk=pk)

    # ====== Isolated challenge (per-user instance) ======
    existing = ActiveContainer.objects.filter(user=request.user, challenge=challenge).first()
    if existing:
        messages.info(request, "You already have an active instance for this challenge.")
        return redirect('challenge_detail', pk=pk)

    # find a free host port
    host_port = find_free_port()

    # create temp compose
    compose_file = os.path.join(challenge.compose_path, "docker-compose.yml")
    tmp_compose_path, modified = create_temp_compose_with_port(
        compose_file,
        challenge.internal_port,
        host_port
    )

    project_name = generate_project_name(request.user, challenge)
    base_dir = os.path.abspath(challenge.compose_path)

    # === Run docker-compose without check=True, capture all output ===
    result = subprocess.run(
        ["docker-compose", "-p", project_name, "-f", tmp_compose_path, "up", "-d"],
        cwd=base_dir,
        check=True,
    )

    if result.returncode != 0:
        messages.error(request, f"Failed to start isolated container: {result.stderr}")
        return redirect('challenge_detail', pk=pk)

    # Save ActiveContainer
    ActiveContainer.objects.create(
        user=request.user,
        challenge=challenge,
        project_name=project_name,
        host_port=host_port,
        compose_temp_path=tmp_compose_path
    )

    messages.success(request, "Your isolated challenge instance has been launched.")
    return redirect('challenge_detail', pk=pk)


@login_required
def stop_challenge(request, pk):
    """
    Stop and remove the user's isolated container instance for a given challenge.
    For shared challenges, optionally stop the shared container if admin.
    """
    challenge = get_object_or_404(CTFChallenge, pk=pk)

    if not challenge.is_isolated:
        # optionally: stop shared container (be careful)
        project_name = f"shared_ch{challenge.id}"
        try:
            subprocess.run(
                ["docker-compose", "-p", project_name, "-f", challenge.compose_path, "down"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            messages.success(request, "Shared challenge environment stopped.")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Error stopping shared container: {e.stderr.decode() if e.stderr else str(e)}")
        return redirect('challenge_detail', pk=pk)

    # isolated -> find user's ActiveContainer
    existing = ActiveContainer.objects.filter(user=request.user, challenge=challenge).first()
    if not existing:
        messages.info(request, "You don't have an active instance to stop.")
        return redirect('challenge_detail', pk=pk)

    try:
        subprocess.run(
            ["docker-compose", "-p", existing.project_name, "-f", existing.compose_temp_path, "down"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        messages.error(request, f"Error stopping container: {e.stderr.decode() if e.stderr else str(e)}")
        # continue to remove DB record and temp file below

    # cleanup temp compose file
    try:
        if existing.compose_temp_path and os.path.exists(existing.compose_temp_path):
            os.remove(existing.compose_temp_path)
    except Exception:
        pass

    existing.delete()
    messages.success(request, "Your challenge instance has been stopped and removed.")
    return redirect('challenge_detail', pk=pk)


@login_required
def challenge_detail(request, pk):
    challenge = get_object_or_404(CTFChallenge, pk=pk)
    active_container = None
    shared_project_name = f"shared_ch{challenge.id}" if challenge.compose_path else None
    already_completed = CompletedChallenge.objects.filter(
        user=request.user,
        challenge=challenge
    ).exists()
    message = None

    if challenge.is_isolated:
        if request.user.is_authenticated:
            active_container = ActiveContainer.objects.filter(user=request.user, challenge=challenge).first()
    else:
        pass

    if request.method == 'POST':
        flag = request.POST.get('flag', '').strip()
        if flag and flag == challenge.flag:
            if not already_completed:
                # Mark challenge as completed
                CompletedChallenge.objects.create(
                    user=request.user,
                    challenge=challenge,
                    completed_at=timezone.now()
                )

                # Award points to UserProfile
                profile = UserProfile.objects.get(user=request.user)
                profile.score += challenge.points
                profile.save()

                message = "Correct flag! Points awarded."
                already_completed = True
            else:
                message = "You have already completed this challenge."
        else:
            message = "Incorrect flag. Try again!"
    return render(request, 'challenges/challenge_detail.html', {
        'challenge': challenge,
        "active_container": active_container,
        "shared_project_name": shared_project_name,
        'already_completed': already_completed,
        'message': message
    })


@login_required
def challenge_list(request):
    challenges = CTFChallenge.objects.all()

    # Filters
    search_query = request.GET.get("search", "")
    difficulty_filter = request.GET.get("difficulty", "")
    type_filter = request.GET.get("type", "")

    if search_query:
        challenges = challenges.filter(title__icontains=search_query)
    if difficulty_filter:
        challenges = challenges.filter(difficulty=difficulty_filter)
    if type_filter:
        challenges = challenges.filter(type=type_filter)

    # Pagination
    paginator = Paginator(challenges, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # User progress
    completed_ids = CompletedChallenge.objects.filter(user=request.user).values_list("challenge_id", flat=True)

    difficulties = CTFChallenge.objects.values_list("difficulty", flat=True).distinct()
    types = CTFChallenge.objects.values_list("type", flat=True).distinct()

    return render(request, "CTF/challenge_list.html", {
        "page_obj": page_obj,
        "difficulties": difficulties,
        "types": types,
        "search_query": search_query,
        "difficulty_filter": difficulty_filter,
        "type_filter": type_filter,
        "completed_ids": completed_ids,
    })

@require_POST
@login_required
def mark_completed(request, challenge_id: int):
    challenge = get_object_or_404(CTFChallenge, id=challenge_id)
    CompletedChallenge.objects.get_or_create(user=request.user, challenge=challenge)
    return redirect(request.META.get("HTTP_REFERER", "challenge_list"))