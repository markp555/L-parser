from forest import *

def join(src, delim=""):
    return delim.join(src)

def get_vertex_name(pv, i):
    return "\"" + str(pv) + "_" + str(i) + "\""

from typing import List, Set

class gss_node:
    def __init__(self, childs: Set['gss_node'], state: int, parse_vertex):
        self.childs = childs
        self.state = state
        self.parse_vertex = parse_vertex

    @staticmethod
    def get_node2(childs: Set['gss_node'], state: int, parse_vertex=None) -> 'gss_node':
        return gss_node(childs, state, parse_vertex)

    @staticmethod
    def get_node(state: int, parse_vertex=None) -> 'gss_node':
        node = gss_node(set(), state, parse_vertex)
        return node

    @staticmethod
    def look(target: 'gss_node', n: int) -> List['Path']:
        result = []
        gss_node.look_dfs(target, n, result, [])
        return result

    @staticmethod
    def look_dfs(target: 'gss_node', n: int, result: List['Path'], path: List) -> None:
        path.append(target.parse_vertex)
        if n == 1:
            result.append(Path(path, target.childs))
            return
        for child in target.childs:
            gss_node.look_dfs(child, n - 1, result, path)

parse_vertex_sp=parse_vertex
gss_node_sp = gss_node
vector = list
unordered_set = set
