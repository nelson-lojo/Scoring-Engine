import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes as urand
from sys import argv

assert len(argv) == 3, f"USAGE: python3 {argv[0]} <vulns file> <pens file>"
vulnF = argv[1]
pensF = argv[2]

def encrypt(data):
    cipher = AES.new(urand(16), AES.MODE_CBC)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return {
        'iv' : b64encode(cipher.iv).decode('utf-8'),
        'data' : b64encode(encrypted).decode('utf-8')
    }

with open(vulnF, 'rb') as v:
    vulns = encrypt(v.read())

with open('vulns', 'wb') as v:
    v.write(vulns['data'])

with open(penF, 'rb') as p:
    pens = encrypt(p.read())

with open('pens', 'wb') as p:
    p.write(pens['data'])

del encrypted

print(f"""
vulns iv: `{vulns['iv']}`
vulns file: `vulns`

pens iv: `{pens['iv']}`
pens file: `pens`
""")