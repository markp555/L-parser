from types2 import *

def checkWord(word: str, automata: Automata):
    current_state = automata.init
    for i in range(len(word)):
        symbol = word[i]
        to = automata.map[current_state].get(symbol, [])
        if len(to) == 0:
            return False
        if len(to) > 1:
            raise ParsingError('Automata is not deterministic')
        current_state = to[0]
    return current_state in automata.final
