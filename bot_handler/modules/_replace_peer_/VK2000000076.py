import random
import re
import urllib.parse

import requests
import vk_api

from bot_handler.core.command import Command
from global_config import MY_HOME_IP
from global_config import VK_MY_TOKEN

myip = MY_HOME_IP
proxies = {
    'https': 'http://{}:38274'.format(myip),
    'http': 'http://{}:38274'.format(myip),
}


def get_answ(text):
    datas = text.split('\n')
    question = datas[2]
    pattern = re.match('([^0-9]*) ', datas[3])
    pattern = pattern[1].split(' ')

    lnn = re.search('([0-9]*) букв', datas[3])
    lnn = lnn[1]

    q = '' + question + ' "Ответ: "'
    q = urllib.parse.quote_plus(q)
    url = 'https://duckduckgo.com/html/?q=' + q
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': 'ax=v165-7',
    }
    req = requests.get(url, headers=headers)
    resp = req.text
    answ = re.search('Ответ: </b>([а-яА-Я]{' + str(lnn) + '})[^а-яА-Я]', resp, re.IGNORECASE)
    if answ:
        return answ[1]


@Command('usual_message', block='defaults', description='Handle usual message(without command)', disable_parser=True)
def usual_message(CurrentUse):
    if (CurrentUse.from_id == -166699484) and ('букв' in CurrentUse.text):
        answ = get_answ(CurrentUse.text)
        if not answ:
            payload = {"message": '*vikobot Закончить игру',
                       # "attachment": '',
                       'peer_id': 2000000000 + 339,
                       'random_id': random.randint(0, 100000)
                       }
            sess = vk_api.VkApi(token=VK_MY_TOKEN)
            resp = sess.method('messages.send', payload, raw=True)

            payload = {"message": '*vikobot начать игру',
                       # "attachment": '',
                       'peer_id': 2000000000 + 339,
                       'random_id': random.randint(0, 100000)
                       }
            sess = vk_api.VkApi(token=VK_MY_TOKEN)
            resp = sess.method('messages.send', payload, raw=True)

        else:
            payload = {"message": answ,
                       # "attachment": '',
                       'peer_id': 2000000000 + 339,
                       'random_id': random.randint(0, 100000)
                       }
            sess = vk_api.VkApi(token=VK_MY_TOKEN)
            resp = sess.method('messages.send', payload, raw=True)
            return resp
