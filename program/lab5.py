import argparse
import copy
import sys
import re
import os
parser = argparse.ArgumentParser(prog="lab5")
parser.add_argument("-g", "--grammar",dest="grammar",help="specify the grammar input file.",required=True)
inputg = parser.add_mutually_exclusive_group(required=True)
inputg.add_argument("-i","--input",dest="input",help="specify the sentence directly.")
inputg.add_argument("-f","--file",dest="file",help="specify the sentence input file.")
screenshot = parser.add_mutually_exclusive_group()
screenshot.add_argument("-s", "--step", dest="step",help="specify the screen step.", type=int)
screenshot.add_argument("-a", "--all",dest="all",action = "store_true",help=("enable full parse trace."))
screenshot.add_argument("-l", "--last",dest="last",action="store_true",help=("only last screen."))
### PARSING
#out=parser.parse_args(["-g", "grammars\\arith_grammar.txt", "-a", "-i", "id * id = id"])
#out = parser.parse_args(input().split())
out=parser.parse_args(sys.argv[1:])
inp = []
if out.input != None:
    inp+=out.input.split()
else:
    inp+=open(out.file).read().split()
inp+="@"

DOT = "."
EPSILON = "#"
NOTHING = "NOTHING"
SPEC_TOKEN = "@"

def set_to_vect(s):
    res = list(s)
    return res

def slice(v, m: int, n: int):
    first = v[m:n + 1]
    return first

def str_to_vect(string: str):
    ans = string.split()
    return ans

# GRAMMAR.CPP
class Grammar:
    def __init__(self,filename:str):
        self.rules = []
        self.terms = set()
        self.nonTerms = set()
        self.startToken = ""
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and line[-1] == '\r':
                    line = line[:-1]
                self.rules.append(line)
                self._add_non_term(line)
                
        self._add_terms()

    def _add_non_term(self, non_term: str) -> None:
        token = non_term.split()[0]
        self.nonTerms.add(token)
        if not self.startToken:
            self.startToken = token
    
    def _add_terms(self) -> None:
        for rule in self.rules:
            tokens = rule.split()
            for token in tokens:
                if token not in ['->', '|'] and token not in self.nonTerms:
                    self.terms.add(token)
    def Rules(self):
        return self.rules
    def NonTerms(self):
        return self.nonTerms
    def Terms(self):
        return self.terms
    def StartToken(self):
        return self.startToken

# FOREST.H

class parse_vertex:
    def __init__(self, path=None, name=None, index=0):
        self.paths = [] if path is None else [path]
        self.name = name
        self.index = index

    @staticmethod
    def get_vertex(path, name, index):
        return parse_vertex(path, name, index)

    @staticmethod
    def get_vertex(name, index):
        vertex = parse_vertex()
        vertex.name = name
        vertex.index = index
        return vertex

class ExtendedRule:
    def __init__(self,LHS:str="",RHS:list=[]):
        self.LHS=LHS
        self.RHS=RHS

class Actions:
    def __init__(self,shiftActions=[],reduceActions=[],is_acc=False):
        self.shiftActions=shiftActions
        self.reduceActions=reduceActions
        self.is_acc=is_acc

