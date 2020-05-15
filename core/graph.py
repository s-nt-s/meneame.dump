import json
import networkx as nx
from networkx.readwrite import json_graph
from random import randint as rand
from bunch import Bunch
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import write_dot
from .j2 import Jnj2

class Graph:
    def __init__(self, *args, **kargv):
        self.G = nx.Graph()

    def add(self, id, size):
        self.G.add_node(id, size=size)

    def add_edge(self, a, b, **kargv):
        if a not in self.G.nodes:
            return
            #self.G.add_node(a)
        if b not in self.G.nodes:
            return
            #self.G.add_node(b)
        self.G.add_edge(a, b, **kargv)

    def show(self):
        pos = nx.nx_agraph.graphviz_layout(self.G)
        nx.draw(self.G, with_labels=True, font_weight='bold', pos=pos)
        plt.show()

    @property
    def nodes(self):
        return tuple(self.G.nodes)

    @property
    def sigmajs(self):
        pos = nx.nx_agraph.graphviz_layout(self.G)

        js = json_graph.node_link_data(self.G)
        sizes = set(nd['size'] for nd in js['nodes'] if 'size' in nd)
        max_size = max(sizes)
        min_size = min(sizes)
        delta = max_size - min_size
        for i, nd in enumerate(js['nodes']):
            p = pos[nd['id']]
            nd['x'] = p[0]
            nd['y'] = p[1]
            if 'weight' not in nd:
                nd['weight'] = nd.get('size')
            if 'size' not in nd:
                nd['size'] = 0.5
            else:
                sz = (nd['size'] - min_size)
                sz = sz / delta
                sz = sz * 4
                nd['size'] = sz + 1
        js['edges'] = js['links']
        for i, e in enumerate(js['edges']):
            e["id"]=i
        for k in list(js.keys()):
            if k not in ("edges", "nodes"):
                del js[k]
        return js


if __name__ == "__main__":
    G = Graph(max_size=7732, color_node=None)

    G.add("PP", size=7732)
    G.add("España", size=6141)
    G.add("EE.UU.", size=4072)
    G.add("crisis", size=3797)
    G.add("Madrid", size=3581)
    G.add("humor", size=3445)
    G.add("corrupcion", size=3207)
    G.add("politica", size=2960)
    G.add("internet", size=2960)
    G.add("policia", size=2617)

    G.add_edge("PP", "corrupcion", weight=1179)
    G.add_edge("España", "crisis", weight=349)
    G.add_edge("EE.UU.", "guerra", weight=546)
    G.add_edge("Madrid", "PP", weight=395)
    G.add_edge("humor", "viñeta", weight=167)
    G.add_edge("corrupcion", "PP", weight=1179)
    G.add_edge("politica", "PP", weight=421)
    G.add_edge("internet", "google", weight=136)
    G.add_edge("policia", "Madrid", weight=123)

    jHtml = Jnj2("template/", "docs/")
    jHtml.create_script("data/graph.js", replace=True,
        graphs={
            "tags": G.sigmajs
        }
    )
