#!/usr/bin/env python3
import re
import os
import string
import random
import requests
from datetime import datetime
from subprocess import call

URL = CENSORED
EXT = 'xlsm'

NOW = datetime.now()
HOME_DIR = '/home/mushinako/www/files/'
XLSX_DIR = HOME_DIR + 'xlsx/'
RAND_LEN = 32
LOCK_DIR = HOME_DIR + 'key/'
LOCK = LOCK_DIR + 'down.lock'
UPD_TIME = LOCK_DIR + 'time.lock'
FP = LOCK_DIR + 'fp.lock'
DOWN_LOG = HOME_DIR + f'log/down/{NOW.strftime(r"%Y-%m-%d (%a)")}.log'
# EMAIL = 'ridoedee@gmail.com'


def random_string():
    cand = string.digits + string.ascii_letters
    return ''.join([random.choice(cand) for _ in range(RAND_LEN)])


def main():
    with open(LOCK, 'w') as f:
        f.write('1')
    file_url = requests.get(URL).content
    file_get_url = re.search(
        br'\"FileGetUrl\":\"(https://[A-Za-z0-9/_\-=\\\.\?]+)\",',
        file_url
        )[1]
    dl_url = file_get_url.replace(b'\\u0026', b'&')
    file = requests.get(dl_url).content
    new_len = len(file)
    old_len = 0
    if os.path.isfile(FP):
        with open(FP, 'r') as f:
            fp = f.read()
        if os.path.isfile(fp):
            with open(fp, 'rb') as f:
                old_len = len(f.read())
            os.remove(fp)
    act_xlsx = XLSX_DIR + random_string() + '.' + EXT
    tmp_xlsx = XLSX_DIR + random_string() + '.' + EXT
    with open(tmp_xlsx, 'wb') as f:
        f.write(file)
    os.replace(tmp_xlsx, act_xlsx)
    with open(FP, 'w') as f:
        f.write(act_xlsx)
    with open(LOCK, 'w') as f:
        f.write('0')
    d = NOW.strftime('%Y-%m-%d (%a) %H:%M')
    with open(UPD_TIME, 'w') as f:
        f.write(d)
    with open(DOWN_LOG, 'a') as f:
        f.write(f'{d} {old_len} -> {new_len} ({new_len-old_len})\n')


if __name__ == '__main__':
    main()
