def remove_keys(keys, ls):
    new_ls = []

    for item in ls:
        if type(item) is not dict:
            continue

        for key in keys:
            item.pop(key, None)

        new_ls.append(item)

    return new_ls
