import hashlib
import io
import random
import re
import time

import requests
import vk_api

from bot_handler.core.command import Command
from bot_handler.utils.storage import StorageC
from global_config import VK_MY_TOKEN, VK_MY_ID
from ._config import YANDEX_API_KEY
from .utils import faces

faceapp_data = StorageC(cmd='filter')
if 'token' not in faceapp_data:
    faceapp_data[
        'token'] = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjoiNmJiMzBiZTktODhiOC00MmJiLTlmYmMtOTVjZWZjNzM1Y2E2IiwiZGV2aWNlX2lkIjoiOGFkNjJiM2QyOWVkNGY1ZiIsImV4cCI6MTU0MjQ1OTI1MSwibGlmZXRpbWUiOjg2NDAwLCJ1c2VyX2lkIjoiZmItMjMxMzc0NDI0ODY2NzYxMyJ9.1RmWv5nLq36ZmT5BUkPWBIw1cgXUSO5QCuSgfst4lrFCYgtNj387VGgJmT0FSdRwx3TZUNBsU67FxU32Tn1ZsA'
    faceapp_data.save()


# ---------BotFunctions---------

@Command('filter', block='rjaki', description='Make rjachnoe photo',
         epilog="Attach photo or forward somebody's message or forward message with attached photo")
def photo_filter(CurrentUse):
    # return 'Временно отключено'
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    global faceapp_data
    faceapp_token = faceapp_data['token']

    # return {'message': 'Временно отключено блин!!'}
    device_id = '8ad62b3d29ed4f5f'
    filters = {'black_hair-stylist': {'title': 'Black', 'id': 'black_hair-stylist', 'button_icon': {
        'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/black_hair.male.0d1d1d5f5cf9.jpg',
        'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/black_hair.male.0d1d1d5f5cf9.jpg'}, 'type': 'filter',
                                      'is_paid': False},
               'blond_hair-stylist': {'title': 'Blond', 'id': 'blond_hair-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/blond_hair.male.ee65912d8faf.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/blond_hair.male.ee65912d8faf.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'brown_hair-stylist': {'title': 'Brown', 'id': 'brown_hair-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/brown_hair.male.ba9fadd6c5ed.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/brown_hair.male.ba9fadd6c5ed.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'red_hair-stylist': {'title': 'Red', 'id': 'red_hair-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/red_hair.male.f7fa8b6b94bb.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/red_hair.male.f7fa8b6b94bb.jpg'},
                                    'type': 'filter', 'is_paid': False},
               'tinted_hair-stylist': {'title': 'Tinted', 'id': 'tinted_hair-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/tinted_hair.male.51430cf64e00.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/tinted_hair.male.51430cf64e00.jpg'},
                                       'type': 'filter', 'is_paid': False},
               'bangs_2-stylist': {'title': 'Bangs', 'id': 'bangs_2-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/bangs_2.male.89b3ae214338.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/bangs_2.male.89b3ae214338.jpg'},
                                   'type': 'filter', 'is_paid': False},
               'hitman-stylist': {'title': 'Hitman', 'id': 'hitman-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hitman.cdc5d80966a8.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hitman.cdc5d80966a8.jpg'},
                                  'type': 'filter', 'is_paid': False},
               'long_hair-stylist': {'title': 'Long', 'id': 'long_hair-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/long_hair.male.fffe4ea6d5e4.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/long_hair.male.fffe4ea6d5e4.jpg'},
                                     'type': 'filter', 'is_paid': False},
               'wavy-stylist': {'title': 'Wavy', 'id': 'wavy-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/wavy.male.5d1fded4895d.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/wavy.male.5d1fded4895d.jpg'},
                                'type': 'filter', 'is_paid': False},
               'straight_hair-stylist': {'title': 'Straight', 'id': 'straight_hair-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/straight_hair.male.4c4004aec1c6.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/straight_hair.male.4c4004aec1c6.jpg'},
                                         'type': 'filter', 'is_paid': False},
               'glasses-stylist': {'title': 'Glasses', 'id': 'glasses-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/glasses.male.cc247a9cb956.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/glasses.male.cc247a9cb956.jpg'},
                                   'type': 'filter', 'is_paid': False},
               'sunglasses-stylist': {'title': 'Sunglasses', 'id': 'sunglasses-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/sunglasses.male.a4cb2407dd86.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/sunglasses.male.a4cb2407dd86.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'goatee-stylist': {'title': 'Goatee', 'id': 'goatee-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/goatee.63ced351f372.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/goatee.63ced351f372.jpg'},
                                  'type': 'filter', 'is_paid': False},
               'mustache-stylist': {'title': 'Mustache', 'id': 'mustache-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/mustache.6d1d52b2e660.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/mustache.6d1d52b2e660.jpg'},
                                    'type': 'filter', 'is_paid': False},
               'full_beard-stylist': {'title': 'Full beard', 'id': 'full_beard-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/full_beard.023795f91689.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/full_beard.023795f91689.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'shaved-stylist': {'title': 'Shaved', 'id': 'shaved-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/shaved.03e40fb3022f.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/shaved.03e40fb3022f.jpg'},
                                  'type': 'filter', 'is_paid': False},
               'grand_goatee-stylist': {'title': 'Grand goatee', 'id': 'grand_goatee-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/grand_goatee.7b829dd2403d.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/grand_goatee.7b829dd2403d.jpg'},
                                        'type': 'filter', 'is_paid': False},
               'hipster-stylist': {'title': 'Hipster', 'id': 'hipster-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hipster.2a2daa091a04.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hipster.2a2daa091a04.jpg'},
                                   'type': 'filter', 'is_paid': False},
               'lion-stylist': {'title': 'Lion', 'id': 'lion-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/lion.b6b2852d5e29.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/lion.b6b2852d5e29.jpg'}, 'type': 'filter',
                                'is_paid': False},
               'petit_goatee-stylist': {'title': 'Petite goatee', 'id': 'petit_goatee-stylist', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/petit_goatee.472da6f07ef2.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/petit_goatee.472da6f07ef2.jpg'},
                                        'type': 'filter', 'is_paid': False},
               'no-filter': {'title': 'Original', 'id': 'no-filter', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/no-filter.male.8027686273cc.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/no-filter.male.8027686273cc.jpg'},
                             'type': 'filter', 'is_paid': False}, 'smile_2': {'title': 'Smile', 'id': 'smile_2',
                                                                              'button_icon': {
                                                                                  'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/smile_2.male.ed0aac90e640.jpg',
                                                                                  'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/smile_2.male.ed0aac90e640.jpg'},
                                                                              'type': 'filter', 'is_paid': False},
               'old': {'title': 'Old', 'id': 'old', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/old.male.f2aab0b4f137.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/old.male.f2aab0b4f137.jpg'},
                       'type': 'filter', 'is_paid': False}, 'young': {'title': 'Young', 'id': 'young', 'button_icon': {
            'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/young.male.361ad86581c2.jpg',
            'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/young.male.361ad86581c2.jpg'}, 'type': 'filter',
                                                                      'is_paid': False},
               'black_hair': {'title': 'Black', 'preview_img_gender': 'm', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/black_hair.male.0d1d1d5f5cf9.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/black_hair.male.0d1d1d5f5cf9.jpg'},
                              'type': 'filter',
                              'preview_img_1': 'https://static.faceapp.io/imgs/v3/previews/default-preview.male.d81962467ef2.jpg',
                              'id': 'black_hair',
                              'preview_img_0': 'https://static.faceapp.io/imgs/v3/previews/default-preview.male.d81962467ef2.jpg',
                              'is_paid': False}, 'hipster': {'title': 'Hipster', 'preview_img_gender': 'm',
                                                             'button_icon': {
                                                                 'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hipster.2a2daa091a04.jpg',
                                                                 'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hipster.2a2daa091a04.jpg'},
                                                             'type': 'filter',
                                                             'preview_img_1': 'https://static.faceapp.io/imgs/v3/previews/beards.hipster.5d69af346432.jpg',
                                                             'id': 'hipster',
                                                             'preview_img_0': 'https://static.faceapp.io/imgs/v3/previews/original.male.11cf21978955.jpg',
                                                             'is_paid': False},
               'bangs_2': {'title': 'Bangs', 'preview_img_gender': 'm', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/bangs_2.male.89b3ae214338.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/bangs_2.male.89b3ae214338.jpg'},
                           'type': 'filter',
                           'preview_img_1': 'https://static.faceapp.io/imgs/v3/previews/default-preview.male.d81962467ef2.jpg',
                           'id': 'bangs_2',
                           'preview_img_0': 'https://static.faceapp.io/imgs/v3/previews/default-preview.male.d81962467ef2.jpg',
                           'is_paid': False}, 'female-cropped': {'title': 'Female', 'id': 'female-cropped',
                                                                 'button_icon': {
                                                                     'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/female.male.0c6e19cbfb1a.jpg',
                                                                     'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/female.male.0c6e19cbfb1a.jpg'},
                                                                 'type': 'filter', 'is_paid': False},
               'female_2-cropped': {'title': 'Female 2', 'id': 'female_2-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/female_2.male.261aaeb191fa.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/female_2.male.261aaeb191fa.jpg'},
                                    'type': 'filter', 'is_paid': False},
               'old-cropped': {'title': 'Old', 'id': 'old-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/old.male.f2aab0b4f137.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/old.male.f2aab0b4f137.jpg'},
                               'type': 'filter', 'is_paid': False},
               'young-cropped': {'title': 'Young', 'id': 'young-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/young.male.361ad86581c2.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/young.male.361ad86581c2.jpg'},
                                 'type': 'filter', 'is_paid': False},
               'heisenberg-cropped': {'title': 'Heisenberg', 'id': 'heisenberg-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/heisenberg.aa1eae10790f.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/heisenberg.aa1eae10790f.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'male-cropped': {'title': 'Male', 'id': 'male-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/male.male.1b4f560621c7.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/male.male.1b4f560621c7.jpg'},
                                'type': 'filter', 'is_paid': False},
               'smile_2-cropped': {'title': 'Smile', 'id': 'smile_2-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/smile_2.male.ed0aac90e640.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/smile_2.male.ed0aac90e640.jpg'},
                                   'type': 'filter', 'is_paid': False},
               'frown-cropped': {'title': 'Upset', 'id': 'frown-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/frown.male.292f73b9d7f1.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/frown.male.292f73b9d7f1.jpg'},
                                 'type': 'filter', 'is_paid': False}, 'hollywood-cropped': {'title': 'Hollywood',
                                                                                            'button_icon': {
                                                                                                'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/impression.male.73784ec9000d.jpg',
                                                                                                'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/impression.male.73784ec9000d.jpg'},
                                                                                            'type': 'filter',
                                                                                            'matching_paid_filter_id': 'impression',
                                                                                            'id': 'hollywood-cropped',
                                                                                            'is_paid': False},
               'makeup_2-cropped': {'title': 'Makeup 2', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/makeup.8dcfb3556357.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/makeup.8dcfb3556357.jpg'},
                                    'type': 'filter', 'matching_paid_filter_id': 'makeup_2', 'id': 'makeup_2-cropped',
                                    'is_paid': False},
               'black_hair-cropped': {'title': 'Black', 'id': 'black_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/black_hair.male.0d1d1d5f5cf9.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/black_hair.male.0d1d1d5f5cf9.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'blond_hair-cropped': {'title': 'Blond', 'id': 'blond_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/blond_hair.male.ee65912d8faf.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/blond_hair.male.ee65912d8faf.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'brown_hair-cropped': {'title': 'Brown', 'id': 'brown_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/brown_hair.male.ba9fadd6c5ed.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/brown_hair.male.ba9fadd6c5ed.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'red_hair-cropped': {'title': 'Red', 'id': 'red_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/red_hair.male.f7fa8b6b94bb.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/red_hair.male.f7fa8b6b94bb.jpg'},
                                    'type': 'filter', 'is_paid': False},
               'tinted_hair-cropped': {'title': 'Tinted', 'id': 'tinted_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/tinted_hair.male.51430cf64e00.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/tinted_hair.male.51430cf64e00.jpg'},
                                       'type': 'filter', 'is_paid': False},
               'bangs_2-cropped': {'title': 'Bangs', 'id': 'bangs_2-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/bangs_2.male.89b3ae214338.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/bangs_2.male.89b3ae214338.jpg'},
                                   'type': 'filter', 'is_paid': False},
               'hitman-cropped': {'title': 'Hitman', 'id': 'hitman-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hitman.cdc5d80966a8.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hitman.cdc5d80966a8.jpg'},
                                  'type': 'filter', 'is_paid': False},
               'long_hair-cropped': {'title': 'Long', 'id': 'long_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/long_hair.male.fffe4ea6d5e4.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/long_hair.male.fffe4ea6d5e4.jpg'},
                                     'type': 'filter', 'is_paid': False},
               'wavy-cropped': {'title': 'Wavy', 'id': 'wavy-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/wavy.male.5d1fded4895d.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/wavy.male.5d1fded4895d.jpg'},
                                'type': 'filter', 'is_paid': False},
               'straight_hair-cropped': {'title': 'Straight', 'id': 'straight_hair-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/straight_hair.male.4c4004aec1c6.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/straight_hair.male.4c4004aec1c6.jpg'},
                                         'type': 'filter', 'is_paid': False}, 'glasses-cropped': {'title': 'Glasses',
                                                                                                  'button_icon': {
                                                                                                      'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/glasses.male.cc247a9cb956.jpg',
                                                                                                      'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/glasses.male.cc247a9cb956.jpg'},
                                                                                                  'type': 'filter',
                                                                                                  'matching_paid_filter_id': 'glasses',
                                                                                                  'id': 'glasses-cropped',
                                                                                                  'is_paid': False},
               'sunglasses-cropped': {'title': 'Sunglasses', 'id': 'sunglasses-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/sunglasses.male.a4cb2407dd86.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/sunglasses.male.a4cb2407dd86.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'hipster-cropped': {'title': 'Hipster', 'id': 'hipster-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hipster.2a2daa091a04.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/hipster.2a2daa091a04.jpg'},
                                   'type': 'filter', 'is_paid': False}, 'goatee-cropped': {'title': 'Goatee',
                                                                                           'button_icon': {
                                                                                               'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/goatee.63ced351f372.jpg',
                                                                                               'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/goatee.63ced351f372.jpg'},
                                                                                           'type': 'filter',
                                                                                           'matching_paid_filter_id': 'goatee',
                                                                                           'id': 'goatee-cropped',
                                                                                           'is_paid': False},
               'mustache-cropped': {'title': 'Mustache', 'id': 'mustache-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/mustache.6d1d52b2e660.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/mustache.6d1d52b2e660.jpg'},
                                    'type': 'filter', 'is_paid': False},
               'full_beard-cropped': {'title': 'Full beard', 'id': 'full_beard-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/full_beard.023795f91689.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/full_beard.023795f91689.jpg'},
                                      'type': 'filter', 'is_paid': False},
               'shaved-cropped': {'title': 'Shaved', 'id': 'shaved-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/shaved.03e40fb3022f.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/shaved.03e40fb3022f.jpg'},
                                  'type': 'filter', 'is_paid': False},
               'grand_goatee-cropped': {'title': 'Grand goatee', 'id': 'grand_goatee-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/grand_goatee.7b829dd2403d.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/grand_goatee.7b829dd2403d.jpg'},
                                        'type': 'filter', 'is_paid': False},
               'lion-cropped': {'title': 'Lion', 'id': 'lion-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/lion.b6b2852d5e29.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/lion.b6b2852d5e29.jpg'}, 'type': 'filter',
                                'is_paid': False},
               'petit_goatee-cropped': {'title': 'Petite goatee', 'id': 'petit_goatee-cropped', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/petit_goatee.472da6f07ef2.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/petit_goatee.472da6f07ef2.jpg'},
                                        'type': 'filter', 'is_paid': False}, 'fun_hollywood': {'title': 'Hollywood',
                                                                                               'button_icon': {
                                                                                                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/hollywood.male.cf50a66f98f1.jpg',
                                                                                                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/hollywood.male.cf50a66f98f1.jpg'},
                                                                                               'text': 'What would you look like as a Hollywood Star?',
                                                                                               'type': 'filter',
                                                                                               'matching_paid_filter_id': 'impression',
                                                                                               'id': 'fun_hollywood',
                                                                                               'is_paid': False},
               'fun_long_hair': {'title': 'Long hair', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/long.male.9c607aac987a.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/long.male.9c607aac987a.jpg'},
                                 'text': 'What would you look like with long hair?', 'type': 'filter',
                                 'matching_paid_filter_id': 'long_hair', 'id': 'fun_long_hair', 'is_paid': False},
               'fun_old': {'title': 'Old', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/old.1107c4673343.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/old.1107c4673343.jpg'},
                           'text': 'What would you look like when you grow old?', 'type': 'filter',
                           'matching_paid_filter_id': 'old', 'id': 'fun_old', 'is_paid': False},
               'fun_young': {'title': 'Young', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/young.male.3e427d196abf.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/young.male.3e427d196abf.jpg'},
                             'text': 'What did you look like when you were younger?', 'type': 'filter',
                             'matching_paid_filter_id': 'young', 'id': 'fun_young', 'is_paid': False},
               'fun_female': {'title': 'Female', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/female_1.259558f20b74.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/female_1.259558f20b74.jpg'},
                              'text': 'What would you look like as a female?', 'type': 'filter', 'id': 'fun_female',
                              'is_paid': False}, 'fun_female_2': {'title': 'Female 2', 'button_icon': {
            'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/female_2.3c88fe5add51.jpg',
            'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/female_2.3c88fe5add51.jpg'},
                                                                  'text': 'What would you look like as a female?',
                                                                  'type': 'filter', 'id': 'fun_female_2',
                                                                  'is_paid': False},
               'fun_full_beard': {'title': 'Full beard', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/full_beard.d7d0aef4ce96.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/full_beard.d7d0aef4ce96.jpg'},
                                  'text': 'What would you look like with a full beard?', 'type': 'filter',
                                  'matching_paid_filter_id': 'full_beard', 'id': 'fun_full_beard', 'is_paid': False},
               'fun_blond_hair': {'title': 'Blond hair', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/blond.male.bc5889144b4f.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/blond.male.bc5889144b4f.jpg'},
                                  'text': 'What would you look like with blonde hair?', 'type': 'filter',
                                  'matching_paid_filter_id': 'blond_hair', 'id': 'fun_blond_hair', 'is_paid': False},
               'fun_black_hair': {'title': 'Black hair', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/black.male.ac1b3f0625da.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/black.male.ac1b3f0625da.jpg'},
                                  'text': 'What would you look like with black hair?', 'type': 'filter',
                                  'matching_paid_filter_id': 'black_hair', 'id': 'fun_black_hair', 'is_paid': False},
               'fun_brown_hair': {'title': 'Brown hair', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/brown.male.c64be53adcf9.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/brown.male.c64be53adcf9.jpg'},
                                  'text': 'What would you look like with brown hair?', 'type': 'filter',
                                  'matching_paid_filter_id': 'brown_hair', 'id': 'fun_brown_hair', 'is_paid': False},
               'fun_red_hair': {'title': 'Red hair', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/red.male.74d62a8e8eef.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/red.male.74d62a8e8eef.jpg'},
                                'text': 'What would you look like with red hair?', 'type': 'filter',
                                'matching_paid_filter_id': 'red_hair', 'id': 'fun_red_hair', 'is_paid': False},
               'fun_tinted_hair': {'title': 'Tinted hair', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/tinted.male.dc04f8bcee6a.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/tinted.male.dc04f8bcee6a.jpg'},
                                   'text': 'What would you look like if dye your hair?', 'type': 'filter',
                                   'matching_paid_filter_id': 'tinted_hair', 'id': 'fun_tinted_hair', 'is_paid': False},
               'fun_hitman': {'title': 'Hitman', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/hitman.ee835d5dd7fc.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/hitman.ee835d5dd7fc.jpg'},
                              'text': 'What do you look like as a Hitman?', 'type': 'filter',
                              'matching_paid_filter_id': 'hitman', 'id': 'fun_hitman', 'is_paid': False},
               'fun_upset': {'title': 'Upset', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/upset.male.a0cd719f3aa1.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/upset.male.a0cd719f3aa1.jpg'},
                             'text': 'What would you look like if you get upset?', 'type': 'filter',
                             'matching_paid_filter_id': 'frown', 'id': 'fun_upset', 'is_paid': False},
               'fun_smile': {'title': 'Smile', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/smile.male.0a58e73a567c.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/smile.male.0a58e73a567c.jpg'},
                             'text': 'What would you look like with a smile?', 'type': 'filter',
                             'matching_paid_filter_id': 'smile_2', 'id': 'fun_smile', 'is_paid': False},
               'fun_smile_tight': {'title': 'Tight smile', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/tight_smile.male.f6287837dbcf.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/tight_smile.male.f6287837dbcf.jpg'},
                                   'text': 'What would you look like with a tight smile?', 'type': 'filter',
                                   'matching_paid_filter_id': 'smile_tight', 'id': 'fun_smile_tight', 'is_paid': False},
               'fun_sunglasses': {'title': 'Sunglasses', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/sunglasses.male.7690e2cfee53.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/sunglasses.male.7690e2cfee53.jpg'},
                                  'text': 'What would you look like with sunglasses?', 'type': 'filter',
                                  'matching_paid_filter_id': 'sunglasses', 'id': 'fun_sunglasses', 'is_paid': False},
               'fun_glasses': {'title': 'Glasses', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/glasses.male.6dcd2f7b1d73.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/glasses.male.6dcd2f7b1d73.jpg'},
                               'text': 'What would you look like with glasses?', 'type': 'filter',
                               'matching_paid_filter_id': 'glasses', 'id': 'fun_glasses', 'is_paid': False},
               'fun_heisenberg': {'title': 'Heisenberg', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/heisenberg.3e7b450c4d19.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/heisenberg.3e7b450c4d19.jpg'},
                                  'text': 'What would you look like as a Heisenberg?', 'type': 'filter',
                                  'id': 'fun_heisenberg', 'is_paid': False}, 'fun_bangs': {'title': 'Bangs',
                                                                                           'button_icon': {
                                                                                               'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/bangs.male.e7e88ada6380.jpg',
                                                                                               'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/bangs.male.e7e88ada6380.jpg'},
                                                                                           'text': 'What would you look like with bangs?',
                                                                                           'type': 'filter',
                                                                                           'matching_paid_filter_id': 'bangs_2',
                                                                                           'id': 'fun_bangs',
                                                                                           'is_paid': False},
               'fun_mustache': {'title': 'Mustache', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/mustache.262920a94a08.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/mustache.262920a94a08.jpg'},
                                'text': 'What would you look like with a mustache?', 'type': 'filter',
                                'matching_paid_filter_id': 'mustache', 'id': 'fun_mustache', 'is_paid': False},
               'fun_goatee': {'title': 'Goatee', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/pan.21a5db030dd5.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/pan.21a5db030dd5.jpg'},
                              'text': 'What would you look like with a goatee beard?', 'type': 'filter',
                              'matching_paid_filter_id': 'goatee', 'id': 'fun_goatee', 'is_paid': False},
               'fun_male': {'title': 'Male', 'button_icon': {
                   'android_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/male.2853bda7bf7a.jpg',
                   'ios_image_url': 'https://static.faceapp.io/imgs/v3/thumbs/fun/male.2853bda7bf7a.jpg'},
                            'text': 'What would you look like as a male?', 'type': 'filter', 'id': 'fun_male',
                            'is_paid': False}}

    if parser_p.all:
        resp = 'Exiscting filters:\n'
        for filt in filters.keys():
            resp += filt + '\n'
        return resp

    if not parser_p.filter:
        parser_p.filter = random.choice(list(filters))

    if parser_p.filter not in filters:
        return 'Unknown filter'

    vk_session = CurrentUse.vk_group.api
    if event_p['attachments'] and (event_p['attachments'][0]['type'] == 'photo'):
        max_size = 0
        url = ''
        for cur_size in event_p['attachments'][0]['photo']['sizes']:
            sz = cur_size['width'] * cur_size['height']
            if sz > max_size:
                url = cur_size['url']
                max_size = sz
    elif event_p['fwd_messages']:
        if event_p['fwd_messages'][0]['attachments'] and (
                event_p['fwd_messages'][0]['attachments'][0]['type'] == 'photo'):
            first_attach = event_p['fwd_messages'][0]['attachments'][0]
            max_size = 0
            url = ''
            for cur_size in first_attach['photo']['sizes']:
                sz = cur_size['width'] * cur_size['height']
                if sz > max_size:
                    url = cur_size['url']
                    max_size = sz
        else:
            uid = event_p['fwd_messages'][0]['from_id']
            payload = {
                'user_ids': uid,
                'fields': 'photo_max_orig'
            }
            resp = vk_session.method('users.get', payload)
            url = resp[0]['photo_max_orig']
    else:
        uid = CurrentUse.from_id
        payload = {
            'user_ids': uid,
            'fields': 'photo_max_orig'
        }
        resp = vk_session.method('users.get', payload)
        url = resp[0]['photo_max_orig']

    retries = 0
    while 1:
        try:
            image = faces.FaceAppImage(url=url, user_token=faceapp_token, device_id=device_id)
            break
        except faces.ImageHasNoFaces:
            return 'Face not found'
        except faces.TooManyRequests:
            new_token = faces.refresh_token(faceapp_token, device_id)
            if new_token:
                faceapp_data['token'] = new_token
                faceapp_data.save()
                faceapp_token = new_token
            retries += 1
            if retries == 2:
                return 'Too many requests'

    # print(image.filters)
    file_bytes = image.apply_filter(parser_p.filter, cropped=True)

    upload = vk_api.upload.VkUpload(vk_session)
    file = io.BytesIO(file_bytes)
    photo = upload.photo_messages([file])[0]
    attach = 'photo' + str(photo['owner_id']) + '_' + str(photo['id'])

    return {'message': parser_p.filter, 'attachment': attach}


