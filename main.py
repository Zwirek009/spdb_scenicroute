import osmnx as ox
from shapely.geometry import box
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import random

class ARoute:
    def __init__(self, nodes = [], length = 0, edges = []):
        self._nodes = nodes
        self._length = length
        self._edges = edges

    def nodes(self):
        return self._nodes

    def length(self):
        return self._length

    def edges(self):
        return self._edges

    def end_node(self):
        if len(self._nodes) == 0:
            return -1
        return self._nodes[len(self._nodes) - 1]

    def start_node(self):
        if len(self._nodes) == 0:
            return -1
        return self._nodes[0]

    def add(self, other): #unsafe!
        if len(self._nodes) == 0:
            self._nodes = self._nodes + other.nodes()
        else:
            self._nodes = self._nodes + other.nodes()[1:]
        self._length = self._length + other.length()
        self._edges = self._edges + other.edges()


def find_nearest_node(graph, latitude, longtitude):
    point = (latitude, longtitude)
    return point, ox.get_nearest_node(graph, point, method='euclidean')

def create_route(graph, start_lat, start_lon, end_lat, end_lon):
    _, start_node = find_nearest_node(graph, start_lat, start_lon)
    _, end_node = find_nearest_node(graph, end_lat, end_lon)
    return nx.shortest_path(G=graph, source=start_node, target=end_node, weight='length')

def create_a_route(graph, start_lat, start_lon, end_lat, end_lon):
    nodes = create_route(graph, start_lat, start_lon, end_lat, end_lon)
    if len(nodes) > 1:
        length = nx.shortest_path_length(G=graph, source=nodes[0], target=nodes[len(nodes)-1], weight='length')
        edges = get_edges_of_nodes_path(nodes)
        return ARoute(nodes, length, edges)
    return None

def create_scenic_routes(graph, nodes_proj):
    scenic_routes = []
    scenic_routes.append(create_a_route(
        graph,
        float((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2),
        float((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2),
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) + 0.01),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) + 0.01)
    ))
    scenic_routes.append(create_a_route(
        graph,
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) - 0.02),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) - 0.02),
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) - 0.02),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) + 0.02)
    ))
    scenic_routes.append(create_a_route(
        graph,
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) + 0.03),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) - 0.01),
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) + 0.02),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) + 0.05)
    ))
    scenic_routes.append(create_a_route(
        graph,
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) - 0.005),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) - 0.05),
        float(((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2) - 0.1),
        float(((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2) + 0.01)
    ))
    return scenic_routes


#TODO something do not work, to be debugged
def get_common_routes_distance(single_route, route_set, graph):
    common_distance = 0
    for route_from_set in route_set:
        start_common_node = -1
        end_common_node = -1
        for node in single_route:
            if (start_common_node == -1) and (node in route_from_set):
                start_common_node = node
            if (start_common_node != -1) and (node in route_from_set):
                end_common_node = node
            if (start_common_node != -1) and (node not in route_from_set) and start_common_node != end_common_node:
                common_distance += nx.shortest_path_length(G=graph, source=start_common_node, target=end_common_node, weight='length')
                start_common_node = -1
                end_common_node = -1
        for node in reversed(single_route):
            if (start_common_node == -1) and (node in route_from_set):
                start_common_node = node
            if (start_common_node != -1) and (node in route_from_set):
                end_common_node = node
            if (start_common_node != -1) and (node not in route_from_set) and start_common_node != end_common_node:
                common_distance += nx.shortest_path_length(G=graph, source=start_common_node, target=end_common_node, weight='length')
                start_common_node = -1
                end_common_node = -1

def choose_direction(graph, start_scenic_node, end_node, scenic_routes):
    routes_with_node = []
    for s_route in scenic_routes:
        if start_scenic_node in s_route.nodes():
            routes_with_node.append(s_route)

    closest_to_end_node_length = None
    closest_to_end_edge = None
    closest_to_end_route = None
    full_route = None

    for r in routes_with_node:
        for (nodeA, nodeB) in r.edges():
            if nodeA == start_scenic_node:
                new_length = nx.shortest_path_length(graph, nodeB, end_node, weight='length')
                if closest_to_end_node_length == None:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r
                elif closest_to_end_node_length > new_length:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r
            elif nodeB == start_scenic_node:
                new_length = nx.shortest_path_length(graph, nodeA, end_node, weight='length')
                if closest_to_end_node_length == None:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r
                elif closest_to_end_node_length > new_length:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r

    edges_of_closest_route = r.edges()
    start_index = edges_of_closest_route.index(closest_to_end_edge)

    if closest_to_end_edge[0] == start_scenic_node:
        new_nodes = [a for (a,b) in edges_of_closest_route[start_index:]]
        new_nodes.append(edges_of_closest_route[-1][1])
        new_edges = [a for a in edges_of_closest_route[start_index:]]
        new_length = nx.shortest_path(graph, new_nodes[0], new_nodes[-1])
    else:
        new_nodes = [a for (a,b) in edges_of_closest_route[:start_index+1]]
        new_nodes.append(edges_of_closest_route[start_index][1])
        new_edges = [a for a in edges_of_closest_route[:start_index+1]]
        new_length = nx.shortest_path(graph, new_nodes[0], new_nodes[-1])

    chosen_route = ARoute(new_nodes, new_length, new_edges)

    return chosen_route, r

