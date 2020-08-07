#!/usr/bin/env python3
import secrets
from math import ceil

CHR_SZ = 8
HEX_CASE = False


class JSArr(list):
    def __getitem__(self, key):
        try:
            val = super().__getitem__(key)
        except IndexError:
            return 0
        return 0 if val is None else val

    def __setitem__(self, key, val):
        if key < 0:
            try:
                super().__setitem__(key, val)
            except IndexError:
                print('Negative index out of range. Nothing changed')
            finally:
                return
        length = super().__len__()
        if key < length:
            super().__setitem__(key, val)
            return
        for _ in range(length, key):
            self.append(None)
        self.append(val)

    def __delitem__(self, key):
        super().__delitem__(key)
        while super().__getitem__(-1) is None:
            super().__delitem__(-1)


def gen_nonce():
    return int(secrets.token_hex(4), 16)


def gen_auth(client_nonce, req_i, server_nonce):
    return hmd5(f'{get_ha1(server_nonce)}:{req_i}:{client_nonce}:JSON:'
                '/cgi/json-req')


def get_ha1(server_nonce):
    return hmd5(f'admin:{server_nonce}:a795119ad9789940d8c1038fb60eb732')


def hmd5(s):
    return numarr2hex(core_md5(str2asciiarr(s), len(s)))


