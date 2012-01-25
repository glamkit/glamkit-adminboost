from django.contrib import admin

urlpatterns = getattr(admin.site, '_inline_urls', {}).values()
