import re

states = []
edges = {}

with open("gsd.ginml", "r") as gs_f:
    for line in gs_f:
        patternn = r'<node id="s(\d{5})">'
        match = re.search(patternn, line.strip())

        if match:
            m = match.group(1)
            state = tuple([int(d) for d in m])
            states.append(state)

        patterne = r'<edge id="s(\d{5})_s(\d{5})"'
        match = re.search(patterne, line.strip())

        if match:
            s1 = tuple([int(d) for d in match.group(1)])
            s2 = tuple([int(d) for d in match.group(2)])

            edges.setdefault(states.index(s1), []).append(states.index(s2))

print(len(states))
print(len(edges))
print(states)
print(edges)
