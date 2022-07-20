
# import .urcl file

# clean code + tokenise
    # add a spacebar before and after [ and ]
    # replace multiple spacebars with a single ones
    # remove all multiline commments
    # split lines
    # remove all line comments
    # remove empty lines and lines with a single spacebar
    # remove spacebars the the start/end of lines
    # tokenise each line by spliting using spacebar
    # find and resolve macros
    # convert relatives to labels
    # turn DW arrays into single DW values
    # convert chars to immediate values
    # convert IMM into a DW value

# translate
    # use dictionary to translate opcode and operands
    # add the results together to create the final instruction
    # create list of final instructions

# save the list of instructions as .csv

###############################################################

# import .urcl file

def charSet() -> tuple:
    return ('0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','_','?','>','<','=','-','+','¦¦','Σ','(',')','/','\\','^','.','‾',',',"'",'¦','≡','!','"','°','\n',' ')

f = open(input("Type name of URCL file with the file extention: "), "r")
code = f.read()
f.close()

# clean code + tokenise
    # add a spacebar before and after [ and ]
code = code.replace("[", " [ ")
code = code.replace("]", " ] ")

    # replace multiple spacebars with a single ones
while code.find("  ") != -1:
    code = code.replace("  ", " ")
    
    # remove all multiline commments
while code.find("/*") != -1:
    code = code[: code.index("/*")] + code[code.index("*/") + 2: ]
    
    # split lines
code = code.splitlines()
    
    # remove all line comments
for lineNumber in range(len(code)):
    if code[lineNumber].find("//") != -1:
        code[lineNumber] = code[lineNumber][: code[lineNumber].index("//")]
    
    # remove empty lines and lines with a single spacebar
lineNumber = 0
while lineNumber < len(code):
    if (not(code[lineNumber])) or (code[lineNumber] == " "):
        code.pop(lineNumber)
    else:
        lineNumber += 1
    
    # remove spacebars the the start/end of lines
for lineNumber in range(len(code)):
    if code[lineNumber].startswith(" "):
        code[lineNumber] = code[lineNumber][1: ]
    if code[lineNumber].endswith(" "):
        code[lineNumber] = code[lineNumber][: -1]
    
    # tokenise each line by spliting using spacebar
for lineNumber in range(len(code)):
    code[lineNumber] = code[lineNumber].split(" ")
    
    # find and resolve macros
lineNumber = 0
while lineNumber < len(code):
    if code[lineNumber][0] == "@DEFINE":
        key = "@" + code[lineNumber][1]
        definition = code[lineNumber][2]
        for lineNumber2 in range(len(code)):
            for tokenNumber in range(len(code[lineNumber2])):
                if code[lineNumber2][tokenNumber] == key:
                    code[lineNumber2][tokenNumber] = definition
        code.pop(lineNumber)
    else:
        lineNumber += 1
    
    # find and resolve @ORG
org = 0
for lineNumber in range(len(code)):
    if code[lineNumber][0] == "@ORG":
        org = int(code[lineNumber][1], 0)
        code.pop(lineNumber)
        break

    # convert relatives to labels
lineNumber = 0
while lineNumber < len(code):
    for tokenNumber in range(len(code[lineNumber])):
        if code[lineNumber][tokenNumber].startswith("~"):
            relative = int(code[lineNumber][tokenNumber][1: ], 0)
            lineNumber2 = relative + lineNumber
            code.insert(lineNumber2, [f".relativeLabel_{lineNumber2}"])
            code[lineNumber][tokenNumber] = f".relativeLabel_{lineNumber2}"
            if relative <= 0:
                lineNumber += 1
    lineNumber += 1
    
    # turn DW arrays into single DW values
