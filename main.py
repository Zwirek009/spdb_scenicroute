import osmnx as ox
from shapely.geometry import box
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

place_name = "Srodmiescie, Warsaw, Poland"
graph = ox.graph_from_place(place_name, network_type='drive')
graph_proj = ox.project_graph(graph)
nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)

bbox = box(*edges_proj.unary_union.bounds)

start_point = bbox.centroid

nodes_proj['x'] = nodes_proj.x.astype(float)
maxx = nodes_proj['x'].max()
end_loc = nodes_proj.loc[nodes_proj['x']==maxx, :]
end_point = end_loc.geometry.values[0]

start_xy = (start_point.y, start_point.x)
end_xy = (end_point.y, end_point.x)
start_node = ox.get_nearest_node(graph_proj, start_xy, method='euclidean')
end_node = ox.get_nearest_node(graph_proj, end_xy, method='euclidean')

route = nx.shortest_path(G=graph_proj, source=start_node, target=end_node, weight='length')
fig, ax = ox.plot_graph_route(graph_proj, route, origin_point=start_xy, destination_point=end_xy)