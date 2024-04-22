import random
import string


class RandomStringTokenGenerator:
    def __init__(self, length=6):
        self.length = length

    def generate(self):
        return "".join([random.choice(string.digits) for _ in range(self.length)])
