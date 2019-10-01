from django.conf.urls import url

from bot_handler import handler

urlpatterns = [

    url(r'^telegram$', handler.tg_request_receiver, name='tg_request_receiver'),
    url(r'^vkGroup$', handler.vk_request_receiver, name='vk_request_receiver'),

]
