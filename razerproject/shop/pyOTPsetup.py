import pyotp
def getKeyReturnOtp(key):
    totp = pyotp.TOTP(key)
    return totp.now()
