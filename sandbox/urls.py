"""URLs for the sandbox demo."""

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.urls import include, path

from applications.apps import application

# from paypal.payflow.dashboard.app import application as payflow
# from paypal.express.dashboard.app import application as express_dashboard

admin.autodiscover()

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # Admin URLs
    # NB: not officially supported with django-oscar; included for
    # debugging purposes only
    path('admin/', admin.site.urls),
    # django-oscar-helcim URLs
    path('checkout/helcim/', include('helcim.urls')),
    # django-oscar URLs
    path('', application.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
