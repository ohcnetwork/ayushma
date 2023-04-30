import os
import binascii


class RandomStringTokenGenerator:
    def __init__(self, length=20):
        self.length = length

    def generate(self):
        return binascii.hexlify(os.urandom(self.length)).decode()
