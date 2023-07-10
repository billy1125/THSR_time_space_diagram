import json
# from collections import namedtuple

# 讀取台鐵JSON
def read_json(filename):
    with open('JSON/' + filename, 'r', encoding='utf8') as data_file:
        data = json.load(data_file)

    return data


# 找出每一個車次
def find_trains(data, select_trains):
    trains = []

    if len(select_trains) == 0:
        for x in data:  # 逐車次搜尋
            trains.append(x)
    elif len(select_trains) > 0:
        for x in data['TrainTimetables']:  # 逐車次搜尋
            if x['Train'] in select_trains:
                trains.append(x)

    return trains
