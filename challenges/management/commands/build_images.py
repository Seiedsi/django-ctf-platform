import os, docker
from django.core.management.base import BaseCommand

from challenges.models import CTFChallenge


class Command(BaseCommand):
    help = "Build Docker images for all challenges"

    def handle(self, *args, **opts):
        client = docker.from_env()
        base_path = os.path.abspath(os.path.join(os.getcwd(), "..", "CTF\containers"))

        for challenge in CTFChallenge.objects.all() and challenge.title == "":
            path = os.path.join(base_path, challenge.docker_image)
            self.stdout.write(f"Building image for {challenge.title} from {path}")
            image, _ = client.images.build(path=path, tag=challenge.docker_image)
            self.stdout.write(self.style.SUCCESS(f"Built {challenge.docker_image}"))
