"""URLs for the sandbox demo."""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, reverse_lazy
from django.views.generic import RedirectView


urlpatterns = [
    # Admin URLs
    url(r'^admin/', admin.site.urls),
    # django-helcim URLs
    url(r'^helcim/', include('helcim.urls')),
    # Example app URLs
    url(r'^example/', include('example_app.urls', namespace='example')),
    # Redirect to example app
    url(
        r'^$',
        RedirectView.as_view(
            permanent=False, url=reverse_lazy('example:home')
        ),
    ),
]

# Additional URLs if site is run in debug mode
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
