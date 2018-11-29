add_library('pdf')
import csv
import json
import math
import ast


def read_boundary(f="guangdong.geojson"):
    """
    Load the polygon of Guangdong province
    """
    j = json.load(open(f, "r"))
    boundary = []
    coord = j["features"][0]["geometry"]["coordinates"][0]
    l = len(coord)
    for i in range(l - 1):
        boundary.append(to_webmercator(coord[i][0], coord[i][1]) + to_webmercator(coord[i + 1][0], coord[i + 1][1]))
    return boundary


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


def map(from_value, from_min, from_max, to_min, to_max):
    """
    Convert GPS coordinate into a new coordinate system
    """
    if from_value is None:
        return to_min
    from_value = float(from_value)
    to_len = to_max - to_min
    from_len = from_max - from_min
    ratio = (from_value - from_min) / from_len
    to_value = to_min + ratio * to_len
    return math.ceil(to_value)


def setup():
    beginRecord(PDF, "guangdong_mobility.pdf");

    # size of generated figure
    s = (796, 581)
    size(796, 581)
    background(255, 255, 255)

    boundary = read_boundary()

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

    stroke(255, 255, 255, 40)
    strokeWeight(1.5)

    with open("广州市道路数据.csv") as file:
        reader = csv.reader(file)
        head = next(reader)
        index = head.index('geometry')
        for row in reader:
            geo = row[index]

            if geo == "":
                continue

            geoPointList = ast.literal_eval(geo)
            geoStringList = zip(geoPointList[:-1], geoPointList[1:])

            for line in geoStringList:
                start = line[0]
                end = line[1]


        line(map(s_lng, min_lng, max_lng, 0, s[0]), s[1] - map(s_lat, min_lat, max_lat, 0, s[1]),
             map(d_lng, min_lng, max_lng, 0, s[0]), s[1] - map(d_lat, min_lat, max_lat, 0, s[1]))
    print("end")
    endRecord()