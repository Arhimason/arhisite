from channels.generic.websocket import WebsocketConsumer

from bot_handler.core.messengers import WEBMessenger

web_messenger = WEBMessenger()


class BotConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        web_messenger.handle_request(text_data, self)