parser = photo_filter.parser
parser.add_argument('-f', dest='filter', help='select filter', type=str)
parser.add_argument('-a', dest='all', help='show existing filters', action='store_true')


@Command('sms', hidden=True,
         description='Send message to peer from ArhiBot', disable_parser=True)
def send_msg_to_conv(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    attachments = []
    for attach in event_p['attachments']:
        try:
            type = attach['type']
            id = attach[type]['id']
            owner_id = attach[type]['owner_id']
        except KeyError:
            continue
        try:
            access_key = '_' + attach[type]['access_key']
        except KeyError:
            access_key = ''
        attachments.append(type + str(owner_id) + '_' + str(id) + access_key)

    datas = re.match('(c?[0-9]*) ?(.*)', CurrentUse.text, re.DOTALL)
    if not datas:
        return {'message': 'Cheto ne tak'}
    peer_id = datas[1]
    if peer_id[0] == 'c':
        peer_id = 2000000000 + int(peer_id[1:])
    payload = {
        'peer_id': peer_id,
        'message': datas[2],
        'attachment': ','.join(attachments),
        'random_id': random.randint(0, 10000000)
    }
    resp = CurrentUse.vk_group.api.method('messages.send', payload)
    response = resp
    return response


@Command('кто', block='rjaki', description='Отвечает', disable_parser=True)
def who(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    starts = ['Я думаю, что это', 'Это определенно', 'Это', 'Я считаю, что это', '--->>']
    peer_id = event_p['peer_id']
    strr = event_p['text'].strip()
    if strr[-1] == '?':
        strr = strr[:-1]
    strr_md5_number = int(hashlib.md5(strr.encode('utf-8')).hexdigest(), 16)
    payload = {
        'peer_id': peer_id,
        'fields': 'first_name, last_name'
    }
    resp = CurrentUse.vk_group.api.method('messages.getConversationMembers', payload)

    max_r = -1
    ret_id = -1
    ret_info = ''
    for profile in resp['profiles']:
        idd = int(profile['id'])
        cur_diff = abs(idd * strr_md5_number) % 1125899839733759
        if cur_diff > max_r:
            max_r = cur_diff
            ret_id = idd
            ret_info = profile['first_name'] + ' ' + profile['last_name']

    respt = '{} {} ( vk.com/id{} )'.format(random.choice(starts), ret_info, ret_id)
    return respt


@Command('ктоб', block='rjaki', description='Отвечает', disable_parser=True, hidden=True)
def who_brute(CurrentUse):
    text = CurrentUse.text.strip().split(' ')
    need_id = int(text[0])
    strr = ' '.join(text[1:])

    if strr[-1] == '?':
        strr = strr[:-1]
    strr_md5_number = int(hashlib.md5(strr.encode('utf-8')).hexdigest(), 16)
    payload = {
        'peer_id': CurrentUse.peer_id,
        'fields': 'first_name, last_name'
    }
    resp = CurrentUse.vk_group.api.method('messages.getConversationMembers', payload)
    attempts = 1000
    while attempts > 0:
        max_r = -1
        ret_id = -1
        ret_info = ''
        for profile in resp['profiles']:
            idd = int(profile['id'])
            cur_diff = abs(idd * strr_md5_number) % 1125899839733759
            if cur_diff > max_r:
                max_r = cur_diff
                ret_id = idd
                ret_info = profile['first_name'] + ' ' + profile['last_name']
        if ret_id == need_id:
            return strr
        else:
            attempts -= 1
            strr += ')'
            strr_md5_number = int(hashlib.md5(strr.encode('utf-8')).hexdigest(), 16)


@Command('рандом', block='rjaki', description='рандомит')
def randomik(CurrentUse):
    if CurrentUse.parser_p.stop - CurrentUse.parser_p.start > 1000000000000:
        return 'Ненене'
    if CurrentUse.parser_p.count > 500:
        return 'Слишком многа хочешь'
    return '\n'.join([str(random.randint(CurrentUse.parser_p.start, CurrentUse.parser_p.stop)) for i in
                      range(CurrentUse.parser_p.count)])


parser = randomik.parser
parser.add_argument('start', type=int)
parser.add_argument('stop', type=int)
parser.add_argument('count', type=int, default=1, nargs='?')


@Command('destroy', block='raid',
         description='Make a razyob in conversation')
def destroy_conv(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    peer_id = event_p['peer_id']
    if parser_p.id:
        if CurrentUse.user.is_admin:
            peer_id = 2000000000 + parser_p.id
        else:
            return 'Ненене'
    chat_id = peer_id - 2000000000

    exc_ids = [VK_MY_ID, CurrentUse.vk_community.id, CurrentUse.from_id]
    code_exc = 'var exc_ids = [' + ','.join([str(x) for x in exc_ids]) + '];'
    code = code_exc + '''var msg_text = "{msg}";
    var tittle = "{tittle}";
    var peer_id = {peer};'''.format(msg='Ща будет разъеб', tittle='DESTROYED', peer=peer_id)
    code += '''
    var counter=0;
    var curuser; var members; var r; var rets = [];
    var cht_id = peer_id-2000000000;
    API.messages.send({"peer_id": peer_id, "message": msg_text});
    API.messages.editChat({"chat_id": cht_id, "title": tittle});
    API.messages.deleteChatPhoto({"chat_id":cht_id});
    members = API.messages.getConversationMembers({"peer_id": peer_id}).items;
    
    while (counter<21) {
        
        curuser = members.pop().member_id;
        if (exc_ids.indexOf(curuser)==-1){
            API.messages.removeChatUser({"member_id": curuser, "chat_id": cht_id});
        } 
        counter = counter+1;
    }   
    return members;
    '''

    payload = {
        'code': code,
    }
    vk_session = CurrentUse.vk_group.api
    resp = vk_session.method('execute', payload)
    members = []
    for member in resp:
        members.append(member['member_id'])

    if not members:
        return 'Badum tss!'

    while 1:
        code = code_exc + 'var members = [' + ','.join([str(x) for x in members]) + '];'
        code += '''
        var counter=0;
        var curuser;
        while (counter<25) {
            curuser = members.pop();
            if (exc_ids.indexOf(curuser)==-1){
                API.messages.removeChatUser({"member_id": curuser, "chat_id": ''' + str(chat_id) + '''});  
            }
            counter = counter+1;
        }   
        return members;
        '''
        payload = {
            'code': code,
        }
        members = vk_session.method('execute', payload)
        if not members:
            break

    return 'Badum tss!'


parser = destroy_conv.parser
parser.add_argument('-id', help='chat id', type=int)


@Command('скажи', block='rjaki',
         description='Говорит текст',
         disable_parser=False)
def text_to_speech(CurrentUse):
    parser_p = CurrentUse.parser_p
    url = "https://tts.voicetech.yandex.net/generate?format=mp3&quality={qa}&lang={lng}&speaker={spk}&speed={spd}&emotion={emot}&key={apikey}".format(
        qa=parser_p.quality,
        lng=parser_p.language,
        spk=parser_p.speaker,
        spd=parser_p.speed,
        emot=parser_p.emotion,
        apikey=YANDEX_API_KEY
    )
    req = requests.post(url, data={'text': ' '.join(parser_p.text)})
    data = req.content

    sess = CurrentUse.vk_group.api
    upl_url = sess.method('docs.getMessagesUploadServer', {'type': 'audio_message', 'peer_id': CurrentUse.peer_id})[
        'upload_url']
    req = requests.post(upl_url, files={'file': data})
    uplfle = req.json()['file']
    resp = sess.method('docs.save', {'file': uplfle})
    obj = resp[resp['type']]
    attachm = 'audio_message' + str(obj['owner_id']) + '_' + str(obj['id']) + '_' + str(obj['access_key'])

    return {'message': attachm, 'attachment': attachm, 'v': '5.101'}


parser = text_to_speech.parser
parser.add_argument('text', default='Ёбаный врот ты текст забыл', nargs='*')
parser.add_argument('-q', '--quality', default='hi')
parser.add_argument('-l', '--language', default='ru-RU')
parser.add_argument('-s', '--speaker', default='alyss')
parser.add_argument('-spd', '--speed', default=1.0, type=float)
parser.add_argument('-e', '--emotion', default='good')


@Command('рчат', block='rjaki', description='выдает рандомный чат вк', disable_parser=True)
def random_chat(CurrentUse):
    stor = CurrentUse.storage('c')
    if 'upd_time' not in stor:
        upd_time = 0
    else:
        upd_time = stor['upd_time']
    if (time.time() - upd_time) < (60 * 60 * 24):
        links_codes = stor['links_codes']
    else:
        code = '''  var resp = [];
                    var cresp = [];
                    var counter = 0;
                    var end_time = 0;
                    var randint = 56456;
    
                    while (counter<25) {
                        cresp = API.newsfeed.search({q: "vk.me/join", count: 200, end_time: end_time});
                        resp = resp + cresp.items@.text;
                        counter = counter+1;
                        end_time = cresp.items[-1].date;
                        if (resp.length==5000) {
                            return resp;
                        }
                    }
                    return resp;
        '''
        sess = vk_api.VkApi(token=VK_MY_TOKEN)
        resps = sess.method('execute', {'code': code})
        links_codes = []
        for resp in resps:
            link = re.search("https://vk\.me/join/([A-Za-z0-9_/]*)", resp)
            if link:
                links_codes.append(link[1])
        stor['links_codes'] = links_codes
        stor['upd_time'] = time.time()
        stor.save()
    return 'https://vk.me/join/' + random.choice(links_codes)
