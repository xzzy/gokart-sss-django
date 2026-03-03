import os
from django.apps import AppConfig
from django.conf import settings


class SssConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sss'

    def ready(self):
        session_path = getattr(settings, 'SESSION_FILE_PATH', None)
        if session_path and not os.path.exists(session_path):
            try:
                os.makedirs(session_path, exist_ok=True)
                print(f"Created session storage directory: {session_path}")
            except Exception as e:
                print(f"Warning: Could not create session storage directory {session_path}: {e}")
