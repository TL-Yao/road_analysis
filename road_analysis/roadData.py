import osmnx as ox
import pandas as pd
import networkx as nx
import matplotlib.cm as cm
import numpy as np
import csv

cities = [
          ##"成都市,中国",
          ##"广州市,中国",
          ##"深圳市,中国",
          #"重庆市,中国",
          "北京市,中国"
          ##"昆明市,中国",
          ##"贵阳市,中国",
          #"天津市,中国",
          #"上海市,中国",
          #"沈阳市,中国",
          ##"盐城市,中国",
          #"南宁市,中国",
          ##"太原市,中国",
          #"杭州市,中国",
          #"武汉市,中国",
          #"哈尔滨市,中国",
          ##"济南市,中国",
          #"合肥市,中国",
          #"赤峰市,中国",
          #"郑州市,中国",
          #"西安市,中国",
          ##"南京市,中国",
          #"长沙市,中国",
          #"潍坊市,中国",
          #"烟台市,中国",
          #"大连市,中国",
          ############"长春市,中国"
          ##"宜昌市,中国",
          #################"青岛市,中国",输出有奇怪字符
          ##"石家庄市,中国",
          #"兰州市,中国"
          #################"乌鲁木齐市,中国",输出有奇怪字符
          ##"台州市,中国",#台州实际变成了泰州
          ##"苏州市,中国",
          ##"临沂市,中国",
          ##"保定市,中国"
            ]

class Row:

        def __init__ (self):
            self.edge_Id =""
            self.edge_Name = ""
            self.start_Node_ID = ""
            self.start_Node_GPS = ""
            self.end_Node_ID = ""
            self.end_Node_GPS = ""
            self.length = ""
            self.highway_type = ""
            self.geometry = ""

        def output_Csv(self):
            result = str(self.edge_Id) + ',' + str(self.edge_Name) + ',' + str(self.start_Node_ID) + ',' + str(self.start_Node_GPS) + ',' \
                     + str(self.end_Node_ID) + ',' + str(self.end_Node_GPS) + ',' + str(self.length) + ',' + str(self.highway_type) + ',' + str(self.geometry)
            return result

def road_data_CSV(name):
    cityname = name[:3] + "道路数据.csv"
    with open(cityname, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Edge_Id', 'Edge_Name', 'Start_Node_ID', 'Start_Node_GPS', 'End_Node_ID', 'End_Node_GPS', 'Length', 'Highway_type', 'geometry'])
        dictLen = 0
        G = ox.graph_from_place(name, network_type='drive',infrastructure = 'way["highway"~"motorway|motorway_link|motorway_junction|trunk|trunk_link|primary|primary_link|secondary|tertiary"]', which_result = 2)
        #infrastructure = 'way["highway"~"motorway|motorway_link|motorway_junction|trunk|trunk_link|primary|primary_link"]'
        #ox.plot_graph(G)
        edges = G.edges()

        for edge in edges:
            turple = Row()

            turple.start_Node_ID = edge[0]
            turple.end_Node_ID = edge[1]
            info = G[edge[0]][edge[1]]
            turple.start_Node_GPS = find_GPS(G, turple.start_Node_ID)
            turple.end_Node_GPS = find_GPS(G, turple.end_Node_ID)
            #print(info)

            if dictLen == 0:
                dictLen = len(info)
            getInfo(turple, dictLen - 1, info)
            dictLen -= 1
            #print(turple.edge_Name)
            writer.writerow([turple.edge_Id, turple.edge_Name, turple.start_Node_ID, turple.start_Node_GPS, turple.end_Node_ID,
                             turple.end_Node_GPS, turple.length, turple.highway_type, turple.geometry])

def getInfo(turple, num, info):
    if 'osmid' in info.get(num):
        turple.edge_Id = str(info.get(num).get('osmid'))

    if 'name' in info.get(num):
        name = str(info.get(num).get('name'))

        if '(' in name:
            name[:name.find('(')]

        turple.edge_Name = name

    if 'length' in info.get(num):
        turple.length = str(info.get(num).get('length'))

    if 'highway' in info.get(num):
        turple.highway_type = str(info.get(num).get('highway'))

    if 'geometry' in info.get(num):
        turple.geometry = str(list(info.get(num).get('geometry').wkt))
        print(str(list(info.get(num).get('geometry').wkt)))

def find_GPS(G, ID):
    info = G.node[ID]
    result = str(info['x']) + ', ' + str(info['y'])
    return result

def test():
    G = ox.graph_from_place("北京市,中国", network_type='drive',
                            infrastructure='way["highway"~"motorway|motorway_link|motorway_junction|trunk|trunk_link|primary|primary_link"]',which_result = 2)

    edges = G.edges()

    for edge in edges:
        info = G[edge[0]][edge[1]]
        if 'geometry' in info:
            print(str(list(info.get('geometry').coords)))


for city in cities:
    road_data_CSV(city)