def slice_route_for_shortest_paths(graph, s_route):
    paths = []
    for (nodeA, nodeB) in s_route.edges():
        new_edges = [(nodeA, nodeB)]
        new_nodes = [nodeA, nodeB]
        new_length = nx.shortest_path_length(graph, nodeA, nodeB, 'length')
        paths.append(ARoute(new_nodes, new_length, new_edges))
    return paths

def check_node_in_other_scenic_route(other_routes, node_to_remove):
    for r in other_routes:
        if node_to_remove in r.nodes():
            return True
    return False

def build_a_route_with_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length):
    #scenic_edges = flatmap_2d_list_to_1d_list([x.edges() for x in scenic_routes])
    scenic_nodes = flatmap_2d_list_to_1d_list([x.nodes() for x in scenic_routes])
    actual_node = start_node
    scenic_nodes_remaining = scenic_nodes
    #scenic_edges_remaining = scenic_edges

    route_length = 0
    expected_route_length = nx.shortest_path(graph, start_node, end_node)
    scenic_route_length = 0
    route_so_far = ARoute()

    while (scenic_route_length < minimum_scenic_length and len(scenic_nodes_remaining) > 1):
        new_route_fragment = get_route_to_closest_node(graph, actual_node, scenic_nodes_remaining) # dojście do odcinka

        # przejście odcinkiem
        new_scenic_fragment = ARoute()
        s_route_part, s_route_full = choose_direction(graph, new_route_fragment.end_node(), end_node, scenic_routes) # fragment odcinka widokowego, idący bardziej w kierunku punktu końcowego

        try:
            expected_route_length = route_length + new_route_fragment.length() + nx.shortest_path_length(graph, new_route_fragment.end_node(), end_node, weight='length')

            if expected_route_length >= maximum_length:
                scenic_routes.remove(s_route_full)
                for to_remove in s_route_full.nodes():
                    check_node_in_other_scenic_route(scenic_routes, to_remove)
                    scenic_nodes_remaining.remove(to_remove)
                break
            s_route_sliced = slice_route_for_shortest_paths(graph, s_route_part)
            for s_route_small in s_route_sliced:
                expected_route_length = route_length + new_route_fragment.length() + new_scenic_fragment.length() + s_route_small.length() + nx.shortest_path_length(
                        graph, s_route_small.end_node(), end_node, weight = 'length')
                if expected_route_length >= maximum_length:
                    break
                new_scenic_fragment.add(s_route_small)
                if scenic_route_length + new_scenic_fragment.length() >= minimum_scenic_length:
                    break

            if new_scenic_fragment.length() > 0: #dodaj do trasy
                route_so_far.add(new_route_fragment)
                route_so_far.add(new_scenic_fragment)
                actual_node = route_so_far.end_node()
                for to_remove in new_scenic_fragment.nodes():
                    scenic_nodes_remaining.remove(to_remove)
                route_length = route_so_far.length()
                scenic_route_length = scenic_route_length + new_scenic_fragment.length()
                continue
            else:
                scenic_routes.remove(s_route_full)
                for to_remove in s_route_full.nodes():
                    scenic_nodes_remaining.remove(to_remove)

        except nx.NetworkXNoPath:
            if s_route_full in scenic_routes:
                scenic_routes.remove(s_route_full)
                for to_remove in s_route_full.nodes():
                    scenic_nodes_remaining.remove(to_remove)
            print('No path')
            continue

    last_nodes = nx.shortest_path(graph, actual_node, end_node)
    last_edges = get_edges_of_nodes_path(last_nodes)
    last_length = nx.shortest_path_length(graph, actual_node, end_node)
    route_so_far.add(ARoute(last_nodes, last_length, last_edges))

    return route_so_far

def flatmap_2d_list_to_1d_list(list_2d):
    list_1d = []
    for l in list_2d:
        list_1d = list_1d + l
    return list_1d

def get_edges_of_nodes_path(path):
    nodeA = None
    nodeB = None
    new_edges = []
    for node in path:
        if nodeB == None:  # pierwszy lub drugi node
            if nodeA == None:
                nodeA = node  # pierwszy node
            else:
                nodeB = node  # drugi node
                new_edges.append((nodeA, nodeB))
        else:
            nodeA = nodeB
            nodeB = node
            new_edges.append((nodeA, nodeB))
    return new_edges

