"""URLs for the sandbox demo."""

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.urls import include

from applications.apps import application

admin.autodiscover()

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    # Admin URLs
    # NB: not officially supported with django-oscar; included for
    # debugging purposes only
    url(r'^admin/', admin.site.urls),
    # django-helcim URLs
    url(r'^checkout/helcim/', include('helcim.urls')),
    # django-oscar URLs
    url(r'', application.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
