from Cryptodome.Cipher import AES


def encrypt(key, vulns, pens, length=2, vulnOut="vulns", penOut="penalties"):
    assert key != "", "Key cannot be an empty string"
    assert length*8 in [16, 24, 32], "Key lengths have to be either 2, 3, 4"

    key *= length*8
    key = key[:length*8]

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
    vulnBin = open (vulnOut, "wb")
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

    penBin = open (penOut, "wb")
    penBin.write(encryptedPenBinary)
    penBin.close()
    del(encryptedPenBinary)

    return vulnNonce, vulnTag, vulnOut, penNonce, penTag, penOut


if __name__=='__main__':
    import sys

    def showBytes(byts):
        return 'b\'\\x' + '\\x'.join([ byts.hex()[i:i+2] for i in range(0, len(byts.hex()), 2) ]) + '\''
    
    print(len(sys.argv))
    assert len(sys.argv) > 3, "args are as follows: encrypt <key> <vulnsFile> <pensFile>"
    key = (sys.argv[1]).encode("utf-8")
    vulnPath = sys.argv[2]
    penPath = sys.argv[3]

    if len(sys.argv) > 4:
        keyLen = int(sys.argv[4])
    else:
        keyLen = 16

    vn, vt, vp, pn, pt, pp = encrypt(key, vulnPath, penPath, length=(keyLen // 8))

    # now print the tags and nonces for later
    print(f"""
    vuln nonce: {showBytes(vn)}
    vuln tag:   {showBytes(vt)}
    encrypted vuln file: `{vp}`

    penalty nonce: {showBytes(pn)}
    penalty tag:   {showBytes(pt)}
    encrypted penalty file: `{pp}`""")







