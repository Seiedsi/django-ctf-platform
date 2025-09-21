# Django CTF Platform

A **Capture The Flag (CTF) platform** built with **Django** and **Docker**, designed for learning and practicing **web penetration testing**.  
This project was developed as a **Bachelor’s Thesis in Computer Engineering** and provides an environment where users can register, attempt security challenges, submit flags, and track their scores on a leaderboard.

---

## Features

- **User Authentication**
  - Register, login, email verification, and password reset.
  - User profiles with persistent scores.

- **Gamification**
  - Points awarded for solving challenges.
  - Leaderboard with ranking.
  - User dashboard with progress and completed challenges.

- **Challenges Management**
  - Supports **Dockerized challenges** using `docker-compose`.
  - Two execution modes:
    - **Shared challenges** → one container for all users.
    - **Isolated challenges** → each user gets their own container with dynamic port mapping.
  - Supports **static challenges** (images, audio files, PDFs, etc.) stored in `/static/assets/`.

- **Resource Management**
  - Automatic cleanup of unused containers after inactivity.
  - Temporary docker-compose files auto-removed after shutdown.

- **Admin & Extensibility**
  - Easy to add new challenges through the database.
  - Compatible with public CTF repositories (e.g. [UrmiaCTF-2023](https://github.com/UrmiaCTF/UCTF-2023)).

---

## Tech Stack

- **Backend:** Django 4.x  
- **Frontend:** Bootstrap 5  
- **Database:** SQLite (development) / PostgreSQL (production recommended)  
- **Containerization:** Docker & Docker Compose  
- **Language:** Python 3.10+  

---

## Installation

### 1. Clone the repo
```bash
git clone https://github.com/USERNAME/django-ctf-platform.git
cd django-ctf-platform
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

pip install -r requirements.txt

```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Create a superuser
```bash
python manage.py createsuperuser
```

### 5. Start the server
```bash
python manage.py runserver
```

### 6. Launch challenges
  - Shared or isolated challenges can be started directly from the Challenge Detail page.

  - Static challenges are accessible via direct links.

---

## Project Structure

```bash
CTF/
 ├── accounts/           # User authentication & profiles
 ├── challenges/         # Challenge models, views, spawning logic
 ├── containers/         # Docker challenge directories
 ├── static/assets/      # Static challenges (images, files, etc.)
 ├── templates/          # HTML templates (Bootstrap-based)
 ├── db.sqlite3          # Development database (ignored in .gitignore)
 ├── manage.py
 └── requirements.txt
```

---

## Flags & Security Notice

- All flags inside challenges are placeholders (e.g., FLAG{example_flag}) for demonstration.

- Replace them with your own flags when deploying in real environments.

- Never expose real flags or sensitive data in public repositories.

---

## Use Cases

- Academic projects for computer engineering / cybersecurity students.

- Internal training platform for organizations.

- Personal portfolio project to showcase Django, Docker, and Security Engineering skills.

---

## Future Improvements

- Kubernetes support for large-scale deployments.

- Real-time container monitoring.

- Support for multi-user competitions.

- Advanced challenge types (reverse engineering, binary exploitation).

---

## License

This project is released under the MIT License. You are free to use, modify, and distribute it with attribution.
