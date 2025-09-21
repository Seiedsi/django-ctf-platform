from django.apps import AppConfig


class ChallengesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "challenges"

    def ready(self):
        from .management.commands.cleanup_scheduler import start_cleanup_thread
        start_cleanup_thread()
