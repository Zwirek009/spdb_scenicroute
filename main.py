import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
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

    def add(self, other):
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
        edges = get_edges_of_nodes_path(nodes)
        length = sum([nx.shortest_path_length(graph, x, y, weight = 'length') for (x, y) in edges])
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


def choose_direction(graph, start_scenic_node, end_node, scenic_routes):
    routes_with_node = []
    for s_route in scenic_routes:
        if start_scenic_node in s_route.nodes():
            routes_with_node.append(s_route)

    closest_to_end_node_length = None
    closest_to_end_edge = None
    full_route = None

    for r in routes_with_node:
        for (nodeA, nodeB) in r.edges():
            if nodeA == start_scenic_node:
                new_length = nx.shortest_path_length(graph, nodeB, end_node, weight='length')
                if closest_to_end_node_length is None:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r
                elif closest_to_end_node_length > new_length:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r
            elif nodeB == start_scenic_node:
                new_length = nx.shortest_path_length(graph, nodeA, end_node, weight='length')
                if closest_to_end_node_length is None:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r
                elif closest_to_end_node_length > new_length:
                    closest_to_end_node_length = new_length
                    closest_to_end_edge = (nodeA, nodeB)
                    full_route = r

    edges_of_closest_route = full_route.edges()
    start_index = edges_of_closest_route.index(closest_to_end_edge)

    if closest_to_end_edge[0] == start_scenic_node:
        new_nodes = [a for (a,b) in edges_of_closest_route[start_index:]]
        new_nodes.append(edges_of_closest_route[-1][1])
        new_edges = [a for a in edges_of_closest_route[start_index:]]
        new_length = sum ([nx.shortest_path_length(graph, x, y, weight = 'length') for (x, y) in new_edges])
    else:
        new_nodes = [a for (a,b) in edges_of_closest_route[:start_index+1]]
        new_nodes.append(edges_of_closest_route[start_index][1])
        new_nodes.reverse()
        new_edges = get_edges_of_nodes_path(new_nodes)
        new_length = sum ([nx.shortest_path_length(graph, x, y, weight = 'length') for (x, y) in new_edges])

    chosen_route = ARoute(new_nodes, new_length, new_edges)

    return chosen_route, full_route


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


def build_a_route_with_closest_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length):

    actual_node = start_node
    scenic_routes_remaining = scenic_routes[:]
    route_length = 0
    scenic_route_length = 0
    route_so_far = ARoute()
    scenic_routes_visited = []

    while (scenic_route_length < minimum_scenic_length and len(scenic_routes_remaining) > 0):
    #while len(scenic_routes_remaining) > 0:
        scenic_nodes = [x.start_node() for x in scenic_routes_remaining] #+ [x.end_node() for x in scenic_routes_remaining]
        new_route_fragment = get_route_to_closest_node(graph, actual_node, scenic_nodes) # dojście do odcinka


        new_scenic_fragment = ARoute()
        s_route_part, s_route_full = choose_direction(graph, new_route_fragment.end_node(), end_node, scenic_routes_remaining) # fragment odcinka widokowego, idący bardziej w kierunku punktu końcowego

        try:
            expected_route_length = route_length + new_route_fragment.length() + nx.shortest_path_length(graph, new_route_fragment.end_node(), end_node, weight='length')

            if expected_route_length >= maximum_length:
                scenic_routes_remaining.remove(s_route_full)
                break
            s_route_sliced = slice_route_for_shortest_paths(graph, s_route_part)
            for s_route_small in s_route_sliced:
                expected_route_length = route_length + new_route_fragment.length() + new_scenic_fragment.length() + s_route_small.length() + nx.shortest_path_length(
                        graph, s_route_small.end_node(), end_node, weight = 'length')
                if expected_route_length >= maximum_length:
                    break
                new_scenic_fragment.add(s_route_small)

            if new_scenic_fragment.length() > 0:
                route_so_far.add(new_route_fragment)
                route_so_far.add(new_scenic_fragment)
                scenic_routes_visited.append(new_scenic_fragment)
                actual_node = route_so_far.end_node()
                scenic_routes_remaining.remove(s_route_full)

                route_length = route_so_far.length()
                scenic_route_length = scenic_route_length + new_scenic_fragment.length()
                continue
            elif s_route_full in scenic_routes_remaining:
                scenic_routes_remaining.remove(s_route_full)

        except nx.NetworkXNoPath:
            if s_route_full in scenic_routes_remaining:
                scenic_routes_remaining.remove(s_route_full)
            print('No path')
            continue

    last_nodes = nx.shortest_path(graph, actual_node, end_node, weight = 'length')
    last_edges = get_edges_of_nodes_path(last_nodes)
    last_length = nx.shortest_path_length(graph, actual_node, end_node, weight = 'length')
    route_so_far.add(ARoute(last_nodes, last_length, last_edges))

    return route_so_far, scenic_routes_visited


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
        if nodeB is None:  # pierwszy lub drugi node
            if nodeA is None:
                nodeA = node  # pierwszy node
            else:
                nodeB = node  # drugi node
                new_edges.append((nodeA, nodeB))
        else:
            nodeA = nodeB
            nodeB = node
            new_edges.append((nodeA, nodeB))
    return new_edges


