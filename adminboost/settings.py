from django.conf import settings

ADMINBOOST_PREVIEW_SIZE = getattr(settings, 'ADMINBOOST_PREVIEW_SIZE',
    (300,300))