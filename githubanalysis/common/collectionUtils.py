def uniquify(seq):
    keys = {}
    for e in seq:
        keys[e] = 1
    return list(keys.keys())


def sum_in_dict(sumDict, summandDict):
    for key in list(summandDict.keys()):
        try:
            sumDict[key] += summandDict[key]
        except KeyError:
            pass
    return sumDict


def get_value_robust(dict, key, default):
    try:
        return dict[key]
    except KeyError:
        return default


def safely_append_to_array_in_dict(dic: dict, key: str, item):
    if key in dic.keys():
        dic[key].append(item)
    else:
        dic.update({key: [item]})

def safely_extend_array_in_dict(dic: dict, key: str, list):
    if key in dic.keys():
        dic[key].extend(list)
    else:
        dic.update({key: list})