def get_route_to_closest_node(graph, actual_node, all_nodes):
    route_to_closest_node = None
    for other_node in all_nodes:
        if other_node == actual_node:
            continue
        if route_to_closest_node is None:
            route_nodes = nx.shortest_path(graph, actual_node, other_node, weight = 'length')
            route_to_closest_node = ARoute(route_nodes, nx.shortest_path_length(graph, actual_node, other_node, weight='length'), get_edges_of_nodes_path(route_nodes))
        elif route_to_closest_node.length() > nx.shortest_path_length(graph, actual_node, other_node, weight='length'):
            nodes = nx.shortest_path(graph, actual_node, other_node, weight='length')
            route_to_closest_node = ARoute(nodes, nx.shortest_path_length(graph, actual_node, other_node, weight='length'), get_edges_of_nodes_path(nodes))

    return route_to_closest_node


def get_routes_with_minimal_length(routes, minimal_length):
    return [r for r in routes if r.length() >= minimal_length]


def reverse_path(graph, path):
    path.nodes().reverse()
    new_edges = get_edges_of_nodes_path(path.nodes())
    new_length =  sum ([nx.shortest_path_length(graph, x, y, weight = 'length') for (x,y) in new_edges])
    return ARoute(path.nodes(), new_length, new_edges)


def choose_best_longest_scenic_route(graph, actual_node, end_node, scenic_routes, maximum_left_length):

    route_in_scenic = ARoute()
    route_in_scenic_full = ARoute()
    route_length = 0

    for sr in scenic_routes:
        route_to_scenic_length = nx.shortest_path_length(graph, actual_node, sr.start_node(), weight='length')
        s_route_sliced = slice_route_for_shortest_paths(graph, sr)
        s_route_part = ARoute()
        old_route_length = 0
        for s_route_small in s_route_sliced:
            new_route_length = route_to_scenic_length + s_route_part.length() + s_route_small.length() + nx.shortest_path_length(graph, s_route_small.end_node(), end_node, weight = 'length')
            if new_route_length > maximum_left_length:
                break
            else:
                s_route_part.add(s_route_small)
                if new_route_length > route_length:
                    route_length = old_route_length
                    route_in_scenic = s_route_part
                    route_in_scenic_full = sr
            old_route_length = new_route_length

    if route_in_scenic.length() > 0:
        new_nodes = nx.shortest_path(graph, actual_node, route_in_scenic.start_node(), weight='length')
        new_edges = get_edges_of_nodes_path(new_nodes)
        new_length = nx.shortest_path_length(graph, actual_node, route_in_scenic.start_node(), weight='length')
        return ARoute(new_nodes, new_length, new_edges), route_in_scenic, route_in_scenic_full

    return ARoute(), route_in_scenic, route_in_scenic_full


def choose_best_astar_scenic_route(graph, actual_node, end_node, scenic_small_routes):

    all_lengths = []

    for sr in scenic_small_routes:
        route_to_scenic_length = nx.shortest_path_length(graph, actual_node, sr.start_node(), weight='length')
        new_route_length = route_to_scenic_length + sr.length() + + nx.shortest_path_length(graph, sr.end_node(),
                                                                                            end_node, weight='length')
        all_lengths.append(new_route_length)

    best_length = min(all_lengths)

    route_in_scenic = scenic_small_routes[all_lengths.index(best_length)]

    new_nodes = nx.shortest_path(graph, actual_node, route_in_scenic.start_node(), weight='length')
    new_edges = get_edges_of_nodes_path(new_nodes)
    new_length = nx.shortest_path_length(graph, actual_node, route_in_scenic.start_node(), weight='length')
    return ARoute(new_nodes, new_length, new_edges), route_in_scenic, route_in_scenic


