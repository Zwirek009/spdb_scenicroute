import osmnx as ox
import networkx as nx

# variables
place_name = "Srodmiescie, Warsaw, Poland"
file_name = "srodmiescie.gpickle"

# script body
graph = ox.graph_from_place(place_name, network_type='drive')
nx.write_gpickle(graph, "places/"+file_name)
