import csv
import json
import math
from math import sin, cos, atan2, sqrt, degrees, radians, pi
import ast
from geopy import Point
from geopy.distance import distance
from decimal import Decimal
import sys
from tqdm import tqdm


hori_length = 0
veti_length = 0
SIZE_BLOCK = 200
boundBox = []
divide_map = [[list() for x in range(6)] for y in range(6)]


def read_boundary(f="上海.geojson"):
    """
    Load the polygon of Guangdong province
    """
    global hori_length
    global veti_length
    global boundBox

    j = json.load(open(f, "r", encoding='UTF-8'))

    boundBox = j["features"][0]["properties"]["boundingbox"]
    hori_length = distance_to_point((float(boundBox[2]), float(boundBox[0])), (float(boundBox[2]), float(boundBox[1])))
    veti_length = distance_to_point((float(boundBox[2]), float(boundBox[0])), (float(boundBox[3]), float(boundBox[0])))
    boundary = []
    type = j["features"][0]["geometry"]["type"]
    coordList = j["features"][0]["geometry"]["coordinates"]

    for record in coordList:
        coord = None
        if type == "MultiPolygon":
            coord = record[0]
        else:
            coord = record

        l = len(coord)
        for i in range(l - 1):
            boundary.append(to_webmercator(coord[i][0], coord[i][1]) + to_webmercator(coord[i + 1][0], coord[i + 1][1]))

    return boundary


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


def midpoint(a, b):
    a_lat, a_lon = radians(a[0]), radians(a[1])
    b_lat, b_lon = radians(b[0]), radians(b[1])
    delta_lon = b_lon - a_lon
    B_x = cos(b_lat) * cos(delta_lon)
    B_y = cos(b_lat) * sin(delta_lon)
    mid_lat = atan2(
        sin(a_lat) + sin(b_lat),
        sqrt(((cos(a_lat) + B_x) ** 2 + B_y ** 2))
    )
    mid_lon = a_lon + atan2(B_y, cos(a_lat) + B_x)
    # Normalise
    mid_lon = (mid_lon + 3 * pi) % (2 * pi) - pi
    return Point(latitude=degrees(mid_lat), longitude=degrees(mid_lon))


def to_webmercator(lng, lat):
    """
    geographic to web mercator
    """
    if abs(lng) > 180 or abs(lat) > 90:
        return

    num = lng * 0.017453292519943295
    x = 6378137.0 * num
    a = lat * 0.017453292519943295

    return [int(x), int(3189068.5 * math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a))))]


def divide_map():
    global SIZE_BLOCK
    global boundBox
    global divide_map

    num_block_hori = math.ceil(hori_length / SIZE_BLOCK)
    num_block_vert = math.ceil(veti_length / SIZE_BLOCK)

    offset_hori = (float(boundBox[3]) - float(boundBox[2])) / num_block_hori
    offset_vert = (float(boundBox[1]) - float(boundBox[0])) / num_block_vert
    startPoint = [float(boundBox[1]), float(boundBox[2])]

    divide_map = [[list() for longtitude in range(num_block_hori)] for latitude in range(num_block_vert)]
    with open('Shanghai_road.csv', 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        count = 0
        b = 0

        for row in reader:
            if int(row[2]) > 109 or int(row[2]) < 101:
                continue

            tmp_road_list_left = list()
            tmp_road_list_right = list()

            for index in range(5, len(row)):

                split = row[index].split(' ')
                coord = [float(split[1]), float(split[0])]
                tmp_road_list_left.append(coord)
                if index is not 5:
                    tmp_road_list_right.append(coord)

            zip_list = list(zip(tmp_road_list_left, tmp_road_list_right))
            for match in zip_list:
                mid_point = midpoint(match[0], match[1])
                road_obj = {'start_lat': match[0][0], 'start_lon': match[0][1], 'mid_lat': mid_point.latitude,
                            'mid_lon': mid_point.longitude, 'end_lat': match[1][0], 'end_lon': match[1][1], 'weight': 0}
                fir_index = math.ceil((startPoint[0] - road_obj['mid_lat']) / offset_vert)
                sec_index = math.ceil((road_obj['mid_lon'] - startPoint[1]) / offset_hori)
                if fir_index >= num_block_vert or sec_index >= num_block_hori:
                    count += 1
                    continue

                divide_map[fir_index][sec_index].append(road_obj)
                # print(str(road_obj))

        print(count)
        match_road(startPoint, offset_hori, offset_vert, num_block_hori, num_block_vert)


def match_road(startPoint, offset_hori, offset_vert, num_block_hori, num_block_vert):
    global divide_map

    with open('Shanghai_trip.csv', 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        count = 0
        num_out = 0
        num_none = 0
        for row in tqdm(reader):
            count += 1

            lat_index = math.ceil((startPoint[0] - float(row['lat'])) / offset_vert)
            lon_index = math.ceil((float(row['lon']) - startPoint[1]) / offset_hori)

            if lat_index >= num_block_vert or lat_index < 0 or lon_index >= num_block_hori or lon_index < 0:
                num_out += 1
                continue

            grid = divide_map[lat_index][lon_index]
            distance_list = list()

            if len(grid) is 0:
                # not test yet

                if lat_index - 1 > 0 and lon_index - 1 > 0:
                    # left-upward
                    grid = divide_map[lat_index - 1][lon_index - 1]
                    distance_cal(distance_list, grid, row)

                if lat_index - 1 > 0:
                    # upward
                    grid = divide_map[lat_index - 1][lon_index]
                    distance_cal(distance_list, grid, row)

                if lat_index - 1 > 0 and lon_index + 1 < num_block_hori:
                    # right-upward
                    grid = divide_map[lat_index - 1][lon_index + 1]
                    distance_cal(distance_list, grid, row)

                if lon_index + 1 < num_block_hori:
                    # right
                    grid = divide_map[lat_index][lon_index + 1]
                    distance_cal(distance_list, grid, row)

                if lat_index + 1 < num_block_vert and lon_index + 1 < num_block_hori:
                    # right-downward
                    grid = divide_map[lat_index + 1][lon_index + 1]
                    distance_cal(distance_list, grid, row)

                if lat_index + 1 < num_block_vert:
                    # downward
                    grid = divide_map[lat_index + 1][lon_index]
                    distance_cal(distance_list, grid, row)

                if lat_index + 1 < num_block_vert and lon_index - 1 > 0:
                    # left-downward
                    grid = divide_map[lat_index + 1][lon_index - 1]
                    distance_cal(distance_list, grid, row)

                if lon_index - 1 > 0:
                    grid = divide_map[lat_index][lon_index - 1]
                    distance_cal(distance_list, grid, row)

                if len(distance_list) is 0:
                    num_out += 1
                    continue
                else:
                    min(distance_list, key=lambda x: x[0])[1]['weight'] += 1

            else:
                distance_cal(distance_list, grid, row)
                min(distance_list, key=lambda x: x[0])[1]['weight'] += 1

        print(num_out)
        print(num_none)
        output_csv()


def distance_cal(distance_list, grid, row):
    for road in grid:
        distance_list.append(
            [int(distance_to_point([road['mid_lon'], road['mid_lat']], [float(row['lon']), float(row['lat'])])), road])


def output_csv():
    global divide_map

    with open('shanghai_road_weight.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['start_lat', 'start_lon', 'end_lat', 'end_lon', 'weight'])

        for lat_list in divide_map:
            for road_list in lat_list:
                for road in road_list:
                    writer.writerow(
                        [road['start_lat'], road['start_lon'], road['end_lat'], road['end_lon'], road['weight']])


read_boundary()
divide_map()