def str2asciiarr(s):
    bin = [0] * ceil(len(s) / 4)
    mask = (1 << CHR_SZ) - 1
    for i in range(0, len(s) * CHR_SZ, CHR_SZ):
        bin[i >> 5] |= (ord(s[i // CHR_SZ]) & mask) << (i % 32)
    return bin


def numarr2hex(arr):
    s = ''
    for num in arr:
        h = hex(num & 0xffffffff)[2:]
        h = '0' * (8 - len(h)) + h
        s += ''.join([h[i:i+2] for i in range(6, -1, -2)])
    return s


def core_md5(num_arr, tot_sz):
    num_arr = JSArr(num_arr)
    tot_chr_sz = tot_sz * CHR_SZ
    num_arr[tot_chr_sz >> 5] |= 128 << (tot_chr_sz % 32)
    num_arr[(((tot_chr_sz + 64) >> 9) << 4) + 14] = tot_chr_sz
    num1 = 1732584193
    num2 = -271733879
    num3 = -1732584194
    num4 = 271733878
    for i in range(0, len(num_arr), 16):
        a = num1
        b = num2
        c = num3
        d = num4
        num1 = md5_1(num3, num4, num1, num_arr[i + 0], -680876936, num2, 7)
        num4 = md5_1(num2, num3, num4, num_arr[i + 1], -389564586, num1, 12)
        num3 = md5_1(num1, num2, num3, num_arr[i + 2], 606105819, num4, 17)
        num2 = md5_1(num4, num1, num2, num_arr[i + 3], -1044525330, num3, 22)
        num1 = md5_1(num3, num4, num1, num_arr[i + 4], -176418897, num2, 7)
        num4 = md5_1(num2, num3, num4, num_arr[i + 5], 1200080426, num1, 12)
        num3 = md5_1(num1, num2, num3, num_arr[i + 6], -1473231341, num4, 17)
        num2 = md5_1(num4, num1, num2, num_arr[i + 7], -45705983, num3, 22)
        num1 = md5_1(num3, num4, num1, num_arr[i + 8], 1770035416, num2, 7)
        num4 = md5_1(num2, num3, num4, num_arr[i + 9], -1958414417, num1, 12)
        num3 = md5_1(num1, num2, num3, num_arr[i + 10], -42063, num4, 17)
        num2 = md5_1(num4, num1, num2, num_arr[i + 11], -1990404162, num3, 22)
        num1 = md5_1(num3, num4, num1, num_arr[i + 12], 1804603682, num2, 7)
        num4 = md5_1(num2, num3, num4, num_arr[i + 13], -40341101, num1, 12)
        num3 = md5_1(num1, num2, num3, num_arr[i + 14], -1502002290, num4, 17)
        num2 = md5_1(num4, num1, num2, num_arr[i + 15], 1236535329, num3, 22)
        num1 = md5_2(num3, num4, num1, num_arr[i + 1], -165796510, num2, 5)
        num4 = md5_2(num2, num3, num4, num_arr[i + 6], -1069501632, num1, 9)
        num3 = md5_2(num1, num2, num3, num_arr[i + 11], 643717713, num4, 14)
        num2 = md5_2(num4, num1, num2, num_arr[i + 0], -373897302, num3, 20)
        num1 = md5_2(num3, num4, num1, num_arr[i + 5], -701558691, num2, 5)
        num4 = md5_2(num2, num3, num4, num_arr[i + 10], 38016083, num1, 9)
        num3 = md5_2(num1, num2, num3, num_arr[i + 15], -660478335, num4, 14)
        num2 = md5_2(num4, num1, num2, num_arr[i + 4], -405537848, num3, 20)
        num1 = md5_2(num3, num4, num1, num_arr[i + 9], 568446438, num2, 5)
        num4 = md5_2(num2, num3, num4, num_arr[i + 14], -1019803690, num1, 9)
        num3 = md5_2(num1, num2, num3, num_arr[i + 3], -187363961, num4, 14)
        num2 = md5_2(num4, num1, num2, num_arr[i + 8], 1163531501, num3, 20)
        num1 = md5_2(num3, num4, num1, num_arr[i + 13], -1444681467, num2, 5)
        num4 = md5_2(num2, num3, num4, num_arr[i + 2], -51403784, num1, 9)
        num3 = md5_2(num1, num2, num3, num_arr[i + 7], 1735328473, num4, 14)
        num2 = md5_2(num4, num1, num2, num_arr[i + 12], -1926607734, num3, 20)
        num1 = md5_3(num3, num4, num1, num_arr[i + 5], -378558, num2, 4)
        num4 = md5_3(num2, num3, num4, num_arr[i + 8], -2022574463, num1, 11)
        num3 = md5_3(num1, num2, num3, num_arr[i + 11], 1839030562, num4, 16)
        num2 = md5_3(num4, num1, num2, num_arr[i + 14], -35309556, num3, 23)
        num1 = md5_3(num3, num4, num1, num_arr[i + 1], -1530992060, num2, 4)
        num4 = md5_3(num2, num3, num4, num_arr[i + 4], 1272893353, num1, 11)
        num3 = md5_3(num1, num2, num3, num_arr[i + 7], -155497632, num4, 16)
        num2 = md5_3(num4, num1, num2, num_arr[i + 10], -1094730640, num3, 23)
        num1 = md5_3(num3, num4, num1, num_arr[i + 13], 681279174, num2, 4)
        num4 = md5_3(num2, num3, num4, num_arr[i + 0], -358537222, num1, 11)
        num3 = md5_3(num1, num2, num3, num_arr[i + 3], -722521979, num4, 16)
        num2 = md5_3(num4, num1, num2, num_arr[i + 6], 76029189, num3, 23)
        num1 = md5_3(num3, num4, num1, num_arr[i + 9], -640364487, num2, 4)
        num4 = md5_3(num2, num3, num4, num_arr[i + 12], -421815835, num1, 11)
        num3 = md5_3(num1, num2, num3, num_arr[i + 15], 530742520, num4, 16)
        num2 = md5_3(num4, num1, num2, num_arr[i + 2], -995338651, num3, 23)
        num1 = md5_4(num3, num4, num1, num_arr[i + 0], -198630844, num2, 6)
        num4 = md5_4(num2, num3, num4, num_arr[i + 7], 1126891415, num1, 10)
        num3 = md5_4(num1, num2, num3, num_arr[i + 14], -1416354905, num4, 15)
        num2 = md5_4(num4, num1, num2, num_arr[i + 5], -57434055, num3, 21)
        num1 = md5_4(num3, num4, num1, num_arr[i + 12], 1700485571, num2, 6)
        num4 = md5_4(num2, num3, num4, num_arr[i + 3], -1894986606, num1, 10)
        num3 = md5_4(num1, num2, num3, num_arr[i + 10], -1051523, num4, 15)
        num2 = md5_4(num4, num1, num2, num_arr[i + 1], -2054922799, num3, 21)
        num1 = md5_4(num3, num4, num1, num_arr[i + 8], 1873313359, num2, 6)
        num4 = md5_4(num2, num3, num4, num_arr[i + 15], -30611744, num1, 10)
        num3 = md5_4(num1, num2, num3, num_arr[i + 6], -1560198380, num4, 15)
        num2 = md5_4(num4, num1, num2, num_arr[i + 13], 1309151649, num3, 21)
        num1 = md5_4(num3, num4, num1, num_arr[i + 4], -145523070, num2, 6)
        num4 = md5_4(num2, num3, num4, num_arr[i + 11], -1120210379, num1, 10)
        num3 = md5_4(num1, num2, num3, num_arr[i + 2], 718787259, num4, 15)
        num2 = md5_4(num4, num1, num2, num_arr[i + 9], -343485551, num3, 21)
        num1 = add_sign_32(num1, a)
        num2 = add_sign_32(num2, b)
        num3 = add_sign_32(num3, c)
        num4 = add_sign_32(num4, d)
    return (num1, num2, num3, num4)


def md5_1(m1, m2, n2, n3, n4, m, roll):
    return md5_common((m & m1) | ((~m) & m2), n2, n3, n4, m, roll)


def md5_2(m1, m2, n2, n3, n4, m, roll):
    return md5_common((m & m2) | (m1 & (~m2)), n2, n3, n4, m, roll)


def md5_3(m1, m2, n2, n3, n4, m, roll):
    return md5_common(m ^ m1 ^ m2, n2, n3, n4, m, roll)


def md5_4(m1, m2, n2, n3, n4, m, roll):
    return md5_common(m1 ^ (m | (~m2)), n2, n3, n4, m, roll)


def md5_common(n1, n2, n3, n4, m, roll):
    return add_sign_32(bit_rol(add_sign_32(n1, n2, n3, n4), roll), m)


def bit_rol(n, num_bits):
    safe_n = safe_sign_32(n)
    bin_n = bin(safe_n & 0xffffffff)[2:]
    bin_n = '0' * (32 - len(bin_n)) + bin_n
    bin_r = bin_n[num_bits:] + bin_n[:num_bits]
    return safe_sign_32(int(bin_r, 2))


def add_sign_32(*arr):
    return safe_sign_32(sum(arr))


def safe_sign_32(n):
    return (n + 2 ** 31) % 2 ** 32 - 2 ** 31
