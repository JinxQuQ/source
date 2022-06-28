def replace(key, obj, replace_value):
    if isinstance(obj,dict):
        if key in obj:
            obj[key] = replace_value
        else:
            for k,v in obj.items():
                replace(key,v,replace_value)
    elif isinstance(obj, list):
        for l in obj:
            replace(key,l,replace_value)


if __name__ == '__main__':
    map = {'getBalance': [{'abc': 1233}], 'abc': {"name": {"test": 123}}}
    print(map)
    replace('test', map, '345tr')
    print(map)