def get_route_to_closest_node(graph, actual_node, all_nodes): #bierze na razie dowolny z all_nodes
    route_to_closest_node = None
    for other_node in all_nodes:
        if other_node == actual_node:
            continue
        if route_to_closest_node == None:
            route_nodes = nx.shortest_path(graph, actual_node, other_node)
            route_to_closest_node = ARoute(route_nodes, nx.shortest_path_length(graph, actual_node, other_node, weight='length'), get_edges_of_nodes_path(route_nodes))
        elif route_to_closest_node.length() > nx.shortest_path_length(graph, actual_node, other_node, weight='length'):
            route_to_closest_node = ARoute(nx.shortest_path(graph, actual_node, other_node),
                   nx.shortest_path_length(graph, actual_node, other_node, weight='length'))

    return route_to_closest_node

def main():

    print('Welcome to ScenicRoute app!')
    print('\nLoading srodmiescie.gpickle routes graph...')
    graph = nx.read_gpickle("places/srodmiescie.gpickle")
    graph_proj = ox.project_graph(graph)
    nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
    scenic_routes = create_scenic_routes(graph, nodes_proj)
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
    #route_scenic_distance = get_common_routes_distance(route, scenic_routes, graph)
    print('DONE')

    print('Shortest route length:\t' + str(route_length) + ' meters')
    #print('Shortest route scenic distance:\t' + str(route_scenic_distance) + ' meters')

    scenic_routes_nodes_lists = [s.nodes() for s in scenic_routes]

    if input('\nShow route on map? [y/n]\t') == 'y':
        print('Close map to continue...')
        fig, ax = ox.plot_graph_route(graph, route, show=False, close=False)
        ax.scatter(start_lon, start_lat, c='g', marker='x')
        ax.scatter(end_lon, end_lat, c='b', marker='x')
        fig_sc, ax_sc = ox.plot_graph_routes(graph, scenic_routes_nodes_lists, route_color='y', show=False, close=False)
        ax_sc.scatter(start_lon, start_lat, c='g', marker='x')
        ax_sc.scatter(end_lon, end_lat, c='b', marker='x')
        plt.show()

    print('\nScenic routes preference:')
    if input('Use default? [y/n]\t') == 'n':
        max_extra_dist = float(input('Type max extra distance [m]:\t'))
        min_scenic_dist = float(input('Type min scenic distance [m]:\t'))
    else:
        max_extra_dist = float(2000)
        min_scenic_dist = float(500)
    print('DONE')

    print("\nGood bye!")

def main2():
    print('Welcome to ScenicRoute app!')
    print('\nLoading srodmiescie.gpickle routes graph...')
    graph = nx.read_gpickle("places/srodmiescie.gpickle")
    graph_proj = ox.project_graph(graph)
    nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
    scenic_routes = create_scenic_routes(graph, nodes_proj)
    print('DONE')


    start_lon = float((nodes_proj['lon'].min() + nodes_proj['lon'].max()) / 2)
    start_lat = float((nodes_proj['lat'].min() + nodes_proj['lat'].max()) / 2)
    end_lon = float(nodes_proj['lon'].max())
    end_lat = float(nodes_proj['lat'].max())

    print('\nFinding shortest route...')
    start_point, start_node = find_nearest_node(graph, start_lat, start_lon)
    end_point, end_node = find_nearest_node(graph, end_lat, end_lon)
    route = nx.shortest_path(G=graph, source=start_node, target=end_node, weight='length')
    route_length = nx.shortest_path_length(G=graph, source=start_node, target=end_node, weight='length')
    print(route_length)

    print('DONE')

    the_route = build_a_route_with_scenic_routes(graph, start_node, end_node, scenic_routes, 500, 10000)

    scenic_routes_nodes_lists = [s.nodes() for s in scenic_routes]
    #32627804
    #32529959

    print('Close map to continue...')
    fig, ax = ox.plot_graph_route(graph, route, show=False, close=False)
    fig_best, ax_best = ox.plot_graph_route(graph, the_route.nodes(), show=False, close=False)
    #ax.scatter(start_lon, start_lat, c='g', marker='x')
    #ax.scatter(end_lon, end_lat, c='b', marker='x')
    #ax.scatter(graph._node[32627804]['x'], graph._node[32627804]['y'], c='b', marker='x')
    #ax.scatter(graph._node[32529959]['x'], graph._node[32529959]['y'], c='b', marker='x')
    fig_sc, ax_sc = ox.plot_graph_routes(graph, scenic_routes_nodes_lists, route_color='y', show=False, close=False)
    ax_sc.scatter(start_lon, start_lat, c='g', marker='x')
    ax_sc.scatter(end_lon, end_lat, c='b', marker='x')
    plt.show()

if __name__ == "__main__":
    #main()
    main2()
