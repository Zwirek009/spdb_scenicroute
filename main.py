import osmnx as ox
from shapely.geometry import box
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

def find_nearest_node(graph, latitude, longtitude):
    point = (latitude, longtitude)
    return point, ox.get_nearest_node(graph, point, method='euclidean')

def main():
    print('Welcome to ScenicRoute app!')
    print('\nLoading srodmiescie.gpickle routes graph...')
    graph = nx.read_gpickle("places/srodmiescie.gpickle")
    graph_proj = ox.project_graph(graph)
    nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
    print('DONE')

    print('\nAvailable longtitudes:\t' + str(nodes_proj['lon'].min()) + '-' + str(nodes_proj['lon'].max()))
    print('Available latitudes:\t' + str(nodes_proj['lat'].min()) + '-' + str(nodes_proj['lat'].max()))

    if input('\nUse default lat and lon? [y/n]\t') == 'n':
        print('\nSpecify desired start and end points:')
        start_lon = float(input('Type start longtitude:\t'))
        start_lat = float(input('Type start latitude:\t'))
        end_lon = float(input('Type end longtitude:\t'))
        end_lat = float(input('Type end latitude:\t'))
    else:
        start_lon = float((nodes_proj['lon'].min()+nodes_proj['lon'].max())/2)
        start_lat = float((nodes_proj['lat'].min()+nodes_proj['lat'].max())/2)
        end_lon = float(nodes_proj['lon'].max())
        end_lat = float(nodes_proj['lat'].max())
    print('DONE')

    print('\nFinding shortest route...')
    start_point, start_node = find_nearest_node(graph, start_lat, start_lon)
    end_point, end_node = find_nearest_node(graph, end_lat, end_lon)

    route = nx.shortest_path(G=graph, source=start_node, target=end_node, weight='length')
    route_length = nx.shortest_path_length(G=graph, source=start_node, target=end_node, weight='length')
    print('DONE')

    print('\nShortest route length:\t' + str(route_length) + ' meters')
    if input('\nShow route on map? [y/n]\t') == 'y':
        print('Close map to end the program...')
        ox.plot_graph_route(graph, route)

    print("\nGood bye!")

if __name__ == "__main__":
    main()
