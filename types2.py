
from typing import List, Dict, Union

class Input:
    def __init__(self, regex: str, alphabet: List[str], maxLength: int):
        self.regex = regex
        self.alphabet = alphabet
        self.maxLength = maxLength

class LTable:
    def __init__(self, S: List[str], E: List[str], table: List[List[bool]], extS: List[str], extTable: List[List[bool]]):
        self.S = S
        self.E = E
        self.table = table
        self.extS = extS
        self.extTable = extTable

class MATResult:
    def __init__(self, ok: bool, result: Union[str, "Automata"]):
        self.ok = ok
        self.result = result

class Automata:
    def __init__(self, states: int, final: List[int], init: int, alphabet: List[str], map: List[Dict[str, List[int]]]):
        self.states = states
        self.final = final
        self.init = init
        self.alphabet = alphabet
        self.map = map

class ParsingError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

