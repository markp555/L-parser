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


from lrparser import *

s=SLRTable(Grammar(out.grammar))
s.PrintTable()
parser=LRParser(s)
parser.init(FULL_TRACE)
parser.parse(inp,FULL_TRACE)
print("PARSED SUCCESFULL")

#print(out)
