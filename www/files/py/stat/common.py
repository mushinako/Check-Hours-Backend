LOG_DIR = '/home/mushinako/www/files/log/request/'
EXCEL_FN = LOG_DIR + 'stat.xlsx'

CHARS = ('\000', '\001', '\002', '\003', '\004', '\005', '\006', '\007', '\010',
         '\013', '\014', '\016', '\017', '\020', '\021', '\022', '\023', '\024',
         '\025', '\026', '\027', '\030', '\031', '\032', '\033', '\034', '\035',
         '\036', '\037')


def san_ill(s):
    for c in CHARS:
        s = s.replace(c, f'\\{(oct(ord(c))[2:]).zfill(3)}')
    return s
