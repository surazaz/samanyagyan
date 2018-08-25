"""
WSGI config for learnclass project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learnclass.settings")
from whitenoise import WhiteNoise
application = get_wsgi_application()
print(application)
application = WhiteNoise(application)
print(application)