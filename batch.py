# 台鐵運行圖 Python 版
import sys
import os
import io
import time

# 自訂class與module
import diagram as dg
import svg_save
from progessbar import progress
import read_JSON_URL as motc_json_thsr

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main(argv_train_no):  # 程式執行段

    version = '0.9'
    txt_output = ''
    output_folder = os.getcwd() + '\OUTPUT\\'

    json_files = motc_json_thsr.read()

    print('台灣高鐵轉檔運行圖程式 - 版本：' + version + '\n')

    count = 0

    trains = dg.find_trains(json_files, argv_train_no)  # 特定車次的基本資料

    total = len(trains)

    today_date = time.strftime("%Y%m%d", time.localtime())
    make_time = time.asctime(time.localtime(time.time()))

    svg_output = svg_save.Draw(output_folder, today_date, 'LINE_THSR', version, 2000, make_time)

    for train_no in trains:  # 逐車次搜尋

        count += 1

        progress(count, total, '')

        train_id = train_no['DailyTrainInfo']['TrainNo']  # 車次號

        if train_id[0:1] == "0":
            train_id = train_id[1:4]


        car_class = train_no['DailyTrainInfo']['TrainNo'][0:2]  # 車種，由車次號轉換
        line_dir = train_no['DailyTrainInfo']['Direction']  # 南下0、北上1

        # print(train_no['DailyTrainInfo'])

        list_start_end_station = dg.find_train_stations(train_no)  # 查詢時刻表中，特定車次所有停靠車站

        # print(list_start_end_station)

        list_passing_stations = dg.find_stations(list_start_end_station, line_dir, line_dir)  # 查詢特定車次所有停靠與通過車站

        # print(list_passing_stations)

        train_time_space = dg.train_time_to_stations(list_start_end_station, list_passing_stations)  # 估算特定車次通過車站通過時間

        svg_output.draw_trains(train_time_space, train_id, car_class)

        svg_output.save()

    txt_output += '完成 ok \n'

    f = open('log.txt', 'w', encoding='utf-8')
    f.write(txt_output)
    f.close()


if __name__ == "__main__":
    argv_train_no = ''

    main(argv_train_no)
