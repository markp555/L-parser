from config import config
import fs
from l_table import LTableAlgorithm
from parser2 import *
from types2 import Automata, ParsingError
from utils import clearLog, logAutomata, printAutomata

def main():
    input = readInput()
    oracul = lambda word: input.regex.match(word) is not None
    l = LTableAlgorithm(input.alphabet, oracul, config["P"], input.maxLength)
    automata = l.compute()
    logAutomata(automata)
    printResults(automata)

def printResults(automata):
    fs.writeFileSync(config["outputPath"], printAutomata(automata))

try:
    clearLog()
    main()
except Exception as e:
    if isinstance(e, ParsingError):
        print(e)
    else:
        raise e
