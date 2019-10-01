"""
         _               _                    _               _              _        
        /\ \            / /\                /\ \             /\ \           / /\      
       /  \ \          / /  \              /  \ \           /  \ \         / /  \     
      / /\ \ \        / / /\ \            / /\ \ \         / /\ \ \       / / /\ \__  
     / / /\ \_\      / / /\ \ \          / / /\ \ \       / / /\ \_\     / / /\ \___\ 
    / /_/_ \/_/     / / /  \ \ \        / / /  \ \_\     / /_/_ \/_/     \ \ \ \/___/ 
   / /____/\       / / /___/ /\ \      / / /    \/_/    / /____/\         \ \ \       
  / /\____\/      / / /_____/ /\ \    / / /            / /\____\/     _    \ \ \      
 / / /           / /_________/\ \ \  / / /________    / / /______    /_/\__/ / /      
/ / /           / / /_       __\ \_\/ / /_________\  / / /_______\   \ \/___/ /       
\/_/            \_\___\     /____/_/\/____________/  \/__________/    \_____\/        
                                                                                      
"""

__author__ = """Vasily Sinitsin"""
__email__ = 'vasilysinitsin@protonmail.com'
__version__ = '0.1.0'
__license__ = 'MIT'

import json
import random
import string
import time

import requests

BASE_API_URL = 'https://tyrion.faceapp.io/api/v3.10/photos'  # Ensure no slash at the end.
BASE_HEADERS = {'User-agent': "FaceApp/3.2.1 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M; wv)",
                'Content-Type': 'application/x-faceapp-payload',
                'X-FaceApp-AppLaunched': str(int(time.time()))
                }
DEVICE_ID_LENGTH = 8


def refresh_token(faceapp_token, device_id):
    burp0_headers = {"X-FaceApp-DeviceID": device_id, "X-FaceApp-AppLaunched": str(round(time.time())),
                     "X-FaceApp-UserToken": faceapp_token,
                     "User-Agent": "FaceApp/3.2.1 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M; wv)",
                     "Accept-Language": "ru-RU", "Content-Type": "application/json; charset=UTF-8",
                     "Connection": "close"}
    req = requests.post("https://api.faceapp.io:443/api/v3.0/auth/user/credentials", headers=burp0_headers)

    resp_json = req.json()
    try:
        faceapp_token = resp_json['user_token']
    except KeyError:
        faceapp_token = -1

    return faceapp_token


def child_parse(obj):
    rets = {}
    if obj['type'] == 'folder':
        for curr in obj['children']:
            rets.update(child_parse(curr))
    elif obj['type'] == 'filter':
        if not obj['is_paid']:
            rets[obj['id']] = obj
    return rets


