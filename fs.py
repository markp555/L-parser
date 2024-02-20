def writeFileSync(name,value):
	with open(name,"w") as f:
		f.write(value)

def readFileSync(name):
	with open(name,"r") as f:
		return f.read()

def appendFileSync(name, s):
	with open(name, "a") as f:
		f.write(s)