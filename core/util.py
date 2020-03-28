import yaml

def chunks(lst, n):
    arr = []
    for i in lst:
        arr.append(i)
        if len(arr)==n:
            yield arr
            arr = []
    if arr:
        yield arr

def read_yml_all(fl):
    with open(fl, 'r') as f:
        return yaml.load_all(f, Loader=yaml.FullLoader)
