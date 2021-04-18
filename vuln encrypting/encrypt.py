#!/usr/bin/python3
from base64 import b64encode
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes as urand
from sys import argv

assert len(argv) == 3, f"USAGE: python3 {argv[0]} <vulns file> <pens file>"
vulnF = argv[1]
pensF = argv[2]

def encrypt(data, key=urand(16)):
    cipher = AES.new(key, AES.MODE_CBC)
    return {
        'key' : b64encode(key).decode('utf-8'),
        'iv'  : b64encode(cipher.iv).decode('utf-8'),
        'data' : cipher.encrypt(pad(data, AES.block_size))
    }

with open(vulnF, 'rb') as v:
    vulns = encrypt(v.read())
    with open('vulns', 'wb') as v:
        v.write(vulns['data'])

with open(pensF, 'rb') as p:
    pens = encrypt(p.read())
    with open('pens', 'wb') as p:
        p.write(pens['data'])

print(f"""
vulns key: `{vulns['key']}`
vulns iv: `{vulns['iv']}`
vulns file: `vulns`

pens key: `{pens['key']}`
pens iv: `{pens['iv']}`
pens file: `pens`
""")