def build_a_route_with_longest_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length):
    actual_node = start_node

    route_so_far = ARoute()
    maximum_length_left = maximum_length

    scenic_routes_remaining = scenic_routes[:]
    scenic_routes_visited = []
    scenic_routes_unused = scenic_routes_remaining[:]

    removed_best_route_full = []

    #while len(scenic_routes_unused) > 0:
    while sum([sr.length() for sr in scenic_routes_visited]) < minimum_scenic_length and len(scenic_routes_unused) > 0:
            route_to_best_route, best_route_part, best_route_full = choose_best_longest_scenic_route(graph, actual_node, end_node, scenic_routes_unused, maximum_length_left)
            if best_route_full in scenic_routes_unused:
                scenic_routes_unused.remove(best_route_full)
                scenic_route_length = route_to_best_route.length() + best_route_part.length()
                expected_scenic_route_length = scenic_route_length + nx.shortest_path_length(graph, best_route_part.end_node(), end_node, weight = 'length' )
                if expected_scenic_route_length > maximum_length_left:
                    removed_best_route_full.append(best_route_full)
                else:
                    maximum_length_left = maximum_length_left - scenic_route_length
                    route_so_far.add(route_to_best_route)
                    route_so_far.add(best_route_part)
                    scenic_routes_visited.append(best_route_part)
                    actual_node = best_route_part.end_node()
                    if len(removed_best_route_full) > 0:
                        scenic_routes_unused = scenic_routes_unused + removed_best_route_full
                        removed_best_route_full = []
            else:
                break

    last_nodes = nx.shortest_path(graph, actual_node, end_node, weight = 'length')
    last_edges = get_edges_of_nodes_path(last_nodes)
    last_length = nx.shortest_path_length(graph, actual_node, end_node, weight = 'length')
    route_so_far.add(ARoute(last_nodes, last_length, last_edges))

    return route_so_far, scenic_routes_visited


def build_a_route_with_astar_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length):
    actual_node = start_node

    route_so_far = ARoute()
    maximum_length_left = maximum_length

    small_s_routes = []
    for sr in scenic_routes:
        small_s_routes = small_s_routes + slice_route_for_shortest_paths(graph, sr)

    scenic_routes_visited = []

    #while len(small_s_routes) > 0:
    while sum([sr.length() for sr in scenic_routes_visited]) < minimum_scenic_length and len(small_s_routes) > 0 :
        route_to_best_route, best_route_part, best_route_full = choose_best_astar_scenic_route(graph, actual_node, end_node, small_s_routes)
        if best_route_full in small_s_routes:

            scenic_route_length = route_to_best_route.length() + best_route_part.length()
            if route_so_far.length() + scenic_route_length + nx.shortest_path_length(graph, best_route_part.end_node(), end_node,
                                                            weight='length') > maximum_length:
                break
            small_s_routes.remove(best_route_full)
            maximum_length_left = maximum_length_left - scenic_route_length
            route_so_far.add(route_to_best_route)
            route_so_far.add(best_route_part)
            scenic_routes_visited.append(best_route_part)
            actual_node = best_route_part.end_node()
        else:
            break

    last_nodes = nx.shortest_path(graph, actual_node, end_node, weight = 'length')
    last_edges = get_edges_of_nodes_path(last_nodes)
    last_length = nx.shortest_path_length(graph, actual_node, end_node, weight = 'length')
    route_so_far.add(ARoute(last_nodes, last_length, last_edges))

    return route_so_far, scenic_routes_visited


def generate_scenic_routes(graph, min_long, min_lat, l_long, l_lat, number = 10, version = 'sparse'):
    routes = []

    coefficients = [0.02*x for x in range(1, 50)]
    random.seed(17)

    if version == 'sparse':
        start_indices = [(random.randrange(8, 36), random.randrange(8, 36)) for x in range(number)]
    elif version == 'cumulated':
        start_indices = [(random.randrange(20, 25), random.randrange(6, 9)) for x in range(number)]
    elif version == 'far':
        start_indices = [(random.randrange(6, 9), random.randrange(8, 36)) for x in range(number)]
    elif version == 'long':
        start_indices = [(random.randrange(8, 20), random.randrange(8, 20)) for x in range(number)]
    for (i_long, i_lat) in start_indices:
        start_long = min_long + coefficients[i_long]*l_long
        start_lat = min_lat + coefficients[i_lat]*l_lat
        if (version == 'long'):
            end_long = min_long + coefficients[i_long + random.randrange(15, 20)] * l_long
            end_lat = min_lat + coefficients[i_lat + random.randrange(15, 20)] * l_lat
        else:
            end_long = min_long + coefficients[i_long + random.randrange(1, 6)] * l_long
            end_lat = min_lat + coefficients[i_lat + random.randrange(1, 6)] * l_lat
        r = create_a_route(graph, start_lat, start_long, end_lat, end_long)
        if r != None:
            routes.append(r)

    return routes

