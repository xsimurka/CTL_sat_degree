from networkx.drawing.nx_pydot import to_pydot
from src.multivalued_grn import MvGRNParser, StateTransitionGraph
import networkx as nx
import json

# Open and read the file
with open('../data/incoherent_ffl4.json', 'r') as f:
    coh_ffl = json.load(f)

mvgrn = MvGRNParser(coh_ffl.get("network")).parse()
stg = StateTransitionGraph(mvgrn)

start_state = (0, 0, 0)

reachable_nodes = nx.descendants(stg.graph, start_state)
reachable_nodes.add(start_state)
reachable_subgraph = stg.graph.subgraph(reachable_nodes).copy()

# Find all strongly connected components
sccs = list(nx.strongly_connected_components(reachable_subgraph))

# Identify bottom SCCs
bottom_sccs = []
for scc in sccs:
    has_outgoing = False
    for node in scc:
        for succ in reachable_subgraph.successors(node):
            if succ not in scc:
                has_outgoing = True
                break
        if has_outgoing:
            break
    if not has_outgoing:
        bottom_sccs.append(scc)

# Now build the pydot graph and highlight
pydot_graph = to_pydot(reachable_subgraph)

pydot_graph.set_prog("dot")
# Customize node appearance
for node in pydot_graph.get_nodes():
    node.set_fontname("Helvetica-Bold")
    node.set_fontsize("32")
    node.set_penwidth(2)

# Customize edge appearance
for edge in pydot_graph.get_edges():
    edge.set_penwidth(2)


# Highlight bottom SCC nodes
for scc in bottom_sccs:
    for node in scc:
        # Find the corresponding pydot node
        pydot_node = pydot_graph.get_node(str(node))[0]
        pydot_node.set_style('filled')
        pydot_node.set_fillcolor('lightblue')  # or any color you like

pydot_graph.write_png("../stg/incoherent_ffl4.png")
print(len(bottom_sccs))
print(len(bottom_sccs[0]))
