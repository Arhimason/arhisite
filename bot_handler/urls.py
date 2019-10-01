from django.conf.urls import url
from django.urls import path, include

from arhisite.settings import BOT_CONFIGURATION
from . import views

# todo diff configurations on diff urls???

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^login$', views.auth, name='auth'),

    path(r'', include(BOT_CONFIGURATION + '.urls')),

]
