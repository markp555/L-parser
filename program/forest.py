# FOREST.H

import copy
import sys
import re
import os

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
