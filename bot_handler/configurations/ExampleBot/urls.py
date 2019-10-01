from django.conf.urls import url

from bot_handler.core.messengers import VKMessenger, TGMessenger

vk_messenger = VKMessenger()
tg_messenger = TGMessenger()
urlpatterns = [

    url(r'^telegram$', tg_messenger.handle_request, name='tg_request_receiver'),
    url(r'^vkGroup$', vk_messenger.handle_request, name='vk_request_receiver'),
]
