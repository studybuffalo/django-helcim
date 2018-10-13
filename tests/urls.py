"""Django URL file to get basic Django instance running."""

from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from oscar.app import application

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
urlpatterns += i18n_patterns(
    # Not sure if this will be required or not
    # url(r'^checkout/helcim/', include('helcim.urls')),
    url(r'', application.urls),
)
