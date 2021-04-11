import hashlib


# function witch returns INT value depending on the key and the size of the ring
def hash(key, size):  # size is a power of 2
    # encoding string by using encode() then sending to SHA1()
    result = hashlib.sha1(key.encode())

    m = size % 16  # module of 16
    d = size // 16  # division of 16

    if m == 0:
        return int(result.hexdigest()[-d:], 16) % size  # return the last d hex of the equivalent hexadecimal value.
    else:  # 2, 4, 8
        return int(result.hexdigest()[-1:], 16) % size  # return the last d hex of the equivalent hexadecimal value.
