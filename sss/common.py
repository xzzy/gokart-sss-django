import hashlib
import re
import base64


typename_re = re.compile("typenames?=\s*(?P<name>[a-zA-Z0-9_\-\:\%]+)\s*",re.DOTALL)
def typename(url):
    m = typename_re.search(url.lower())
    return m.group('name').replace("%3a",":") if m else None


def get_md5(data):

    m = hashlib.md5()
    m.update(str(data).encode('utf-8'))
    data = base64.urlsafe_b64encode(m.digest())

    data = data.decode()
    if data[-3:] == "===":
        return data[0:-3]
    elif data[-2:] == "==":
        return data[0:-2]
    elif data[-1:] == "=":
        return data[0:-1]
    else:
        return data