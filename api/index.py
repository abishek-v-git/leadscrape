# api\index.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "contact_search.settings")

application = get_wsgi_application()
