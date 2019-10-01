# todo script easy manager with bot cmds and status and requirements and  ihihih cool
import sys

BASE_DIR = '/home/ec2-user/arhisite'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from bot_handler.CONFIG import VK_GROUP_TOKEN

from jconfig import Config
import time
import requests
import re
import random
from vk_api import VkApi
from fuzzywuzzy import fuzz
import logging
import html2text

logging.basicConfig(filename='freelansim.log', level=logging.INFO)
storage = Config('freelansim', 'fl_parsing.jconfig')
FREELANSIM_FORCE_UPD_TIMEOUT = 60 * 60 * 3
FREELANSIM_TIMEOUT = 120
KEYWORDS = ["WP", "Woocommerce", "WC", "Wordpress", 'вордпресс', 'парсер', 'python', 'питон', 'снифф']
NEED_RATIO = 90
CHAT_ID = 2000000088
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"

TASK_TEMPLATE = '''
{title}
{finance}

Теги:
{tags_raw}


{description}

{link}
'''


def get_latest_task_id():
    req = session.get("https://freelansim.ru:443/tasks")
    task_ids = re.findall('/tasks/([0-9]*)', req.text)

    if not task_ids:
        logging.error("Can't get latest task id")
        return storage['latest_id']

    mx = 0
    for tid in task_ids:
        tid = int(tid)
        if tid > mx:
            mx = tid
    logging.info('Latest task id {}'.format(mx))
    return mx


def get_tasks_info(task_ids):
    logging.info('Getting tasks info for tasks: {}'.format(str(task_ids)))
    if type(task_ids) != list:
        task_ids = [task_ids]
    resp_dict = {}
    for task_id in task_ids:
        logging.info("Parsing task {}".format(task_id))
        url = "https://freelansim.ru/tasks/{}".format(task_id)
        req = session.get(url)
        # print(req.text)
        if req.status_code != 200:
            if req.status_code == 404:
                logging.info('Task 404'.format(task_id))
                continue
            logging.critical('Unexpected response status: {}'.format(req.status_code))
            continue

        resp = req.text
        title = re.search("<h2 class='task__title'>\n([^<]*)\n.*\n([^<]*)", resp)
        if title:
            title = '{} {}'.format(title[1], title[2])
        else:
            logging.error("Can't parse title")
            title = None

        finance = re.search("<div class='task__finance'>\n<span class='count'>([^<]*)<span class='suffix'>([^<]*)",
                            resp)
        if finance:
            finance = '{} {}'.format(finance[1], finance[2])
        else:
            logging.error("Can't parse finance")
            finance = None

        tags = re.findall('">([^<]*)</a></li><', resp)
        if not tags:
            logging.error("Can't parse tags")

        description = re.search("<div class='task__description'>(.*?)</div>", resp, re.DOTALL)
        if description:
            description = description[1]
            description = html2text.html2text(description)
            # description = BeautifulSoup(description, "lxml").decode(pretty_print=True)
        else:
            logging.error("Can't parse description")
            description = None

        cur_info = {
            'id': task_id,
            'title': title,
            'finance': finance,
            'tags': tags,
            'tags_raw': ', '.join(tags),
            'description': description,
            'link': url
        }
        resp_dict[task_id] = cur_info

    return resp_dict


def check_task(task):
    logging.info("Checking task {id}".format(**task))
    for keyw in KEYWORDS:
        if 'tags' in task and task['tags']:
            for tag in task['tags']:
                cur_ratio = fuzz.ratio(keyw.lower(), tag.lower())
                if cur_ratio > NEED_RATIO:
                    logging.info("Good task. {} found in tags with ratio {}".format(keyw, cur_ratio))
                    return True
        if 'title' in task and task['title']:
            cur_ratio = fuzz.partial_ratio(keyw.lower(), task['title'].lower())
            if cur_ratio > NEED_RATIO:
                logging.info("Good task. {} found in title with ratio {}".format(keyw, cur_ratio))
                return True

        if 'description' in task and task['description']:
            cur_ratio = fuzz.partial_ratio(keyw.lower(), task['description'].lower())
            if cur_ratio > NEED_RATIO:
                logging.info("Good task. {} found in description with ratio {}".format(keyw, cur_ratio))
                return True

    logging.info("Bad task. Keywords not found")
    return False


def send_notify(text):
    payload = {
        'message': text,
        'peer_id': CHAT_ID,
        'random_id': random.randint(0, 1000000)
    }
    try:
        resp = sess.method('messages.send', payload)
        logging.info("Message sent")
        return 1
    except:
        logging.error("Error while sending message")
        return 0


sess = VkApi(token=VK_GROUP_TOKEN)
session = requests.session()
session.headers = {"Connection": "close",
                   "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
                   "X-Requested-With": "XMLHttpRequest",
                   "User-Agent": UA,
                   "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"}

if (storage['latest_id'] is None) or \
        storage['latest_id_upd'] and time.time() - storage['latest_id_upd'] > FREELANSIM_FORCE_UPD_TIMEOUT:
    logging.info("latest_id not found  or too old")
    storage['latest_id'] = get_latest_task_id()
    storage['latest_id_upd'] = time.time()
    storage.save()

while 1:
    cur_latest_id = get_latest_task_id()
    if cur_latest_id == storage['latest_id']:
        time.sleep(FREELANSIM_TIMEOUT)
        continue

    old_latest_id = storage['latest_id']
    storage['latest_id'] = cur_latest_id
    storage['latest_id_upd'] = time.time()
    storage.save()

    new_tasks = get_tasks_info(list(range(old_latest_id + 2, cur_latest_id + 1, 2)))

    for task_id, task in new_tasks.items():
        is_good = check_task(task)
        if not is_good:
            continue

        task_text = TASK_TEMPLATE.format(**task)
        send_notify(task_text)
