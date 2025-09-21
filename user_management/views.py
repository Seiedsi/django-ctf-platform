from .models import UserProfile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from challenges.models import CompletedChallenge


@login_required
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        user = request.user
        user.username = username
        user.email = email
        user.save()

        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Prevent logout after password change
            messages.success(request, "Profile and password updated.")
        else:
            messages.error(request, "Error updating password.")

        return redirect("dashboard")

    password_form = PasswordChangeForm(request.user)
    return render(request, "edit_profile.html", {
        "password_form": password_form,
    })


@login_required
def dashboard_view(request):
    profile = UserProfile.objects.get(user=request.user)
    logs = CompletedChallenge.objects.filter(user=request.user).select_related("challenge")
    total_points = profile.score

    # Leaderboard: directly from profile scores
    users = UserProfile.objects.all()
    leaderboard = [(u.user, u.score) for u in users]  # use u.user for username/email
    leaderboard.sort(key=lambda x: x[1], reverse=True)

    # Get current user's rank
    rank = [u[0] for u in leaderboard].index(request.user) + 1

    return render(request, "dashboard.html", {
        "user": request.user,          # Django auth user
        "profile": profile,            # UserProfile object
        "logs": logs,
        "total_points": total_points,
        "rank": rank,
        "leaderboard": leaderboard[:10],
    })


@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("register")
    return render(request, "delete_confirm.html")


def home(request):
    return render(request, 'CTF/home.html')


def user_home(request):
    return render(request, 'CTF/user_home.html')


def logout_view(request):
    logout(request)
    return redirect('home')


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return HttpResponse("Email verified successfully.")
            else:
                return HttpResponse("Invalid token.")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse("Invalid verification link.")


def send_verification_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"http://127.0.0.1:8000{reverse('verify_email', kwargs={'uidb64': uid, 'token': token})}"
    send_mail(
        "Verify Your Email",
        f"Click the link to verify your email: {link}",
        "alibirashk82@gmail.com",
        [user.email],
        fail_silently=False,
    )


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("user_home")  # Adjust to your landing page
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")


class RegisterView(View):
    def get(self, request):
        return render(request, "CTF/register.html")

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # Create user with inactive status until email is verified
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        # Send verification email
        send_verification_email(user)

        messages.success(request, "Account created! Please check your email to verify before logging in.")
        return redirect("login")