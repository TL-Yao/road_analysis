# add_library('pdf')
import csv
import json
import math
import ast
from geopy import Point
from geopy.distance import distance

hori_length = 0
veti_length = 0
ratio = 0


def read_boundary(f="shanghai.geojson"):
    """
    Load the polygon of Guangdong province
    """

    j = json.load(open(f, "r"))

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

    return boundary, hori_length, veti_length


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


def read_mobility():
    """
    Read mobility patterns
    """
    lines = []
    with open("highway_mobility.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            s_lon, s_lat = to_webmercator(float(row[0]), float(row[1]))
            d_lon, d_lat = to_webmercator(float(row[2]), float(row[3]))
            lines.append([s_lon, s_lat, d_lon, d_lat])
    return lines


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


'''
def map(from_value,from_min, from_max, to_min, to_max):
    """
    Convert GPS coordinate into a new coordinate system
    """
    if from_value is None:
        return to_min
    from_value = float(from_value)
    to_len = to_max - to_min
    from_len = from_max - from_min
    ratio = (from_value - from_min)/from_len
    to_value = to_min + ratio * to_len
    return math.ceil(to_value)
'''


def setup():
    beginRecord(PDF, "shanghai_mobility.pdf");

    # size of generated figure

    boundary, hori_length, veti_length = read_boundary()
    # print(hori_length, veti_length)
    ratio = hori_length / veti_length
    # print(ratio)
    s = (hori_length, veti_length)
    h = int(hori_length / 100)
    v = int(veti_length / 100)
    print(h, v)
    size(h, v)
    background(0, 0, 0)

    max_lng = max(boundary, key=lambda x: x[0])[0]
    max_lat = max(boundary, key=lambda x: x[1])[1]
    min_lng = min(boundary, key=lambda x: x[0])[0]
    min_lat = min(boundary, key=lambda x: x[1])[1]

    stroke(0)
    strokeWeight(1)

    beginShape()
    for s_lng, s_lat, d_lng, d_lat in boundary:
        vertex(map(s_lng, min_lng, max_lng, 0, s[0]), s[1] - map(s_lat, min_lat, max_lat, 0, s[1]))
    fill(0, 0, 0)
    endShape(CLOSE)

    smooth(4)

    strokeWeight(0.01)

    with open("shanghai_road_weight.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            green = math.pow(int(row['weight']), 3)
            stroke(255, green, 51)
            startlnt, startlat = to_webmercator(float(row['start_lon']), float(row['start_lat']))
            endlnt, endlat = to_webmercator(float(row['end_lon']), float(row['end_lat']))
            line(map(startlnt, min_lng, max_lng, 0, s[0]), s[1] - map(startlat, min_lat, max_lat, 0, s[1]),
                 map(endlnt, min_lng, max_lng, 0, s[0]), s[1] - map(endlat, min_lat, max_lat, 0, s[1]))
    print("end")
    endRecord()
