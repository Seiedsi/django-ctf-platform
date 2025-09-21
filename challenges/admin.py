from django.contrib import admin
from .models import CTFChallenge, CompletedChallenge, ActiveContainer

admin.site.register(CTFChallenge)
admin.site.register(CompletedChallenge)
admin.site.register(ActiveContainer)
