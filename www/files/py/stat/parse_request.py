#!/usr/bin/env python3
import os
import re
from datetime import datetime as dt

import pytz
import phpserialize as ser
from openpyxl import load_workbook

from common import LOG_DIR, EXCEL_FN, san_ill

TIME = re.compile(
    r'(?P<yr>\d{4})-(?P<mo>\d{2})-(?P<day>\d{2}) '
    r'(?P<hr>\d{2})\.(?P<mn>\d{2})\.(?P<sec>\d{2})\.(?P<us>\d{6})\.log')


class Req:
    def __init__(self, time, req, res):
        self._time = {k: int(v) for k, v in time.items()}
        self._req = req
        self._res = res

    @property
    def time(self):
        t = self._time
        return dt(
            t['yr'], t['mo'], t['day'], t['hr'], t['mn'], t['sec'],
            t['us'], tzinfo=pytz.timezone('US/Pacific'))

    @property
    def fname(self):
        d = self._req
        return san_ill(d[b'fname'].decode('utf-8')) if b'fname' in d else ''

    @property
    def lname(self):
        d = self._req
        return san_ill(d[b'lname'].decode('utf-8')) if b'lname' in d else ''

    @property
    def idn(self):
        d = self._req
        return san_ill(d[b'id'].decode('utf-8')) if b'id' in d else ''

    @property
    def fell(self):
        d = self._res
        return f"{float(d[b'fell']):.2f}" if d is not None else ''

    @property
    def lead(self):
        d = self._res
        return f"{float(d[b'lead']):.2f}" if d is not None else ''

    @property
    def serv(self):
        d = self._res
        return f"{float(d[b'serv']):.2f}" if d is not None else ''

    @property
    def notes(self):
        d = self._req
        return san_ill(', '.join(
            [f"{k.decode('utf-8')}: \"{v.decode('utf-8')}\""
             for k, v in d.items() if k not in (b'fname', b'lname', b'id')]))


def main():
    stats = []
    for fn in sorted(os.listdir(LOG_DIR)):
        re_fn = TIME.fullmatch(fn)
        if re_fn is None:
            continue
        fp = LOG_DIR + fn
        with open(fp, 'rb') as f:
            raw_data = [x for x in f.read().split(b'\n') if x]
        os.remove(fp)
        req_b = ser.loads(raw_data[0])
        res_b = ser.loads(raw_data[1]) if len(raw_data) == 2 else None
        stats.append(Req(re_fn.groupdict(), req_b, res_b))
    if not stats:
        return []
    wb = load_workbook(filename=EXCEL_FN)
    ws = wb.active
    ws.title = 'Stats'
    for s in stats:
        ws.append((s.time, s.idn, s.fname, s.lname,
                   s.fell, s.lead, s.serv, s.notes))
    wb.save(filename=EXCEL_FN)
    return (stats, wb)


if __name__ == '__main__':
    s = main()