lineNumber = 0
while lineNumber < len(code):
    if code[lineNumber][0] == "DW":
        if code[lineNumber][1] == "[":
            array = []
            for tokenNumber in range(len(code[lineNumber] - 3)):
                array.append(code[lineNumber][tokenNumber + 2])
            for DWValue in range(len(array)):
                code.insert(lineNumber, array[DWValue])
                lineNumber += 1
            code.pop(lineNumber)
        else:
            lineNumber += 1
    else:
        lineNumber += 1
    
    # convert chars to immediate values
for lineNumber in range(len(code)):
    for tokenNumber in range(len(code[lineNumber])):
        if code[lineNumber][tokenNumber].startswith("'"):
            char = code[lineNumber][tokenNumber][1: -1]
            code[lineNumber][tokenNumber] = charSet().index(char)
    
    # convert IMM into a DW value
lineNumber = 0
while lineNumber < len(code):
    if code[lineNumber][0] == "IMM":
        register = code[lineNumber][1]
        immediate = code[lineNumber][2]
        translation = [
            ["ADD", register, "PC", "R5"],
            ["ADD", "PC", "PC", "R5"],
            ["DW", immediate],
            ["LOD", register, register]
        ]
        code = code[: lineNumber] + translation + code[lineNumber + 1: ]
    else:
        lineNumber += 1

    # get rid of headers
lineNumber = 0
while lineNumber < len(code):
    if code[lineNumber][0] in ("BITS", "MINREG", "MINHEAP", "MINSTACK", "RUN"):
        code.pop(lineNumber)
    else:
        lineNumber += 1

    # prepend code to setup R5 as a constant value of 2
code = [
    ["NOR", "R5", "R0", "R0"],
    ["NOR", "R4", "R0", "R0"],
    ["ADD", "R5", "R4", "R5"],
    ["ADD", "R5", "R4", "R5"],
    ["NOR", "R5", "R5", "R0"]
    ] + code

    # convert labels into literals
lineNumber = 0
while lineNumber < len(code):
    if code[lineNumber][0].startswith("."):
        label = code[lineNumber][0]
        value = str(lineNumber)
        for lineNumber2 in range(len(code)):
            for tokenNumber in range(len(code[lineNumber2])):
                if code[lineNumber2][tokenNumber] == label:
                    code[lineNumber2][tokenNumber] = value
        code.pop(lineNumber)
    else:
        lineNumber += 1

# translate
    # use dictionary to translate opcode and operands
opCodes = {
    "ADD": 0x0000,
    "BGE": 0x0200,
    "NOR": 0x0400,
    "RSH": 0x0600,
    "LOD": 0x0800,
    "STR": 0x0A00,
    "IN" : 0x0C00,
    "OUT": 0x0E00
}
registers = {
    "R0": 0,
    "R1": 1,
    "R2": 2,
    "R3": 3,
    "R4": 4,
    "R5": 5,
    "SP": 6,
    "PC": 7,
}
ram = []

for line in code:
    if line[0] == "DW":
        instruction = int(line[1], 0)
    else:
        opCode = opCodes[line[0]]
        
        match line[0]:
            case "ADD" | "BGE" | "NOR":
                op1 = registers[line[1]] << 6
                op2 = registers[line[2]] << 3
                op3 = registers[line[3]]
            case "IN":
                op1 = registers[line[1]] << 6
                op2 = 0
                op3 = 0
            case "OUT":
                op1 = 0
                op2 = registers[line[2]] << 3
                op3 = 0
            case "RSH" | "LOD":
                op1 = registers[line[1]] << 6
                op2 = registers[line[2]] << 3
                op3 = 0
            case "STR":
                op1 = 0
                op2 = registers[line[1]] << 3
                op3 = registers[line[2]]
            case _:
                raise Exception(f"FATAL - Unrecognised core URCL instruction: {line[0]}")
            
        # add the results together to create the final instruction
        instruction = opCode + op1 + op2 + op3
    
    # create list of final instructions
    ram.append(instruction)

# save the list of instructions as .csv
ram = str(ram).replace(" ", "")[1: -1]
f = open(input("Input save file name: ") + ".csv", "w+")
f.write(ram)
f.close()
