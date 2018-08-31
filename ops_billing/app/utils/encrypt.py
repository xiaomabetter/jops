from Crypto.Cipher import ChaCha20
from binascii import b2a_hex,a2b_hex
import hashlib

class ChaEncrypt(object):
    def __init__(self, key):
        self.key = key

    def encrypt(self, text):
        cryptor = ChaCha20.new(key=self.key)
        ciphertext = b2a_hex(cryptor.nonce + cryptor.encrypt(text))
        return ciphertext

    def decrypt(self, text):
        text = a2b_hex(text)
        nonce = text[:8]
        ciphertext = text[8:]
        cipher = ChaCha20.new(key=self.key, nonce=nonce)
        return cipher.decrypt(ciphertext)

def encryption_md5(text):
    m = hashlib.md5()
    m.update(text.encode("utf8"))
    return m.hexdigest()