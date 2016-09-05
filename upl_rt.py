#!/usr/bin/python
# -*- coding= utf-8 -*-

import requests
import re
import time
import random
import sys

from lib.upload_lib import *
from lib.single import *
import logging as log

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=log.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

basedir = os.path.dirname(__file__)

log.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s',
                level = log.DEBUG, filename = os.path.join(basedir,  upload_log_file))

stderr_logger = log.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, log.ERROR)
sys.stderr = sl

name = "redtube"

def get_videos():
    data = os.walk(os.path.join(basedir,  videos_folder))
    for root,  dirs,  files in data:
        return files
        
def get_user():
    with open(os.path.join(basedir,  upload_accounts_folder,  'pornhub.txt'),  'r') as files:
        users = files.read().split('\n')
        
    users_list = []
    for user in users:
        if len(user) > 1:
            users_list.append(user)
            
    if len(users_list) > 0:
        return users_list
    else:
        return None

def get_proxy():
    try:
        with open(os.path.join(basedir,  upload_accounts_folder,  'proxy.txt'),  'r') as files:
            proxies = files.read().split('\n')
    except:
        return None

    proxies_list = []
    for proxy in proxies:
        if len(proxy) > 1:
            proxies_list.append(proxy)
            
    if len(proxies_list) > 0:
        return proxies_list
    else:
        return None

def generete_block(length):
        a = ''
        for _ in range(length):
            a += random.choice('0123456789ABCDEF')

        return a

def get_csrf():
        data = []

        data.append(generete_block(8))
        data.append(generete_block(4))
        data.append(generete_block(4))
        data.append(generete_block(4))
        data.append(generete_block(12))
        return '-'.join(data)
        
def create_session(login, password, proxy):
    s = requests.Session()

    p_data = proxy.split(':')

    proxy = 'http://%s:%s@%s:%s/' % (p_data[2], p_data[3], p_data[0], p_data[1])
    s.proxies = {'http':  proxy,
                    'https': proxy}
    
    log.info("{}: try to login into account {}:{}".format(name,  login,  password))

    try:
        resp = s.get('http://www.redtube.com/phlogin')
    except:
        log.info("{}: proxy {} dead".format(name,  proxy))
        return False

    login_key = re.findall('id="login_key" value="(.+?)"', resp.text)[0]

    login_hash = re.findall('id="login_hash" value="(.+?)"', resp.text)[0]
    redirect = re.findall('name="redirect" value="(.+?)"', resp.text)[0]

    data = {
    'forceLogin': '1',
    'login_key': login_key,
    'login_hash': login_hash,
    'redirect': redirect,
    'authorized': '1',
    'username': login,
    'password': password
    }

    url = 'http://www.pornhub.com/user/login_json'
    resp = s.post(url, data)

    log.debug("{}: {}".format(name, resp.text))

    if resp.json()['success'] == 1:
        resp = s.get('http://www.pornhub.com%s' % resp.json()['redirect'])
        log.info("{}: login success".format(name))

        return s
    else:
        return 'Bad acc'


def get_file_data(filename):
    with open(os.path.join(basedir,  videos_folder,  filename), 'rb') as files:
        filedata = files.read()

    return filedata
    