class SLRTable:
    class Comp:
        def __call__(self, lhs: str, rhs: str) -> bool:
            if lhs[-1] == "'":
                return True
            if rhs[-1] == "'":
                return False
            return lhs < rhs
   
    def is_belong(this,rule:ExtendedRule,arr):
        for elem in arr:
            if rule == elem:
                return True
        return False
    def PrintTable(this):
        print("\t", end="")
        for col in this.cols:
            print(col, end="\t\t")
        print()
        for i in range(len(this.table)):
            for j in range(len(this.table[i])):
                if j == 0:
                    print(f"{i}\t{this.table[i][j]}\t\t", end="")
                else:
                    print(f"{this.table[i][j]}\t\t", end="")
            print()


    def GoTo(this,state:int,token:str):
        element_iter = this.GOTOStateDict.get((state, token))
        if element_iter is None:
            return -1
        return element_iter

    def GetActions(this,state,token):
        terms = this.input_grammar.Terms()
        if token not in terms and token != SPEC_TOKEN:
            return Actions()

        ind = this.cols.index(token)
        actionsString = this.table[state][ind]

        if actionsString == "acc":
            ans = Actions()
            ans.is_acc = True
            return ans

        shiftActions = []
        reduceActions = []

        ss = actionsString.split()
        for action in ss:
            if action[0] == 'S':
                shiftActions.append(int(action[1:]))
            elif action[0] == 'R':
                rule_num = int(action[1:])
                rule = this.extendedGrammarRules[rule_num]
                rule.RHS = rule.RHS[1:]
                reduceActions.append(rule)

        return Actions(shiftActions, reduceActions)

    def processGrammar(this):
        SUFFIX = "'"

        this.new_start_token = this.input_grammar.StartToken() + SUFFIX
        while this.new_start_token in this.input_grammar.NonTerms():
            new_start_token += SUFFIX

        this.extended_grammar_rules.append(ExtendedRule(this.new_start_token, [DOT, this.input_grammar.StartToken()]))

        for rule in this.input_grammar.Rules():
            tokens = rule.split()
            lhs = ""
            rhs = [DOT]
            for token in tokens:
                if not lhs:
                    lhs = token
                elif token == "->":
                    continue
                elif token == "|":
                    this.extended_grammar_rules.append(ExtendedRule(lhs, rhs))
                    rhs = [DOT]
                else:
                    rhs.append(token)
            this.extended_grammar_rules.append(ExtendedRule(lhs, rhs))

    def findClosure(this,inp_state, token_after_dot):
        closure = []

        if token_after_dot == this.new_start_token:
            for rule in this.extended_grammar_rules:
                if rule.LHS == token_after_dot:
                    closure.append(rule)
        else:
            closure = inp_state

        prev_len = -1
        while prev_len != len(closure):
            prev_len = len(closure)

            tmp_closure = []

            for rule in closure:
                if rule.RHS[-1] != DOT:
                    dot_ind = rule.RHS.index(DOT)
                    dot_points_here = rule.RHS[dot_ind + 1]
                    for in_rule in this.extended_grammar_rules:
                        if dot_points_here == in_rule.LHS and not this.is_belong(in_rule, tmp_closure):
                            tmp_closure.append(in_rule)

            for rule in tmp_closure:
                if not this.is_belong(rule, closure):
                    closure.append(rule)

        return closure

    def GOTO(this,state, token):
        newState = []

        for rule in this.state_dict[state]:
            if rule.RHS[-1] != DOT:
                dotInd = rule.RHS.index(DOT)
                if rule.RHS[dotInd + 1] == token:
                    shiftedRule = rule
                    shiftedRule.RHS[dotInd] = shiftedRule.RHS[dotInd + 1]
                    shiftedRule.RHS[dotInd + 1] = '.'
                    newState.append(shiftedRule)

        addClosureRules = []
        for rule in newState:
            if rule.RHS[-1] != DOT:
                dotInd = rule.RHS.index(DOT)
                closureRes = this.findClosure(newState, rule.RHS[dotInd + 1])
                for inRule in closureRes:
                    if not this.is_belong(inRule, addClosureRules) and not this.is_belong(inRule, newState):
                        addClosureRules.append(inRule)

        for rule in addClosureRules:
            newState.append(rule)

        stateExists = -1
        for _state in this.state_dict:
            if this.state_dict[_state] == newState:
                stateExists = _state
                break

        if stateExists == -1:
            this.stateCount += 1
            this.state_dict[this.stateCount] = newState
            this.GOTOStateDict[(state, token)] = this.stateCount
        else:
            this.GOTOStateDict[(state, token)] = stateExists

    def computeGOTO(this,state):
        for rule in this.state_dict[state]:
            generateStatesFor = set()

            if rule.RHS[-1] != DOT:
                dotInd = rule.RHS.index(DOT)
                dotPointsHere = rule.RHS[dotInd + 1]
                if dotPointsHere not in generateStatesFor:
                    generateStatesFor.add(dotPointsHere)
        
            if generateStatesFor:
                for token in generateStatesFor:
                    this.GOTO(state, token)

    def generateStates(this):
        prevLen = -1
        used = set()

        while len(this.state_dict) != prevLen:
            prevLen = len(this.state_dict)
            keys = this.getKeys(this.state_dict)
            for key in keys:
                if key not in used:
                    used.add(key)
                    this.computeGOTO(key)

    def createParseTable(this):
        v = [''] * (len(this.input_grammar.NonTerms()) + len(this.input_grammar.Terms()) + 1)
        this.table = [v for _ in range(this.stateCount + 1)]
        #print(this.table)
        non_terms = this.input_grammar.NonTerms()
        terms = this.input_grammar.Terms()

        this.cols = this.findCols()

        for entry in this.GOTOStateDict:
            state = entry[0]
            token = entry[1]
            col = this.cols.index(token)
            if token in non_terms:
                this.table[state][col] += str(this.GOTOStateDict[entry])
            if token in terms:
                this.table[state][col] += "S" + str(this.GOTOStateDict[entry]) + " "

        processed = {}
        c = 0
        #print(this.extended_grammar_rules)
        for rule in this.extended_grammar_rules:
            tmp_rule = copy.deepcopy(rule)
            if DOT in tmp_rule.RHS:
                tmp_rule.RHS.remove(DOT)
            processed[c] = tmp_rule
            c += 1
        #print(this.extended_grammar_rules[0].RHS)
        added_rule = this.extended_grammar_rules[0].LHS + " -> " + this.extended_grammar_rules[0].RHS[1]
        rules = this.input_grammar.Rules()
        rules.insert(0, added_rule)
        for rule in rules:
            tokens = rule.split()
            lhs = ''
            rhs = ''
            multirhs = []

            for token in tokens:
                if not lhs:
                    lhs = token
                elif token == "->":
                    continue
                elif token == "|":
                    rhs = rhs[:-1]
                    multirhs.append(rhs)
                    rhs = ''
                else:
                    rhs += token + " "
        
            rhs = rhs[:-1]
            multirhs.append(rhs)
            if lhs in this.dict:
                this.dict[lhs] += multirhs
            else:
                this.dict[lhs] = multirhs

        for state_num, rules in this.state_dict.items():
            for rule in rules:
                if rule.RHS[-1] == DOT:
                    tmp_rule = copy.deepcopy(rule)
                    tmp_rule.RHS.remove(DOT)
                    for key, proc in processed.items():
                        if proc == tmp_rule:
                            used = set()
                            follow_res = follow(rule.LHS, used)
                            for col in follow_res:
                                ind = this.cols.index(col)
                                if key == 0:
                                    this.table[state_num][ind] = "acc"
                                else:
                                    this.table[state_num][ind] += "R" + str(key) + " "
    def follow(this,nonTerm, used):
        sol_set = set()
        if non_term == new_start_token:
            sol_set.add(SPEC_TOKEN)
        
        used.add(non_term)

        for cur in this.dict:
            cur_non_term = cur
            rhs = this.dict[cur]
            for sub_rule in rhs:
                while non_term in sub_rule.split():
                    non_term_ind = sub_rule.index(non_term)
                    sub_rule = sub_rule[non_term_ind + 1:]
                    first_res = first(sub_rule, set())
                    if first_res and EPSILON in first_res:
                        first_res.remove(EPSILON)
                        ans_new = follow(cur_non_term, used)
                        first_res.extend(ans_new)
                    else:
                        if non_term != cur_non_term and cur_non_term not in used:
                            first_res = follow(cur_non_term, used)
                    if first_res and first_res[0] != NOTHING:
                        sol_set.update(first_res)

        v = set_to_vect(sol_set)
        return v
    def first(this,rule, used):
        if rule[0] != NOTHING and rule:
            if rule[0] == EPSILON:
                return [EPSILON]
            if rule[0] in this.input_grammar.Terms():
                return [rule[0]]

            if rule[0] in this.dict:
                res = []
                if rule[0] not in used:
                    used.add(rule[0])
                    rhs = this.dict[rule[0]]
                    for sub_rule in rhs:
                        sub_rule_vect = str_to_vect(sub_rule)
                        in_res = first(sub_rule_vect, used)
                        if in_res and in_res[0] != NOTHING:
                            res.extend(in_res)

                if EPSILON not in res:
                    return res

                res.remove(EPSILON)

                if len(res) > 1:
                    sliced = rule[1:]
                    ans_new = first(sliced, used)
                    if ans_new and ans_new[0] != NOTHING:
                        res.extend(ans_new)
                    return res

                res.append(EPSILON)
                return res
        return [NOTHING]

    
    def getKeys(this,map):
        keys = [key for key in map.keys()]
        return keys
    def findCols(this):
        rows = []
        for term in this.input_grammar.Terms():
            rows.append(term)
        rows.append(SPEC_TOKEN)
        for non_term in this.input_grammar.NonTerms():
            rows.append(non_term)

        return rows

    def __init__(this,grammar:Grammar):
        this.input_grammar=grammar
        this.extended_grammar_rules=[]
        this.state_dict=dict()
        this.GOTOStateDict=dict()
        this.table=[];
        this.cols=[];

        this.dict=dict()

        this.newStartToken=""
        this.stateCount=0
        this.processGrammar()
        #print(this.extended_grammar_rules)
        tmp=[]
        I0=this.findClosure(tmp,this.new_start_token)
        this.state_dict[0]=I0
        this.generateStates()
        #print(this.extended_grammar_rules)
        this.createParseTable()
        pass
    pass

LAST_TRACE = -3
NO_TRACE = -3
FULL_TRACE = -1

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
s=SLRTable(Grammar(out.grammar))
s.PrintTable()
parser=LRParser(s)
parser.init(FULL_TRACE)
parser.parse(inp,FULL_TRACE)
print("PARSED SUCCESFULL")

#print(out)
