import hashlib
import random
import re
import time

import cfscrape

ERR_ATTEMPTS = 3
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"

session = cfscrape.create_scraper()
session.headers = {"Connection": "close", "Accept": "application/json, text/javascript, */*; q=0.01", "DNT": "1",
                   "X-Requested-With": "XMLHttpRequest",
                   "User-Agent": UA,
                   "Referer": "https://temp-mail.org/ru/option/change/", "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"}


def generate_nick(length, pnt):
    VOWELS = "aeiou"
    CONSONANTS = "".join(set('abcdefghijklmnopqrstuvwxyz') - set(VOWELS))
    word = ""
    for i in range(length):
        if i % 2 == 0:
            char = random.choice(CONSONANTS)
        else:
            char = random.choice(VOWELS)
        if i == 0 or i == pnt:
            char = char.upper()
        word += char
    return word


def get_domains():
    global domains, domains_upd_time
    if len(domains) and (time.time() - domains_upd_time) < 60 * 60 * 2:
        return domains
    req = session.get('https://api4.temp-mail.org/request/domains/format/json')
    domains_loc = req.json()
    for i in range(len(domains_loc)):
        domains_loc[i] = domains_loc[i][1:]
    domains = domains_loc
    domains_upd_time = time.time()
    return domains


domains = []
domains_upd_time = 0


class TempMail:
    def __init__(self, mail=None):
        global burp0_headers
        domains = get_domains()
        # session = requests.session()
        # session = cfscrape.create_scraper()
        if not mail:
            mail = generate_nick(random.randint(6, 16), random.randint(2, 6)) + str(
                random.randint(0, 100)) + '@' + random.choice(
                domains)
        else:
            mail_domain = mail.split('@')[1]
            if mail_domain not in domains:
                raise Exception('Wrong domain')

        self.session = session
        self.mail = mail
        self.mail_key = hashlib.md5(mail.lower().encode()).hexdigest()
        self.messages = {}

    def get_messages(self):
        global burp0_headers
        attempts = 0
        messages = None
        for i in range(ERR_ATTEMPTS):
            req_url = "https://api4.temp-mail.org/request/mail/id/{}/format/json".format(self.mail_key)
            req = self.session.get(req_url)

            try:
                messages = req.json()
            except:
                continue

            if 'error' in messages:
                if messages['error'] == 'There are no emails yet':
                    messages = []
                else:
                    continue
            break

        if messages is None:
            raise TempMailException('Error while getting messages list 1')

        # print(req.text)
        msgs_objs = []
        for cur_msg in messages:
            if cur_msg['mail_id'] in self.messages:
                msg_obj = self.messages[cur_msg['mail_id']]
            else:
                msg_obj = Message(cur_msg, session)
                self.messages[cur_msg['mail_id']] = msg_obj

            msgs_objs.append(msg_obj)

        return msgs_objs


class Message:
    def __init__(self, data, session):
        self.id = data['mail_id']
        self.tittle = data['mail_subject']

        mail_from_raw = data['mail_from']
        mail_from = re.match('([^<]*) <([^>]*)>', mail_from_raw)
        self.sender_name = mail_from[1]
        self.sender_mail = mail_from[2]

        self.text = data['mail_html']
        self.session = session

    def get_text(self):
        global burp0_headers
        if self.text is not None:
            return self.text
        # attempts = 0
        # while 1:
        #     req = self.session.get('https://temp-mail.org/ru/view/' + self.id)
        #     resp = req.text
        # # print(resp)
        #     dat = re.match('.*?<div class="inbox-data-content-intro">(.*</div>)</div>.*', resp, re.DOTALL)
        #     try:
        #         text = dat[1]
        #         break
        #     except:
        #         print('vir_t')
        #         attempts+=1
        #         if attempts==err_attempts:
        #             raise TempMailException('Error while getting message text', resp)
        # self.text = text
        # return text

    def delete(self):
        global burp0_headers
        self.session.get('https://api4.temp-mail.org/request/delete/id/{}/format/json'.format(self.id))
        return 1


class TempMailException(Exception):
    pass
