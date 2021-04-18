#!/usr/bin/python3
from base64 import b64decode
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from sys import argv

assert len(argv) == 4, f"USAGE: python3 {argv[0]} <filename> <b64 key> <b64 iv>"

def decrypt(data, key, iv):
    return unpad((AES.new(b64decode(key), AES.MODE_CBC, b64decode(iv))).decrypt(data), AES.block_size)

with open(argv[1], 'rb') as fil:
    print(
        decrypt(
            fil.read(),
            argv[2],
            argv[3]
        ).decode('ascii')
    )

