import re


def validate_password(pwd):
    p1 = re.compile('[a-z]')
    p2 = re.compile('[A-Z]')
    p3 = re.compile('[0-9]')
    if len(pwd) not in range(6, 21):
        return False
    for p in [p1, p2, p3]:
        result = p.findall(pwd)
        if len(result) < 1:
            return False
    return True


def validate_username(name):
    print(len(name))
    if len(name) in range(1, 21):
        return True
    return False
