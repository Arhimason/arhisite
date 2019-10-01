from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot_handler/', include('bot_handler.urls')),
    path('token_handler/', include('token_handler.urls')),
]
