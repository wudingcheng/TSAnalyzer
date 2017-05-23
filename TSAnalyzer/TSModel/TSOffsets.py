import json
from datetime import datetime, timedelta


def get_offsets(site, file='offsets.json'):
    with open(file, 'r') as f:
        offsets = json.loads(f.read())
    # print offsets
    return offsets.get(site, None)


def write_offsets(offset, file='offsets.json'):
    try:
        with open(file, 'r') as f:
            offsets = json.loads(f.read())
    except IOError:
        offsets = {}
    for key, item in offset.items():
        try:
            offsets[key].update(item)
        except KeyError:
            offsets[key] = item
    with open(file, 'w') as f:
        f.write(json.dumps(offsets, indent=4, sort_keys=False))


def offset_to_list(offset):
    if offset is None:
        return []
    offset_list = []
    for key, item in offset.items():
        for k, i in item.items():
            offset_list.append(' '.join([key, k, i]))
    return offset_list


def offset_to_fit(offset, component="north"):
    offsets = []
    psdecays = []
    for date, components in offset.items():
        date = datetime.strptime(date, '%Y%m%d')
        try:
            com = components[component]
        except KeyError:
            continue

        if com == 'eq' or com == 'ep':
            offsets.append(date)
        elif 'exp' in com:
            psdecays.append(
                [date, date + timedelta(days=int(com.split()[-1])), 0])
        elif 'log' in com:
            psdecays.append(
                [date, date + timedelta(days=int(com.split()[-1])), 1])
    return offsets, psdecays
