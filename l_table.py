from automata import checkWord
from types import *
from utils import *
import copy
import random

class LTableAlgorithm:
    def __init__(self, alphabet, oracul, P=100, maxLength=10):
        self.P = P
        self.maxLength = maxLength
        self.checkedWords = []
        self.oracul = oracul
        self.alphabet = alphabet
        self.table = LTable([],[],[],[],[])
        self.initTable()

    def initTable(self):
        S=[""]+self.alphabet
        E=copy.deepcopy(S)
        self.table = LTable(
            S,
            E,
            [[self.oracul(s+e) for e in E] for s in S],
            [],
            []
        )
        self.restructExtended()

    def restructExtended(self):
        self.table.extS.clear()
        for a in self.alphabet:
            self.table.extS += [s+a for s in self.table.S if not any(v != s and v.startswith(s) for v in self.table.S)]
        self.table.extS.sort()
        self.table.extTable = [[self.oracul(s+e) for e in self.table.E] for s in self.table.extS]

    def compute(self):
        logTable(self.table)
        while True:
            while not self.isFull() or not self.isCompatable():
                pass
            res = self.MAT()
            if res["ok"]:
                fs.writeFileSync(config["outputPath"], printAutomata(res["result"]))
                return res["result"]
            log(str(res["ok"]) + ' ' + str(res["result"]))
            word = res["result"]
            for v in range(len(word) + 1):
                s = word[:v]
                if s not in self.table.S:
                    self.table.S.append(s)
                    self.table.table.append([self.oracul(s+e) for e in self.table.E])
            logTable(self.table)

    def isFull(self):
        compareRows = lambda row1, row2: all(v1 == v2 for v1, v2 in zip(row1, row2))
        for i, s in enumerate(self.table.extS):
            found = any(compareRows(row, self.table.extTable[i]) for row in self.table.table)
            if not found:
                self.table.S.append(s)
                self.table.table.append(self.table.extTable[i])
                self.restructExtended()
                return False
        return True
    
    def isCompatable(self):
        compareRows = lambda row1, row2: all(v1 == v2 for v1, v2 in zip(row1, row2))
        for i in range(len(self.table.S)):
            for j in range(i + 1, len(self.table.S)):
                if not compareRows(self.table.table[i], self.table.table[j]):
                    continue
                for a in self.alphabet:
                    try:
                        ii = (self.table.S + self.table.extS).index(f"{self.table.S[i]}{a}")
                        jj = (self.table.S + self.table.extS).index(f"{self.table.S[j]}{a}")
                    except:
                        continue
                    if ii < 0 or jj < 0:
                        continue
                    ##k = next((k for k, (val1, val2) in enumerate(zip(self.table.table[ii], self.table.table[jj])) if val1 != val2), None)
                    k = 0
                    for i in range(len(self.table.E)):
                        val1 = self.table.table[ii][i] if ii < len(self.table.S) else self.table.extTable[ii - len(self.table.S)][i]
                        val2 = self.table.table[jj][i] if jj < len(self.table.S) else self.table.extTable[jj - len(self.table.S)][i]
                        if val1!=val2:
                            k=self.table.E[i]
                            break
                    if k:
                        newSuffix = f"{a}{k}"
                        self.table.E.append(newSuffix)
                        for i, s in enumerate(self.table.S):
                            self.table.table[i].append(self.oracul(f"{s}{newSuffix}"))
                        for i, s in enumerate(self.table.extS):
                            self.table.extTable[i].append(self.oracul(f"{s}{newSuffix}"))
                        return False
        return True

    def buildAutomata(self):
        compareRows = lambda row1, row2: all(v1 == v2 for v1, v2 in zip(row1, row2))
        statesDict = [row for i, row in enumerate(self.table.table) if self.table.table.index(row) == i]
        initState = statesDict.index(self.table.table[self.table.S.index('')])
        if initState == -1:
            return None
        table2=[row for i,row in enumerate(self.table.table) if row[0]]
        table3=[statesDict.index(row) for row in table2]
        final=[ind for i,ind in enumerate(table3) if table3.index(ind) == i]
        automata = Automata(
            len(statesDict),
            
            final,
            initState,
            self.alphabet,
            []
        )

        tmp=[copy.deepcopy(dict.fromkeys(self.alphabet, copy.deepcopy([]))) for _ in statesDict]
        for _ in statesDict:
            automata.map.append({})
            for x in self.alphabet:
                automata.map[-1][x]=[]
        
        def addTransition(fromRow, toRow, a):
            fromState = statesDict.index( fromRow)
            toState = statesDict.index(toRow)
            if toState not in automata.map[fromState][a]:
                automata.map[fromState][a].append(toState)
        
        for i, fromS in enumerate(self.table.S):
            for toS in self.table.S + self.table.extS:
                if len(toS) == len(fromS) + 1 and toS.startswith(fromS):
                    a = toS[-1]
                    addTransition(self.table.table[i],
                                  self.table.table[self.table.S.index(toS)] if toS in self.table.S else self.table.extTable[self.table.extS.index(toS)],
                                  a)

        return automata

    def MAT(self):
        automata = self.buildAutomata()
        if not automata:
            raise ParsingError("Can't build automata")
        
        for i in range(self.P):
            length = 1 + int(1 + (len(self.alphabet) - 1) * random.random())
            word = ''.join(random.choice(self.alphabet) for _ in range(length))
            self.checkedWords.append(word)

            if self.oracul(word) != checkWord(word, automata):
                return {
                    "ok": False,
                    "result": word
                }
        
        self.checkedWords = list(dict.fromkeys(self.checkedWords))
        return {
            "ok": True,
            "result": automata
        }
