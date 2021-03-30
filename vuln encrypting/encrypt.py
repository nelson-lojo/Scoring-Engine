from Cryptodome.Cipher import AES
import sys

print(len(sys.argv))
assert len(sys.argv) > 3, "args are as follows: encrypt <key> <vulnsFile> <pensFile>"
key = (sys.argv[1]).encode("utf-8")
vulnPath = sys.argv[2]
penPath = sys.argv[3]

if len(sys.argv) > 4:
    keyLen = int(sys.argv[4])
else:
    keyLen = 16

assert key != "", "Key cannot be an empty string"
assert keyLen in [16, 24, 32], "Key lengths have to be either 16, 24, 36"

key *= keyLen
key = key[:keyLen]

def showBytes(byts):
    return 'b\'\\x' + '\\x'.join([ byts.hex()[i:i+2] for i in range(0, len(byts.hex()), 2) ]) + '\''

# grab the binary of the vulns json file and put it in vulnJsonBin
vulnJson = open(vulnPath, "rb")
vulnJsonBin = vulnJson.read()
vulnJson.close()

# encrypt vulnJsonBin and put it in encryptedVulnBinary
encryptor = AES.new(key, AES.MODE_EAX)
vulnNonce = encryptor.nonce
encryptedVulnBinary, vulnTag = encryptor.encrypt_and_digest(vulnJsonBin)
del(encryptor, vulnJsonBin)

# put encryptedVulnBinary in file 'vulns' 
vulnBin = open ("vulns", "wb")
vulnBin.write(encryptedVulnBinary)
vulnBin.close()
del(encryptedVulnBinary)

# do it all again for the penalties
penJson = open(penPath, "rb")
penJsonBin = penJson.read()
penJson.close()

encryptor = AES.new(key, AES.MODE_EAX)
penNonce = encryptor.nonce
encryptedPenBinary, penTag = encryptor.encrypt_and_digest(penJsonBin)
del(penJsonBin)

penBin = open ("penalties", "wb")
penBin.write(encryptedPenBinary)
penBin.close()
del(encryptedPenBinary)


# now print the tags and nonces for later
print(f"""
vuln nonce: {showBytes(vulnNonce)}
vuln tag:   {showBytes(vulnTag)}
encrypted vuln file: `vulns`

penalty nonce: {showBytes(penNonce)}
penalty tag:   {showBytes(penTag)}
encrypted penalty file: `penalties`""")


