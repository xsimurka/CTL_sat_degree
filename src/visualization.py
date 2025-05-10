from networkx.drawing.nx_pydot import to_pydot
from src.multivalued_grn import MvGRNParser, StateTransitionGraph
import networkx as nx
import json

# # Open and read the file
# with open('../data/incoherent_ffl1.json', 'r') as f:
#     coh_ffl = json.load(f)
#
# mvgrn = MvGRNParser(coh_ffl.get("network")).parse()
# stg = StateTransitionGraph(mvgrn)
#
# start_state = (0, 0, 0)
#
# reachable_nodes = nx.descendants(stg.graph, start_state)
# reachable_nodes.add(start_state)
# reachable_subgraph = stg.graph.subgraph(reachable_nodes).copy()
#
# # Find all strongly connected components
# sccs = list(nx.strongly_connected_components(reachable_subgraph))
#
# # Identify bottom SCCs
# bottom_sccs = []
# for scc in sccs:
#     has_outgoing = False
#     for node in scc:
#         for succ in reachable_subgraph.successors(node):
#             if succ not in scc:
#                 has_outgoing = True
#                 break
#         if has_outgoing:
#             break
#     if not has_outgoing:
#         bottom_sccs.append(scc)
#
# # Now build the pydot graph and highlight
# pydot_graph = to_pydot(reachable_subgraph)
# for node in pydot_graph.get_nodes():
#     node.set_fontsize("32")
# # Highlight bottom SCC nodes
# for scc in bottom_sccs:
#     for node in scc:
#         # Find the corresponding pydot node
#         pydot_node = pydot_graph.get_node(str(node))[0]
#         pydot_node.set_style('filled')
#         pydot_node.set_fillcolor('lightblue')  # or any color you like
#         pydot_node.set_penwidth(2)
#
# pydot_graph.write_png("../stg/single_input_module.png")
# print(len(bottom_sccs))
# print(len(bottom_sccs[0]))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

data = [
    [2.15, 16.90, 37.40, 62.90, 170.67, 283.58],
    [1.91, 14.36, 18.34, 37.45, 94.51, 167.38],
    [1.46, 10.96, 14.13, 31.23, 76.81, 139.49],
    [1.31, 3.59, 8.16, 15.15, 30.30, 44.93],
    [0.53, 2.70, 6.79, 13.13, 19.96, 37.64],
]

col_labels = ['567', '1008', '1792', '2800', '4375', '6624']
row_labels = ['12', '10', '8', '6', '4']

data_array = np.array(data)

fig, ax = plt.subplots(dpi=300)
cax = ax.imshow(data_array, cmap='RdYlGn_r', norm=LogNorm(vmin=np.min(data_array), vmax=np.max(data_array)))

# Show all ticks and label them
ax.set_xticks(np.arange(len(col_labels)))
ax.set_yticks(np.arange(len(row_labels)))
ax.set_xticklabels(col_labels, fontsize=9)
ax.set_yticklabels(row_labels, fontsize=9)

# Rotate x labels
plt.xticks(rotation=0)

# Annotate cells with the data
for i in range(len(row_labels)):
    for j in range(len(col_labels)):
        ax.text(j, i, f"{data[i][j]:.2f}", ha='center', va='center', color='black' if 200 > data[i][j] > 1 else "white", fontsize=8, fontweight='bold')

# Labels and title
ax.set_xlabel("Size of state space", fontsize=11)
ax.set_ylabel("Number of APs in formula", fontsize=11)
ax.set_title("Computation time (s) for input instances", fontsize=12)

#plt.tight_layout()
plt.show()
