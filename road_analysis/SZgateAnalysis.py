from math import sin, cos, atan2, sqrt, degrees, radians, pi
import csv
import sys
from geopy import Point
from geopy.distance import distance
import numpy as np
from datetime import datetime

gates = []
cars = []
distri = [[[] for i in range(24)] for i in range(79)]

def distance_to_point(p1, p2):
    """
    Calculate distance from point to point
    :param p1:
    :param p2:
    :return: meters
    """
    a = Point(latitude=p1[1], longitude=p1[0])
    b = Point(latitude=p2[1], longitude=p2[0])
    return distance(a, b).m

def read_gates():
    '''
        read gates information from csv file
    :return:
    '''
    path = 'C:\\Users\\apdem\\Downloads\\sz_stations.csv'
    with open(path) as file:
        global gates
        file_data = csv.DictReader(file)
        #print(str([row for row in file_data]))
        for data in file_data:
            gates.append(data)

def index_nearest_gate(data):
    car_lng = data.get('lon')
    car_lat = data.get('lat')
    distan_list = []
    for gate in gates:
        gate_lng = gate.get('lng')
        gate_lat = gate.get('lat')
        distan_list.append(distance_to_point((car_lng, car_lat), (gate_lng, gate_lat))) \

    return distan_list.index(min(distan_list))

def index_time_range(data):
    str_time = data.get('time')
    hour = int(str_time[9])
    if str_time[10] != ':':
        hour = hour * 10 + int(str_time[10])

    return hour

def distribute_to_gates():
    global cars
    path = 'C:\\Users\\apdem\\Downloads\\Shenzhen_trip_sample.csv'
    with open(path) as file:
        car_data = csv.DictReader(file)

        for data in car_data:
            data['nearestGate'] = index_nearest_gate(data)
            data['timeIndex'] = index_time_range(data)
            distri[data.get('nearestGate')][data.get('timeIndex')].append(data)
            cars.append(data)

def statistic_calc(list, type):
    '''
    :param list: a list of car data to be calculated.
    :param type: string: average or median or standard
    :return:
    '''
    speed_list = []
    result = 0
    for carData in list:
        speed_list.append(int(carData.get('speed')))

    if type == 'average':
        result = np.mean(speed_list)
    elif type == 'median':
        result = np.median(speed_list)
    elif type == 'standard':
        result = np.std(speed_list)

    return result

def write_to_csv(id, gateDistri, writer):
    '''
    :param id: gate id
    :param gateDistri: car data near the gate after distribution
    :param writer: file writer
    :return: none
    '''
    gate_name = gates[id].get('id')
    average_list = [gate_name, 'avg']
    median_list = [gate_name, 'median']
    car_in_range_list = []
    range_average_list = [gate_name, 'avg_in_range']

    for timeDistri in gateDistri:
        if len(timeDistri) == 0:
            average_list.append(0)
            median_list.append(0)
            range_average_list.append(0)
            continue
        else:
            average = statistic_calc(timeDistri, 'average')
            average_list.append(average)

            median = statistic_calc(timeDistri, 'median')
            median_list.append(median)

            standard = statistic_calc(timeDistri, 'standard')
            ceiling = median + standard * 3
            floor = median - standard * 3

            #选取median ± 3个标准差的数据
            for data in timeDistri:
                speed = int(data.get('speed'))

                if floor <= speed <= ceiling:
                    car_in_range_list.append(data)

            avg_in_range = statistic_calc(car_in_range_list, 'average')
            range_average_list.append(avg_in_range)

    writer.writerows([average_list, median_list, range_average_list])



read_gates()
distribute_to_gates()

with open("sz_csv.csv", 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ['station', 'type'] + [str(i) for i in range(0, 24)])
    gate_id = 0

    for gateDistri in distri:
        write_to_csv(gate_id, gateDistri, writer)
        gate_id += 1