def main():
    print('Welcome to ScenicRoute app!')
    print('\nLoading routes graph...')
    graph = nx.read_gpickle("places/zamosc.gpickle")
    graph_proj = ox.project_graph(graph)
    nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
    print('DONE')

    lon_max = nodes_proj['lon'].max()
    lon_min = nodes_proj['lon'].min()
    l_long = lon_max - lon_min
    lat_max = nodes_proj['lat'].max()
    lat_min = nodes_proj['lat'].min()
    l_lat = lat_max - lat_min

    mode = input('\nDo you want to run demonstration mode? [y/n]\t')
    if mode == 'n':
        print('\nAvailable longitudes:\t' + str(lon_min) + '-' + str(lon_max))
        print('Available latitudes:\t' + str(lat_min) + '-' + str(lat_max))

        if input('\nUse default lat and lon? [y/n]\t') == 'n':
            print('\nSpecify desired start and end points:')
            start_lon = float(input('Type start longitude:\t'))
            start_lat = float(input('Type start latitude:\t'))
            end_lon = float(input('Type end longitude:\t'))
            end_lat = float(input('Type end latitude:\t'))

        else:

            alfa1 = 0.3
            beta1 = 0.6
            alfa2 = 0.7
            beta2 = 0.4

            start_lon = float(lon_min + alfa1 * l_long)
            start_lat = float(lat_min + beta1 * l_lat)
            end_lon = float(lon_min + alfa2 * l_long)
            end_lat = float(lat_min + beta2 * l_lat)

    else:

        alfa1 = 0.3
        beta1 = 0.6
        alfa2 = 0.7
        beta2 = 0.4

        start_lon = float(lon_min + alfa1 * l_long)
        start_lat = float(lat_min + beta1 * l_lat)
        end_lon = float(lon_min + alfa2 * l_long)
        end_lat = float(lat_min + beta2 * l_lat)

    print('\nFinding shortest route...')
    start_point, start_node = find_nearest_node(graph, start_lat, start_lon)
    end_point, end_node = find_nearest_node(graph, end_lat, end_lon)
    route = nx.shortest_path(G=graph, source=start_node, target=end_node, weight='length')
    route_length = nx.shortest_path_length(G=graph, source=start_node, target=end_node, weight='length')
    print('Shortest route length:\t' + str(route_length) + ' meters')

    print('DONE')

    scenic_routes1 = generate_scenic_routes(graph, lon_min, lat_min, l_long, l_lat,
                                            10, 'sparse')
    scenic_routes2 = generate_scenic_routes(graph, lon_min, lat_min, l_long, l_lat,
                                            10,
                                            'cumulated')
    scenic_routes3 = generate_scenic_routes(graph, lon_min, lat_min, l_long, l_lat,
                                            10,
                                            'far')
    scenic_routes4 = generate_scenic_routes(graph, lon_min, lat_min, l_long, l_lat,
                                            10,
                                            'long')

    scenic_types = {'sparse': scenic_routes1, 'cumulated': scenic_routes2, 'far': scenic_routes3,
                    'long': scenic_routes4}
    scenic_routes_list = [scenic_types['sparse'], scenic_types['cumulated'], scenic_types['far']]

    if mode == 'n':
        print('\nAvailable types of scenic routes:')
        print('1 - sparse')
        print('2 - cumulated')
        print('3 - far')
        print('4 - long')
        typee = input('Type number of desired type:\t')
        types = {1: 'sparse', 2: 'cumulated', 3: 'far', 4: 'long'}
        scenic_routes = scenic_types[types[int(typee)]]

        print('\nScenic routes parameters preference:')
        if input('Use default? [y/n]\t') == 'n':
            max_extra_dist = float(input('Type max extra distance [m]:\t'))
            minimum_scenic_length = float(input('Type min scenic distance [m]:\t'))
        else:
            max_extra_dist = float(6700)
            minimum_scenic_length = float(3000)
        print('DONE')

        if input('\n Do you want max extra distance to be hard limitation? [y/n]:\t') == 'n':
            maximum_length = 100000
        else:
            maximum_length = route_length + max_extra_dist

        the_route_closest, scenic_routes_visited_closest = build_a_route_with_closest_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length)
        print("\nFound route and sum of scenic routes - closest scenic route algorithm")
        print(the_route_closest.length(), sum([sr.length() for sr in scenic_routes_visited_closest]))

        the_route_longest, scenic_routes_visited_longest = build_a_route_with_longest_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length)
        print("\nFound route and sum of scenic routes - longest scenic route algorithm")
        print(the_route_longest.length(), sum([sr.length() for sr in scenic_routes_visited_longest]))

        the_route_astar, scenic_routes_visited_astar = build_a_route_with_astar_scenic_routes(graph, start_node,  end_node, scenic_routes, minimum_scenic_length, maximum_length)
        print("\nFound route and sum of scenic routes - a star scenic route algorithm")
        print(the_route_astar.length(), sum([sr.length() for sr in scenic_routes_visited_astar]))

        scenic_routes_nodes_lists = [s.nodes() for s in scenic_routes]

        print('\nClose maps to continue...')

        fig, ax = ox.plot_graph_route(graph, route, show=False, close=False)
        fig_closest, ax_closest = ox.plot_graph_route(graph, the_route_closest.nodes(), show=False,
                                                      close=False)  # nie dziala wyswietlanie, z jakiegos powodu niektore wierzcholki nie wystepuja w krawedziach grafu
        fig_longest, ax_longest = ox.plot_graph_route(graph, the_route_longest.nodes(), show=False, close=False)
        fig_astar, ax_astar = ox.plot_graph_route(graph, the_route_astar.nodes(), show=False, close=False)

        fig_sc, ax_sc = ox.plot_graph_routes(graph, scenic_routes_nodes_lists, route_color='y', show=False, close=False)
        plt.show()

    else:

        minimum_scenic_length = 3000
        maximum_length_hard = route_length + 6700

        print ('\nCalculating routes...')
        for maximum_length in [maximum_length_hard, 100000]:
            print('Maximum length of route:')
            print (maximum_length_hard)
            for scenic_type, scenic_routes in scenic_types.items():
                if scenic_routes not in scenic_routes_list:
                    continue
                print('\nType of scenic routes: ' + scenic_type)

                the_route_closest, scenic_routes_visited_closest = build_a_route_with_closest_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length)
                print("\nFound route and sum of scenic routes - closest scenic route algorithm")
                print(the_route_closest.length(), sum([sr.length() for sr in scenic_routes_visited_closest]))

                the_route_longest, scenic_routes_visited_longest = build_a_route_with_longest_scenic_routes(graph, start_node, end_node, scenic_routes,minimum_scenic_length, maximum_length)
                print("\nFound route and sum of scenic routes - longest scenic route algorithm")
                print(the_route_longest.length(), sum([sr.length() for sr in scenic_routes_visited_longest]))

                the_route_astar, scenic_routes_visited_astar = build_a_route_with_astar_scenic_routes(graph, start_node, end_node, scenic_routes, minimum_scenic_length, maximum_length)
                print("\nFound route and sum of scenic routes - a star scenic route algorithm")
                print(the_route_astar.length(), sum([sr.length() for sr in scenic_routes_visited_astar]))

                scenic_routes_nodes_lists = [s.nodes() for s in scenic_routes]


                print('\nClose maps to continue...')

                fig, ax = ox.plot_graph_route(graph, route, show=False, close=False)
                fig_closest, ax_closest = ox.plot_graph_route(graph, the_route_closest.nodes(), show=False, close=False) #nie dziala wyswietlanie, z jakiegos powodu niektore wierzcholki nie wystepuja w krawedziach grafu
                fig_longest, ax_longest = ox.plot_graph_route(graph, the_route_longest.nodes(), show=False, close=False)
                fig_astar, ax_astar = ox.plot_graph_route(graph, the_route_astar.nodes(), show=False, close=False)

                fig_sc, ax_sc = ox.plot_graph_routes(graph, scenic_routes_nodes_lists, route_color='y', show=False, close=False)
                plt.show()

    print("\nGood bye!")

if __name__ == "__main__":
    main()
