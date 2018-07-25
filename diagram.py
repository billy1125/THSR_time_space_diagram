import json

import pandas as pd # 引用套件並縮寫為 pd
import numpy as np

#自訂class與module
import basic_data


#處理所有車站基本資訊(Stations.csv)
stations = basic_data.stations()

#時間轉換(Locate.csv)
time_loc = basic_data.time_loc()

#找出每一個車次
def find_trains(data, train_no):

    trains = []

    if train_no == '':
        for x in data: #逐車次搜尋
            trains.append(x)
    # elif train_no != '':
    #     for x in data['TrainInfos']: #逐車次搜尋
    #         if x['Train'] == train_no:
    #             trains.append(x)

    return trains

#找出每一個車次的表定經過車站
def find_train_stations(train_no):

    list_start_end_station = {}
    
    for station in train_no['StopTimes']:
        list_start_end_station[station['StationID']] = [station['ArrivalTime'], station['DepartureTime'], station['StationID'], station['StopSequence']]

    return list_start_end_station

    
#找出每一個車次所有會經過的車站，無論是否會停靠
def find_stations(list_start_end_station, line, line_dir):

    #起終點車站代碼
    end_station_number = len(list_start_end_station) - 1
    start_station = list(list_start_end_station)[0]
    end_station = list(list_start_end_station)[end_station_number]

    global stations

    temp = []
    station = start_station

    km = 0.0 #計算經過車站里程
        
    while True:

        temp.append([stations[station][0], stations[station][1], stations[station][3], km])
        # print(stations[station][1])
        if line_dir == 0:  #南下

            km += float(stations[station][10])
            station = stations[station][4]

        elif line_dir == 1:  #北上

            km += float(stations[station][11])
            station = stations[station][5]

        if station == end_station:
            temp.append([stations[station][0], stations[station][1], stations[station][3], km])
            break

        if len(temp) > 200:
            print(len(temp))
            break
            
    list_passing_stations = temp

    return list_passing_stations

#將所有經過車站找出，並且將通過車站的時間點估計出來
def train_time_to_stations(list_start_end_station, list_passing_stations):
    
    global time_loc

    station = []
    station_id = []
    time = []
    loc = []

    for item in list_passing_stations:

        station_id.append(item[0])
        station.append(item[1])
        loc.append(item[3])

        if list_start_end_station.__contains__(item[0]): #如果經過車站清單中包括停靠車站，則將出發時間再加入
            #list_passing_stations[index].append(int(list_station[item[0]].replace(':','')))
            ArrTime = int(time_loc[list_start_end_station[item[0]][0]])
            DepTime = int(time_loc[list_start_end_station[item[0]][1]])

            time.append(ArrTime)

            if ArrTime > DepTime: #車站內跨午夜處理，將跨午夜車站通過時間增加1440與0，之後在svg_save重複繪製兩次
                station_id.append('-1')
                station.append('跨午夜')
                loc.append(item[3])
                time.append(1440)

                station_id.append('-1')
                station.append('跨午夜')
                loc.append(item[3])
                time.append(0)

            if item[0] == 'End':
                station_id.append(list_passing_stations[0][0])
            else:
                station_id.append(item[0])
            station.append(item[1])
            loc.append(item[3])
            time.append(DepTime)
        else:
            #list_passing_stations[index].append(np.NaN)
            time.append(np.NaN)

    dict = {"Station": station, "Time": time, "Loc": loc, "Station ID": station_id}
    
    select_df = pd.DataFrame(dict)
    #select_df = select_df.sort_values(by = 'Loc')
    
    select_df = select_df.set_index('Loc').interpolate(method='index') #估計通過時間

    return select_df


#跨午夜車次處理，基本邏輯，非車站內跨午夜則必須估計出午夜十二點的位置
# def midnight_train(list_start_end_station, list_passing_stations, over_night_stn):
#
#     global time_loc
#
#     nidmight_km = 0
#
#     midnight_in_station = False
#
#     station = []
#     station_id = []
#     time = []
#     loc = []
#
#     i = 0
#
#     while True:
#         item = list_passing_stations[i]
#         if list_start_end_station.__contains__(item[0]):
#             ArrTime = int(time_loc[list_start_end_station[item[0]][0]])
#             DepTime = int(time_loc[list_start_end_station[item[0]][1]])
#
#             if item[0] == over_night_stn:
#
#                 if DepTime >= ArrTime: #插入一個跨午夜的虛擬車站，藉此估計列車所在的里程數
#                     station_id.append('-1')
#                     station.append('跨午夜')
#                     loc.append(np.NaN)
#                     time.append(1440)
#
#                     station_id.append(item[0])
#                     station.append(item[1])
#                     loc.append(float(item[3]))
#                     time.append(ArrTime + 1440) #要將跨午夜車站的時間加上1440估計較為適當
#
#                 elif DepTime < ArrTime: #車站內跨日則跳過處理，於train_time_to_stations函數進行處理即可
#                     midnight_in_station = True
#
#             else:
#                 station_id.append(item[0])
#                 station.append(item[1])
#                 loc.append(float(item[3]))
#                 time.append(ArrTime)
#
#                 station_id.append(item[0])
#                 station.append(item[1])
#                 loc.append(float(item[3]))
#                 time.append(DepTime)
#
#         i += 1
#         if item[0] == over_night_stn:
#             break
#
#     dict = {"Station": station, "Time": time, "Loc": loc, "Station ID": station_id}
#
#     select_df = pd.DataFrame(dict)
#     # print(select_df)
#     select_df = select_df.interpolate(method='index') #估計午夜通過里程
#
#     # print(select_df[select_df.loc[:,"Station ID"] == '-1'].iloc[0, 0])
#
#     if midnight_in_station == False: #如果跨午夜車次不是在車站內跨夜，才將資料帶出
#         nidmight_km = select_df[select_df.loc[:,"Station ID"] == '-1'].iloc[0, 0]
#
#     return nidmight_km