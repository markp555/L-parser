import fs
from typing import Optional
from types2 import Automata, LTable
from config import *

enter = "\n"
def clearLog():
    fs.writeFileSync(config["logPath"], '')

def logAutomata(automata: Automata, label: Optional[str] = None):
    fs.appendFileSync(config["logPath"], f"AUTOMATA({label if label else ''}):{enter}{printAutomata(automata)}{enter}{enter}")

def logTable(LTable: LTable, label: Optional[str] = None):
    fs.appendFileSync(config["logPath"], f"TABLE({label if label else ''}):{enter}{printTable(LTable)}{enter}")

def log(text: str):
    fs.appendFileSync(config["logPath"], f"{text}{enter}")

def addLeadingSpaces(e: str, count: int) -> str:
    spaces = count - len(e)
    return f"{' ' * spaces}{e}"

def printAutomata(automata: Automata):
    statesLine = f"STATES: {' '.join(map(str, range(automata.states)))}"
    initLine = f"INIT: {automata.init}"
    finalLine = f"FINAL: {' '.join(map(str, automata.final))}"
    alphabetLine = f"ALPHABET: {' '.join(automata.alphabet)}"
    
    columnSizes = [max([len(e[symbol]) if e[symbol] is not None else 1 for symbol in automata.alphabet]) for e in automata.map]
    backslash = "\\"
    header = f"TABLE:{enter}{addLeadingSpaces(backslash, len(str(automata.states - 1)))} | {' | '.join([addLeadingSpaces(e, columnSizes[i]) for i, e in enumerate(automata.alphabet)])}"
    #table = [f"{addLeadingSpaces(str(automata.states - 1), j)} | {' |
    #'.join([addLeadingSpaces(e[symbol].join(',') if e[symbol] is not None else
    #'', columnSizes[i]) for i, symbol in enumerate(automata.alphabet)])}" for
    #j, e in enumerate(automata.map)]
    #table = "TABLE:\n" + " | ".join(["\\"] + automata.alphabet)
    table = [f"{addLeadingSpaces(str(j), len(str(automata.states - 1)))} | {' | '.join([addLeadingSpaces(','.join(map(str,e[c])),columnSizes[i]) for i,c in enumerate(automata.alphabet)])}" for j,e in enumerate(automata.map)]
    
    return f"{statesLine}{enter}{initLine}{enter}{finalLine}{enter}{alphabetLine}{enter}{header}{enter}{'-'*(len(header))}{enter}{enter.join(table)}"

def printTable(table: LTable):
    firstColumnLength = max([len(e) if e else 1 for e in table.S + table.extS])
    columnLengths = [len(e) if e else 1 for e in table.E]
    
    header = f"{addLeadingSpaces(' ', firstColumnLength)} {' '.join([e if e else 'e' for e in table.E])}"
    
    body = [f"{addLeadingSpaces(s if s else 'e', firstColumnLength)} {' '.join([addLeadingSpaces('1' if v else '0', columnLengths[i]) for i, v in enumerate(row)])}" for s, row in zip(table.S, table.table)]
    
    extBody = [f"{addLeadingSpaces(s if s else 'e', firstColumnLength)} {' '.join([addLeadingSpaces('1' if v else '0', columnLengths[i]) for i, v in enumerate(row)])}" for s, row in zip(table.extS, table.extTable)]
    
    return f"{header}{enter}{enter.join(body)}{enter}{'-'*(firstColumnLength + 1 + sum(columnLengths) + len(columnLengths) - 1)}{enter}{enter.join(extBody)}"