def upload_video(filename):
    log.info("{}: try to upload {}".format(name, filename ))
    url = 'http://www.redtube.com/upload'

    resp = s.get(url)

    upload_session = re.findall('upload_session=(.+?)"', resp.text)[0]


    url = 'http://www.redtube.com/upload/file?upload_session=%s' % upload_session

    cookies = []
    cookies_dict = s.cookies.get_dict()
    for cook in cookies_dict:
        cookies.append('%s=%s' % (cook, cookies_dict[cook]))

    cookies_line = '; '.join(cookies)

    s.headers['Content-Type'] = 'multipart/form-data; boundary=----------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7'
    s.headers['User-Agent'] = 'Shockwave Flash'
    s.headers['Connection'] = 'Keep-Alive'
    s.headers['Host'] = 'www.redtube.com'
    s.headers['Accept'] = 'text/*'
    s.headers['Pragma'] = 'no-cache'

    dct = {}
    dct['createtime'] = str(time.time()).replace('.', '') + '2'

    dct['filename'] = filename
    dct['title'] = make_title(dct['filename'])
    dct['video_data'] = get_file_data(dct['filename'] )
    dct['filesize'] = len(dct['video_data'])
    dct['cookie_line'] = cookies_line
    dct['multipowuploadid'] = get_csrf()
    dct['fileid'] = get_csrf()
    dct['tags'] = make_tags(dct['title'], tags)

    dct['modificatetime'] = str(time.time()).replace('.', '') + '5'

    log.info("{}: title: {}".format(name, dct['title']))
    log.info("{}: tags: {}".format(name, dct['tags']))

    data = '''------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="Filename"

{filename}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="MultiPowUpload_browserCookie"

{cookie_line}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="filesCount"

1
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="fileCreationdate"

{createtime}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="fileModificationDate"

{modificatetime}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="type"

1
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="title"

{title}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="tags"

{tags}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="currentFileIndex"

0
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="MultiPowUploadId"

{multipowuploadid}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="fileSize"

{filesize}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="fileId"

{fileid}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="Filedata"; filename="{filename}"
Content-Type: application/octet-stream

{video_data}
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7
Content-Disposition: form-data; name="Upload"

Submit Query
------------cH2GI3cH2Ef1Ef1Ij5KM7gL6ae0KM7'''.format(**dct)

    resp = s.post(url , data)

    log.debug("{}: {}".format(name, resp.text))
    if '"success":true' in resp.text:
        log.info("{}: upload success".format(name))

    
def delete_user_from_file(all_users,  current_user):
    all_users.remove(current_user)
    with open(os.path.join(basedir,  upload_accounts_folder,  'pornhub.txt'),  'w') as files:
        files.write('\n'.join(all_users))

def delete_proxy_from_file(all_proxies,  current_proxy):
    all_proxies.remove(current_proxy)
    with open(os.path.join(basedir,  upload_accounts_folder,  'proxy.txt'),  'w') as files:
        files.write('\n'.join(all_proxies))
        
def delete_video_from_folder(filename):
    os.remove(os.path.join(basedir,  videos_folder,  filename))
    

def main():
    log.info("{}: start script".format(name))
    videos = get_videos()
    if len(videos) <5:
        log.error("{}: no video for uploading, upload skipped".format(name))
        exit()

    global users
    global user
        
    users= get_user()
    if not users:
        log.error("{}: no accounts to login, upload skipped".format(name))
        exit()
    
    user = users[0]
    log.debug("{}: {}".format(name, user))

    proxies = get_proxy()
    if not proxies:
        log.error("{}: no proxy, upload skipped".format(name))
        exit()

    proxy = random.choice(proxies)
    
    login = user.split(':')[0]
    password  = user.split(':')[1]
    
    global s
    s = create_session(login,  password, proxy)
    
    if not s:
        delete_proxy_from_file(proxies, proxy)
        exit()
    elif s == 'Bad acc':
        delete_user_from_file(users,  user)
        log.error("{}: Wrong account. {}".format(name, user))
        exit()
        
    for _ in range(upload_packet):
        video = videos.pop(0)
        log.debug("{}: upload video {}".format(name, video))

        upload_video(video)
        delete_video_from_folder(video)
        time.sleep(upload_packet_timeout)
        
    delete_user_from_file(users,  user)
    log.info("{}: stop script".format(name))


if __name__ == "__main__":
    soo_lonely = SingleInstance() 
    main()
 # защита от запуска второй копии скрипта
    

 #Берем аккаунт из lib.data.accounts.pornhub.txt
 #смотрим есть ли ролики в upload/pornhub
 #если роликов нет - просто завершаем скрипт

 #если роликов 5 и больше - запускаем заливку.
 #в каждый аккаунт грузим пять роликов.
 #title, tags, description - формируются в upload_lib.py
 #после заливки аккаунт удаляется из pornhub.txt
 
 #**заливка осуществляется через прокси.
 #я на впс подниму прокси.
 #*** скрипт будет работать по крону - поэтому basedir не забыть )




