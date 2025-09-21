import threading
import time
import subprocess
from django.utils import timezone
from challenges.models import CTFChallenge

MAX_LIFETIME_MINUTES = 30  # Shutdown after 30 minutes

def cleanup_loop():
    while True:
        now = timezone.now()
        for challenge in CTFChallenge.objects.exclude(last_launched__isnull=True):
            elapsed_minutes = (now - challenge.last_launched).total_seconds() / 60
            if elapsed_minutes > MAX_LIFETIME_MINUTES:
                subprocess.run(
                    ["docker-compose", "down"],
                    cwd=challenge.compose_path
                )
                challenge.last_launched = None
                challenge.save()
        time.sleep(300)  # Wait 5 minutes

def start_cleanup_thread():
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
