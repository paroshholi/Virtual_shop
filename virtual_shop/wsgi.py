"""
WSGI config for virtual_shop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import nltk

from django.core.wsgi import get_wsgi_application

nltk.download('punkt')
nltk.download('wordnet')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_shop.settings')

application = get_wsgi_application()
