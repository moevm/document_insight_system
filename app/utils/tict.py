def has(tict, key):
    for tuple_key in tict:
        if tuple_key[1] == key:
            return True
    return False


def get(tict, key):
    for tuple_key in tict:
        if tuple_key[1] == key:
            return tict[tuple_key]
    return None


def dictify(tict):
    dictionary = {}
    for tuple_key in tict:
        dictionary[tuple_key[1]] = tict[tuple_key]
    return dictionary
