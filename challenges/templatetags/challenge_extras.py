import os
from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_static_files(assets_path):
    abs_path = os.path.join(settings.BASE_DIR, 'static', assets_path)
    if os.path.exists(abs_path):
        return [
            os.path.join(assets_path, f)
            for f in os.listdir(abs_path)
            if os.path.isfile(os.path.join(abs_path, f))
        ]
    return []

@register.filter
def basename(path):
    return os.path.basename(path)