class FaceAppImage(object):
    def __init__(self, url=None, file=None, code=None, device_id=None, user_token=None):
        """
        Class is initialized via image url, file or both code and device_id. Expect IllegalArgSet exception if set is
        wrong.
        Initializing with code and device_id may be useful to rebuild class from plain data.
        :param url: direct link to the image.
        :param file: image file.
        :param code: code of already uploaded to FaceApp file.
        :param device_id: device id should match one that was used for uploading.
        """

        self.code = None
        self.device_id = None

        # To be used for debugging
        self._request = None

        if (url or file) and not (url and file) and not code:
            if not device_id:
                device_id = self._generate_device_id()
            headers = self._generate_headers(device_id, user_token)
            self.headers = headers

            if file:  # Just to be understandable.
                pass

            elif url:
                file = requests.get(url).content

            with open('2.jpg', 'wb') as f:
                f.write(file)
            file = open('2.jpg', 'rb')

            post = requests.post(BASE_API_URL, headers=headers, files={'file': file})
            code = str(post.headers)

            self._request = post

            if not code:
                error = post.headers['X-FaceApp-ErrorCode']
                if error == 'photo_bad_type':
                    raise BadImageType('Bad image provided.')
                elif error == 'photo_no_faces':
                    raise ImageHasNoFaces('No faces on this image.')
                elif error == 'too_many_requests':
                    raise TooManyRequests('Too many requests or token expired')
                else:
                    raise BaseFacesException(error)

            self.code = code
            self.device_id = device_id
            face = random.choice(post.json()['faces_p'])['id']
            self.face = face

        elif (code and device_id) and not (url or file):
            self.code = code
            self.device_id = device_id

        else:
            raise IllegalArgSet('Wrong args set. Please use either url, file or code and device_id')

    def apply_filter(self, filter_name, cropped=False):
        """
        This method will apply FaceApp filter to uploaded image. You can apply filters multiple times with same class.
        :param filter_name: name of filter to be applied. List can be obtained from .filters property.
        :param cropped: provide True if you want FaceApp to crop image. True will be forced if filter is cropped-only.
        :return: binary of image.
        """
        code = self.code
        device_id = self.device_id
        headers = self.headers

        # Forcing cropped option for appropriate filters.

        url = '{}/{}/editor?filters={}&face_id=f1'.format(BASE_API_URL, code, filter_name)
        request = requests.get(
            url,
            headers=headers)
        error = request.headers.get('X-FaceApp-ErrorCode')
        if len(request.content) > 10:
            return request.content
        if error:
            if error == 'bad_filter_id':
                raise BadFilterID('Filter id is bad.')
            else:
                raise BaseFacesException(error)

        return request.content

    @property
    def filters(self):
        """
        :return: list of filter names to use in apply_filter.
        """
        return self._get_filters_list()

    def to_json(self):
        """
        This method will dump instance data to json string. Then class can be recreated with from_json class method.
        It is handy when you have uploader-worker application and have to pass data between.
        :return: json string.
        """
        dump_dict = {'code': self.code, 'device_id': self.device_id}
        return json.dumps(dump_dict)

    @classmethod
    def from_json(cls, json_string):
        """
        This class method will rebuild a class.
        :param json_string: obtained from to_json method.
        :return: FaceAppImage instance.
        """
        data_dict = json.loads(json_string)
        code = data_dict['code']
        device_id = data_dict['device_id']
        return cls(code=code, device_id=device_id)

    @staticmethod
    def _generate_device_id():
        """
        This method will generate device id according to DEVICE_ID_LENGTH.
        :return: device id.
        """
        device_id = ''.join(random.choice(string.ascii_letters) for _ in range(DEVICE_ID_LENGTH))
        return device_id

    @staticmethod
    def _generate_headers(device_id, user_token):
        """
        This method will compile BASE_HEADERS with provided device id.
        :param device_id: device id.
        :return: headers dict to be handled by requests.
        """
        hhhe = {'X-FaceApp-DeviceID': device_id}
        if user_token:
            hhhe['X-FaceApp-UserToken'] = user_token
        BASE_HEADERS.update(hhhe)
        return BASE_HEADERS

    @property
    def _only_cropped(self):
        # print(self._get_filters_list())
        """
        :return: list of filters supported only with cropped option.
        """
        return [face_app_filter['id'] for face_app_filter in self._get_filters_list() if
                not face_app_filter['is_paid']]

    def __str__(self):
        return 'FaceAppImage#{}'.format(self.code)

    def _get_filters_list(self):
        rets = {}
        for obj in self._request.json()['objects']:
            rets.update(child_parse(obj))
        return rets


class IllegalArgSet(ValueError):
    """
    Expect this when exclusive or none args provided.
    """
    pass


class BaseFacesException(Exception):
    """
    This is a general module exception. It will show error string received from FaceApp.
    """
    pass


class BadImageType(BaseFacesException):
    """
    Expect this when bad file provided or url returns anything except image.
    """
    pass


class ImageHasNoFaces(BaseFacesException):
    """
    Expect this when FaceApp recognize no faces on image.
    """
    pass


class BadFilterID(BaseFacesException):
    """
    Expect this when FaceApp has no such filter.
    """
    pass


class TooManyRequests(BaseFacesException):
    """
    Expect this when FaceApp has no such filter.
    """
    pass
