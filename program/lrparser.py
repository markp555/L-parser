from slrtable import *
from gss import *

LAST_TRACE = -3
NO_TRACE = -3
FULL_TRACE = -1



class Path:
    def __init__(self, vertices: List[parse_vertex_sp], base_nodes: Set[gss_node_sp]):
        self.vertices = vertices
        self.base_nodes = base_nodes


class LRParser:
    def __init__(self, _table):
        self.table = _table
        self.target_step = None
        self.pos = 0
        self.token = None
        self.just_created = []
        self.reduce_stack = []
        self.parse_vertex_count = {}
        self.stubs = set()
        self.jss_node_sp = gss_node.get_node(0, parse_vertex.get_vertex("", 0))
        self.bottom = self.jss_node_sp
        self.shift_map = {}
        self.terminal_vertices = []
        self.accepted = []

    def parse(self, in_list, target_step=NO_TRACE):
        self.target_step = target_step
        self.token = in_list[self.pos]
        empty_string = ""
        empty_vertex = parse_vertex.get_vertex(empty_string, 0)
        bottom = gss_node.get_node(0, empty_vertex)
        self.update(bottom, in_list[self.pos])
        self.next_step()

        while True:
            # Reduce stage
            self.just_created = []
            while len(self.reduce_stack) != 0:
                reduce = self.reduce_stack.pop()
                rule = reduce[1]
                paths = gss_node.look(reduce[0], len(rule.RHS))
                for path in paths:
                    p_vertex = parse_vertex.get_vertex(
                        path.vertices, rule.LHS, self.parse_vertex_count.get(rule.LHS, 0))
                    for pv in path.vertices:
                        self.stubs.extract(pv)
                    base_nodes = path.base_nodes
                    goto_partition = {}
                    for node in base_nodes:
                        goto_partition[self.table.GoTo(node.state, rule.LHS)].add(node)
                    is_parse_vertex_created = False
                    for s, s_part in goto_partition.items():
                        amb_flag = False
                        for node in self.just_created:
                            if s == node.state and s_part == node.childs:
                                amb_flag = True
                                # tree packing
                                node.parse_vertex.paths.append(path.vertices)
                                break
                        if amb_flag:
                            continue
                        is_parse_vertex_created = True
                        node = gss_node.get_node(s_part, s, p_vertex)
                        self.stubs.add(p_vertex)
                        self.just_created.append(node)
                        self.update(node, in_list[self.pos])
                        if is_parse_vertex_created:
                            self.parse_vertex_count[rule.LHS] += 1
                    self.next_step()
            if len(self.shift_map) != 0:
                if self.token not in self.parse_vertex_count:
                    self.parse_vertex_count[self.token]=0
                parse_vertex2 = parse_vertex.get_vertex(self.token, self.parse_vertex_count[self.token])
                self.parse_vertex_count[self.token] += 1
                self.terminal_vertices.append(parse_vertex2)
                self.stubs.add(parse_vertex2)
                next_tops = set()
                for shift_state, shift_nodes in self.shift_map.items():
                    accum = gss_node.get_node2(shift_nodes, shift_state, parse_vertex2)
                    next_tops.add(accum)
                self.shift_map = {}
                self.pos += 1
                self.token = in_list[self.pos]
                for top in next_tops:
                    self.update(top, self.token)
                self.next_step()

            # Check stage
            if len(self.accepted) != 0:
                if self.target_step == LAST_TRACE:
                    make_screen()
                return True

            if len(self.reduce_stack) == 0 and len(self.shift_map) == 0:
                if self.target_step == LAST_TRACE:
                    make_screen()
                return False


    def stack_to_graph(self, out):
        out.write("digraph {n")
        out.write("rankdir=RLn")
        out.write("label=\"next token: \" + self.token + \"\\npos: " + str(self.pos) + "\n")
        out.write("node [shape=box]n")

        tops = {}
        visited = set()

        for i in range(len(self.reduce_stack)):
            reduce = self.reduce_stack[i]
            node, rule = reduce
            tops[node] = tops.get(node, "") + "reduce(" + rule.LHS + " -> " + ' '.join(rule.RHS) + ")n"

        for shift_state, shift_nodes in self.shift_map.items():
            for node in shift_nodes:
                tops[node] = tops.get(node, "") + "shift(" + str(shift_state) + ")n"

        for node in self.accepted:
            tops[node] = "acc"

        for node, xlabel in tops.items():
            out.write(""" + str(node) + """ + "[xlabel="" + xlabel + "", shape=ellipse]n")
            self.stack_to_graph_dfs(node, out, visited)

        out.write("}n")

    def make_screen(self):
        stack_name = "stack/step_" + str(self.step) + ".dot"
        tree_name = "tree/step_" + str(self.step) + ".dot"
        with open(stack_name, 'w') as stack_out, open(tree_name, 'w') as tree_out:
            self.stack_to_graph(stack_out)
            self.parse_tree_to_graph(tree_out)

    def next_step(self):
        if self.target_step == FULL_TRACE or (self.target_step >= 0 and self.step == self.target_step):
            self.make_screen()
        self.step += 1

    def init(self, target_step):
        self.target_step = target_step
        if target_step == LAST_TRACE or target_step == FULL_TRACE or target_step >= 0:
            os.system("mkdir tree")
            os.system("mkdir stack")
        self.pos = 0
        self.step = 0
        self.parse_vertex_count = {}
        self.reduce_stack = {}
        self.shift_map = {}
        self.just_created = {}
        self.accepted = {}
        

    def update(self, target, token):
        self.actions = self.table.GetActions(target.state, token)
        if self.actions.is_acc:
            self.accepted.add(target)
        for rule in self.actions.reduceActions:
            self.reduce_stack.append((target, rule))
        for shift_state in self.actions.shiftActions:
            if shift_state not in self.shift_map:
                self.shift_map[shift_state]=set()
            self.shift_map[shift_state].add(target)
        shift_number = len(self.actions.shiftActions)

    def stack_to_graph_dfs(self, t, out, visited):
        visited.add(t)
        out.write("\"" + str(t) + "\" [label=<" + str(t.state) + " (" + t.parse_vertex.name + "<SUB>" + str(t.parse_vertex.index) + "</SUB>" + ")>]n")
        
        for child in t.childs:
            out.write("\"" + str(t) + "\" -> \"" + str(child) + "\n")
            
            if child not in visited:
                self.stack_to_graph_dfs(child, out, visited)

    def parse_tree_to_graph(self, out):
        out.write("digraph {\n")
        out.write("label=\"sentence: ")
        for v in self.terminal_vertices:
            out.write(v.name + " ")
        out.write("\n")
        out.write("node [shape=circle];\n")
        out.write("compound=true;\n")
        out.write("rank1 [style = invis];\n")
        out.write("{\n")
        out.write("rank = same;\n")
        out.write("node [shape=box];\n")
        out.write("rank1 \n")
        for v in self.terminal_vertices:
            out.write(" -> " + get_vertex_name(v, 1) + "\n")
        out.write(" [style = invis];\n")
        out.write("}\n")
        
        visited = set()
        for pv in self.stubs:
            self.parse_tree_to_graph_dfs(pv, out, visited)
        
        out.write("}\n")

    def parse_tree_to_graph_dfs(self,pv, out, visited):
        visited.add(pv)
    
        if len(pv.paths) > 1:
            out.write("subgraph \"cluster_" + str(pv) + "\" {\n")
            out.write("style=filled;\n")
            out.write("color=lightgrey;\n")
            out.write("label = <" + pv.name + "<SUB>" + str(pv.index) + "</SUB>>;\n")
        
            for i in range(len(pv.paths)):
                p = pv.paths[i]
                p_name = self.get_vertex_name(pv, i)
                out.write(p_name + " [label=" + str(i) + "]\n")
        
            out.write("}\n")
        
            for i in range(len(pv.paths)):
                p = pv.paths[i]
                p_name = self.get_vertex_name(pv, i)
            
                for j in range(len(p) - 1, -1, -1):
                    child = p[j]
                    c_name = self.get_vertex_name(child, 1)
                    out.write(p_name + " -> " + c_name)
                
                    if len(child.paths) > 1:
                        out.write("[lhead=\"cluster_" + str(child) + "\"]")
                
                    out.write("\n")
                
                    if child not in visited:
                        self.parse_tree_to_graph_dfs(child, out, visited)
        
            return
    
        p_name = get_vertex_name(pv, 1)
        out.write(p_name + "[label = <" + pv.name + "<SUB>" + str(pv.index) + "</SUB>>];\n")
    
        for p in pv.paths:
            for child in p:
                c_name = get_vertex_name(child, 1)
                out.write(p_name + " -> " + c_name)
            
                if len(child.paths) > 1:
                    out.write("[lhead=\"cluster_" + str(child) + "\"]")
            
                out.write("\n")
            
                if child not in visited:
                    self.parse_tree_to_graph_dfs(child, out, visited)
