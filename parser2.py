import fs
import re
from types2 import Input, ParsingError
from config import *

REGEX_HEADER = 'regex'
ALPHABET_HEADER = 'alphabet'
MAXLENGTH_HEADER = 'maxlength'

def readInput() -> Input:
    rawData = fs.readFileSync(config["inputPath"])
    data = rawData
    
    currentStage = ''
    regexRaw = None
    maxLength = None
    alphabet = []

    for line in map(str.strip, data.split('\n')):
        if line.lower() in [REGEX_HEADER, ALPHABET_HEADER, MAXLENGTH_HEADER]:
            currentStage = line.lower()
            continue
        if currentStage == REGEX_HEADER:
            regexRaw = line
        elif currentStage == ALPHABET_HEADER:
            alphabet.extend(line.split(' '))
        elif currentStage == MAXLENGTH_HEADER:
            maxLength = int(line)

    if not regexRaw:
        raise ParsingError("You must specify regex")
    regex = re.compile(regexRaw)
    if any(len(v) != 1 for v in alphabet):
        raise ParsingError("Alphabet must contain letters")
    if not maxLength or not isinstance(maxLength, int):
        print("maxLength is not defined and set to default (10)")
        maxLength = 10

    return Input(alphabet=alphabet, regex=regex, maxLength=maxLength)
