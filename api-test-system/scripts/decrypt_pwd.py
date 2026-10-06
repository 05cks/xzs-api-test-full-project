# -*- coding: utf-8 -*-
"""校验 xzs 用户密码：用私钥解密库中密文，还原明文，用于自动化登录。"""
import base64
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

PRIVATE_KEY = (
    "MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAKXDDGEkrBK0Oe7t"
    "zTIJGTBNbZUq4tbDJW0ULpnH1th0XWrCpI/boKQPBoXoYdrIi+/1vwEeUBpAfhIs"
    "g/OKvTrbLM26Sqyma2FTDiA8mFvHUBCtZGhAlK/f/VKT61bIlEddKIJklnfbXosO"
    "G3HjYtDQci0M/xT0Eu2zED7ksRnNAgMBAAECgYEAlCuz5yn2volnt9HNuEo1v92W"
    "dN5vAnZSAB0oQsJFpBrwXjw7CXTTNZNQy2YcAot9uzO6Vu+Xvr+jce9ky9BasM7e"
    "hz0gnwJWAO79IqUnmu3RRq7HllDwp72qysXIypJZCF4HX5jAzUGlNzlTSUb1H4Lt"
    "avKc6a//YqPfQ0jTLsECQQDZuGKGAYq6rBCX0+T8qlQpCPc41wsl4Gi9lLD21ks9"
    "PMx44JdhsUrqLWItZiGynDzq1LJ3M1hr3gbSsPQcI9HJAkEAwugDFCiRLOqOBRRG"
    "lYbzgGdmXbR4SrMNIpcFTFhU+MsEqaMueVPiNtRSIK6W8pS28ZN0aiZDTBAT84fO"
    "IENp5QJBAJaVgQ9OYbVa7N8WH3riE/ONz+/wTDWWUNtOzFbtQHzKYGH6dLmM9lOh"
    "sBXWXdg7V6bUFdt8F9wDZJS07yHHZIECQG4rHrJiS80Lt8L/NvaGFVVbHO2SePwg"
    "QShwHLqOo1kNyFDqv/YsiA1d7h4zEXeEv/PE2WS2xAtWezCIbualtFECQQDPUkYh"
    "s3vZoZgsltdeFnv/WoXaXNRIzunMTmksIlh8JP7C1xQHrwdCpUkffgSVphxGJGHk"
    "xooMpki7oTC1Mdjx"
)


def decrypt(cipher_b64):
    key = RSA.import_key(base64.b64decode(PRIVATE_KEY))
    cipher = PKCS1_v1_5.new(key)
    sentinel = b"__FAIL__"
    plain = cipher.decrypt(base64.b64decode(cipher_b64), sentinel)
    if plain == sentinel:
        return None
    return plain.decode("utf-8")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(arg, "=>", decrypt(arg))
