from Crypto.Cipher import AES
from hashlib import md5
import binascii
import base64

def pad(data):
	length = 16 - (len(data) % 16)
	data += chr(length)*length
	return data	

def encrypt(plainText,workingKey):
	iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
	plainText = pad(plainText)
	#encDigest = md5.new ()
	encDigest = md5()
	encDigest.update(workingKey)
	enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv.encode("utf8"))
	#encryptedText = enc_cipher.encrypt(plainText).encode('hex')
	encryptedText = enc_cipher.encrypt(plainText.encode("utf8"))
	encryptedText = binascii.hexlify(encryptedText)
	return encryptedText

def decrypt(cipherText,workingKey):
	iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
	#decDigest = md5.new ()
	decDigest = md5()
	decDigest.update(workingKey)
	#encryptedText = cipherText.decode('hex') #hex is no longer available in python3
	encryptedText = binascii.unhexlify(cipherText)
	#dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
	dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv.encode("utf8"))
	decryptedText = dec_cipher.decrypt(encryptedText)
	return decryptedText.decode('utf-8')