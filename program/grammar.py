import copy
import sys
import re
import os

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

class ExtendedRule:
    def __init__(self,LHS:str="",RHS:list=[]):
        self.LHS=LHS
        self.RHS=RHS

class Actions:
    def __init__(self,shiftActions=[],reduceActions=[],is_acc=False):
        self.shiftActions=shiftActions
        self.reduceActions=reduceActions
        self.is_acc=is_acc
