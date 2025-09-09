import sys
import random
from constants import CHARS_ARRAY


def generate_random_string(length):
    random_string = ''.join(random.choice(CHARS_ARRAY) for _ in range(length))
    return random_string


def error(text):
    sys.stderr.write(text + '\n')
    exit(1)
