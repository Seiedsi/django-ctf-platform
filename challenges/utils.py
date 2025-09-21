import os
import socket
import tempfile
import shutil
import random
import string
import yaml
from pathlib import Path

def find_free_port(start=20000, end=60000):
    """
    Returns a free TCP port on the host by trying to bind ephemeral sockets.
    We select random ports in a range to avoid collisions.
    """
    for _ in range(100):
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    # fallback: bind 0 to let OS pick (rare)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        return s.getsockname()[1]


def generate_project_name(user, challenge):
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"user{user.id}_ch{challenge.id}_{rand}"


def create_temp_compose_with_port(original_compose_path, original_internal_port, new_host_port):
    """
    Copy the challenge's docker-compose.yml into the challenge base folder,
    patch the ports, and save as a temporary compose file (unique name).
    Returns the path to the new file and whether it was modified.
    """
    # Ensure the original compose exists
    if not os.path.isfile(original_compose_path):
        raise FileNotFoundError(f"Compose file not found: {original_compose_path}")

    # Load the original docker-compose.yml
    with open(original_compose_path, "r") as f:
        compose = yaml.safe_load(f)

    modified = False
    services = compose.get("services", {})
    for svc_name, svc in services.items():
        ports = svc.get("ports")
        if not ports:
            continue
        new_ports = []
        for p in ports:
            if isinstance(p, str):
                if ":" in p:
                    host_part, container_part = p.split(":")[-2:] if p.count(":") >= 2 else p.split(":")
                    try:
                        container_port = int(container_part)
                        if container_port == original_internal_port:
                            if p.count(":") == 2:  # e.g. "127.0.0.1:49070:49070"
                                new_p = f"{host_part.split(':')[0]}:{new_host_port}:{container_part}"
                            else:
                                new_p = f"{new_host_port}:{container_part}"
                            new_ports.append(new_p)
                            modified = True
                            continue
                    except ValueError:
                        pass
                else:
                    try:
                        container_port = int(p)
                        if container_port == original_internal_port:
                            new_ports.append(f"{new_host_port}:{container_port}")
                            modified = True
                            continue
                    except ValueError:
                        pass
                new_ports.append(p)
            elif isinstance(p, dict):
                target = p.get("target")
                if target == original_internal_port:
                    p["published"] = new_host_port
                    modified = True
                new_ports.append(p)
            else:
                new_ports.append(p)
        if modified:
            svc["ports"] = new_ports
            compose["services"][svc_name] = svc

    # Save the modified docker-compose.yml into the challenge's base folder
    base_dir = Path(original_compose_path).resolve().parent
    tmp_file = base_dir / f"docker-compose.temp_{os.getpid()}_{random.randint(1000, 9999)}.yml"

    with open(tmp_file, "w") as f:
        yaml.safe_dump(compose, f)

    print("DEBUG created temporary compose file:", tmp_file)
    return str(tmp_file), modified



