from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from passlib.hash import argon2

PASSWORD_MIN_LEN = 12


def encrypt_note(content, password):
    pwhash = argon2.hash(password)
    key = bytes(pwhash[-16:], 'ascii')
    iv = bytes(pwhash[31:47], 'ascii')
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(bytes(content, 'utf-8'), AES.block_size))
    return pwhash, ciphertext


def decrypt_note(ciphertext, pwhash):
    key = bytes(pwhash[-16:], 'ascii')
    iv = bytes(pwhash[31:47], 'ascii')
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    content = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return content.decode('utf-8')


def check_note_password(password, pwhash):
    return argon2.verify(password, pwhash)
