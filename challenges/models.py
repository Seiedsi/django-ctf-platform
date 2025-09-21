from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class CTFChallenge(models.Model):
    DIFFICULTY_LEVELS = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, null=True, blank=True)
    points = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=200)
    flag=models.CharField(max_length=200, null=True)
    compose_path = models.CharField(max_length=200, blank=True, null=True)
    host_port = models.IntegerField(blank=True, null=True)
    internal_port = models.PositiveIntegerField(blank=True, null=True,
        help_text="Port inside container to expose (e.g. 5000, 80, 3000)"
    )
    last_launched = models.DateTimeField(blank=True, null=True)
    is_static = models.BooleanField(default=False)
    is_isolated = models.BooleanField(default=False)

    def get_static_assets_path(self):
        """
        Relative path to static assets folder for this challenge.
        Example: assets/reverse-image
        """
        return f"assets/{slugify(self.title)}"

    def __str__(self) -> str:
        return f"{self.title}"


class CompletedChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CTFChallenge, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "challenge")

    def __str__(self) -> str:
        return f"{self.user.username} - {self.challenge.title}"


class ActiveContainer(models.Model):
    """
    Tracks active per-user container instances (only used for isolated challenges).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(CTFChallenge, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=150, unique=True)
    host_port = models.IntegerField()  # host port that maps to container's internal_port
    compose_temp_path = models.CharField(max_length=1024, blank=True, null=True)  # temp file path
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.project_name})"