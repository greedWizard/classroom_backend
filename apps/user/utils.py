import hashlib


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()
