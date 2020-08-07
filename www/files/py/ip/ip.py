#!/usr/bin/env python3
import os
import subprocess
from json import load, loads, dumps
from datetime import datetime
from requests import Session
from urllib.parse import quote_plus

from cs_nonce import gen_nonce, gen_auth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NOW = datetime.now()
HOME_DIR = '/home/mushinako/www/files/'
ROUTER_URL = 'http://192.168.1.251/cgi/json-req'
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
IP_FILE = HOME_DIR + 'key/ip.lock'
IP_LOG = HOME_DIR + f'log/ip/{NOW.strftime("%Y-%m-%d (%a)")}.log'
# GIT_URL = 'https://github.com/Mushinako/Check-Hours.git'
IP_JS_DIR = HOME_DIR + 'github/Check-Hours/'
IP_TXT = IP_JS_DIR + 'ip.txt'


def replace_ip(ip_d, ip):
    # Report new IP to GitHub
    os.chdir(IP_JS_DIR)
    with open(IP_TXT, 'w') as f:
        f.write(ip)
    subprocess.run(('git', 'pull'))
    subprocess.run(('git', 'add', '.'))
    subprocess.run(('git', 'commit', '-a', '-m', ip_d))
    subprocess.run(('git', 'push'))
    # Self-Log
    with open(IP_FILE, 'w') as f:
        f.write(ip)


def post_json(s, fn, url, id, sid='0', snonce=''):
    with open(os.path.join(CUR_DIR, fn), 'r') as f:
        req = load(f)
    cnonce = gen_nonce()
    req['request']['session-id'] = sid
    req['request']['cnonce'] = cnonce
    req['request']['auth-key'] = gen_auth(cnonce, id, snonce)
    return parse_post(s, url, req)


def parse_post(s, url, ddata):
    return loads(s.post(url, f'req={quote_plus(dumps(ddata))}', verify=False).content)


def side():
    s = Session()
    # POST 1 Login
    res1 = post_json(s, 'req1.json', ROUTER_URL, 0)
    params = res1['reply']['actions'][0]['callbacks'][0]['parameters']
    sid = params['id']
    snonce = params['nonce']
    # POST 2 GetIP
    res2 = post_json(s, 'req.json', ROUTER_URL, 1, sid, snonce)
    return (s, res1, res2)


def main():
    s = Session()
    # POST 1 Login
    res1 = post_json(s, 'req1.json', ROUTER_URL, 0)
    params = res1['reply']['actions'][0]['callbacks'][0]['parameters']
    try:
        sid = params['id']
    except KeyError:
        return (s, res1, None, None)
    snonce = params['nonce']
    # POST 2 GetIP
    res2 = post_json(s, 'req2.json', ROUTER_URL, 1, sid, snonce)
    ip = res2['reply']['actions'][0]['callbacks'][0]['parameters']['value']
    # POST 3 Logout
    res3 = post_json(s, 'req3.json', ROUTER_URL, 2, sid, snonce)
    # Sum up
    if os.path.isfile(IP_FILE):
        with open(IP_FILE, 'r') as f:
            ip_old = f.read()
    else:
        ip_old = 'None'
    if ip_old != ip and ip:
        time = NOW.strftime('%Y-%m-%d (%a) %H:%M:%S')
        ip_d = f'{ip_old} -> {ip}'
        with open(IP_LOG, 'a') as f:
            f.write(f'{time} {ip_d}\n')
        replace_ip(ip_d, ip)
    return (s, res1, res2, res3)


if __name__ == '__main__':
    main()
