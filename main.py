
# Marshmellow Emulator
# A simple 16 bit CPU designed to run Core URCL

# 8x4 character terminal
# 4k of RAM (12 bit program counter)

# 8 registers
#   R0          - Constant 0
#   R1 to R5    - General purpose registers (16 bit)
#   SP          - Stack pointer (physically it is just a normal register like R1 to R5) (16 bit)
#   PC          - Program counter (12 bit)

# Instructions  Unused      Op Code     Op1     Op2     Op3
#          ADD    XXXX          000     CCC     AAA     BBB
#          BGE    XXXX          001     CCC     AAA     BBB
#          NOR    XXXX          010     CCC     AAA     BBB
#          RSH    XXXX          011     CCC     AAA     000
#          LOD    XXXX          100     CCC     AAA     000
#          STR    XXXX          101     000     AAA     BBB
#           IN    XXXX          110     CCC     000     000
#          OUT    XXXX          111     000     AAA     000

# Registers     Index
#        R0       000
#        R1       001
#        R2       010
#        R3       011
#        R4       100
#        R5       101
#        SP       110
#        PC       111

# Note - IMM instructions are not directly supported by the CPU, instead you must load a RAM location which contains the desired immediate value

def fix16bit(x: int) -> int:
    while x >= (2**16):
        x -= (2**16)
    while x < 0:
        x += (2**16)
    return x

def logicalNOR(x: int, y: int) -> int:
    x = bin(x)[2: ]
    while len(x) < 16:
        x = "0" + x
    y = bin(y)[2: ]
    while len(y) < 16:
        y = "0" + y
    answer = ""
    for i in range(16):
        a = x[i]
        b = y[i]
        if (a == "0") and (b == "0"):
            answer += "1"
        else:
            answer += "0"
    answer = int(answer, 2)
    return answer

def charSet() -> tuple:
    return ('0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','_','?','>','<','=','-','+','¦¦','Σ','(',')','/','\\','^','.','‾',',',"'",'¦','≡','!','"','°','\n',' ')

def printChar(a: int, display: list) -> list:
    char = charSet()[a & 63]
    if char == '\n':
        for x in range(8):
            for y in range(4):
                if y == 0:
                    display[x][y] = ' '
                else:
                    display[x][y] = display[x][y - 1]
    else:
        for x in range(7):
            display[x][0] = display[x + 1][0]
        display[7][0] = char
    
    # redraw screen
    drawScreen(display)
    
    return display

def drawScreen(display: list) -> None:
    screen = ""
    for y in range(4):
        for x in range(8):
            screen += display[x][3 - y]
        screen += '\n'
    screen = screen[: -1]
    print("Display:")
    print("-"*8)
    print(screen)
    print("-"*8)

def disassemble(instruction: int) -> str:
    opCodes = {
        0x0000: "ADD",
        0x0200: "BGE",
        0x0400: "NOR",
        0x0600: "RSH",
        0x0800: "LOD",
        0x0A00: "STR",
        0x0C00: "IN" ,
        0x0E00: "OUT"
    }
    registers = {
        0: "R0",
        1: "R1",
        2: "R2",
        3: "R3",
        4: "R4",
        5: "R5",
        6: "SP",
        7: "PC",
    }
    try:
        opCode = instruction & 0xFE00
    except:
        return "INVALID INSTRUCTION EXECUTED"
    
    op1 = (instruction & 0x01C0) >> 6
    op2 = (instruction & 0x0038) >> 3
    op3 = (instruction & 0x0007)
    
    opCode = opCodes[opCode]
    op1 = registers[op1]
    op2 = registers[op2]
    op3 = registers[op3]
    
    match opCode:
        case "ADD" | "BGE" | "NOR":
            return f"{opCode} {op1} {op2} {op3}"
        case "IN":
            return f"{opCode} {op1} %NUMB"
        case "OUT":
            return f"{opCode} %TEXT {op2}"
        case "RSH" | "LOD":
            return f"{opCode} {op1} {op2}"
        case "STR":
            return f"{opCode} {op2} {op3}"
    
ram = [0 for i in range(2**12)]
registers = [0 for i in range(2**3)]
display = [[' ' for y in range(4)] for x in range(8)]

R0 = 0
R1 = 1
R2 = 2
R3 = 3
R4 = 4
R5 = 5
SP = 6
PC = 7

ADD = 0
BGE = 1
NOR = 2
RSH = 3
LOD = 4
STR = 5
IN  = 6
OUT = 7

# initialise RAM with a program
memoryEditor = [
    0x0C40, # IN R1 %NUMB
    0x0C80, # IN R2 %NUMB
    0x0A0A, # STR R1 R2
    0x0200  # BGE R0 R0 R0
]

name = input("Input file name (without .csv extention) or leave blank to run the basic memory editor: ")
if name:
    f = open(name + ".csv", "r")
    startingProgram = eval("[" + f.read() + "]")
    f.close()
else:
    startingProgram = memoryEditor
ram = startingProgram + ram[len(startingProgram): ]

registers[SP] = (2**12) - 1
errorCount = 0
drawScreen(display)

while True:
    # fetch instruction
    instruction = ram[registers[PC]]
    print(disassemble(instruction))

    opCode = (instruction & 0x0E00) >> 9
    op1    = (instruction & 0x01C0) >> 6
    op2    = (instruction & 0x0038) >> 3
    op3    = (instruction & 0x0007)
    
    dontIncrement = False
    
    if opCode == ADD:
        source1        = registers[op2]
        source2        = registers[op3]
        answer         = fix16bit(source1 + source2)
        registers[op1] = answer
        if op1 == PC:
            dontIncrement = True
        
    elif opCode == BGE:
        source1        = registers[op2]
        source2        = registers[op3]
        destination    = registers[op1]
        answer         = (source1 + (((2**16) - 1) - source2) + 1) >= (2**16)
        if answer:
            registers[PC] = destination
            dontIncrement = True
    
    elif opCode == NOR:
        source1        = registers[op2]
        source2        = registers[op3]
        answer         = logicalNOR(source1, source2)
        registers[op1] = answer
        if op1 == PC:
            dontIncrement = True
    
    elif opCode == RSH:
        source1        = registers[op2]
        answer         = source1 >> 1
        registers[op1] = answer
        if op1 == PC:
            dontIncrement = True
    
    elif opCode == LOD:
        address        = registers[op2] & 0x03FF
        registers[op1] = ram[address]
        if op1 == PC:
            dontIncrement = True
    
    elif opCode == STR:
        address        = registers[op2] & 0x03FF
        ram[address]   = registers[op3]
    
    elif opCode == IN:
        while True:
            userInput = input("INPUT: ")
            if userInput.upper() == "SAVE":
                name = input("Input file name to save current RAM state to: ")
                f = open(name + ".csv", "w+")
                f.write(str(ram).replace(" ", "")[1: -1])
                f.close()
                print("Saved RAM state")
                dontIncrement = True
            elif userInput[: 1].isnumeric():
                userInput = int(userInput, 0)
                break
            elif userInput in charSet():
                userInput = charSet().index(userInput)
                break
            else:
                print(f"Invalid input: {userInput}\nOnly 16 bit unsigned numbers or chars in the char set are valid")
        
        if type(userInput) == int:
            registers[op1] = fix16bit(userInput)
            if op1 == PC:
                dontIncrement = True
    
    elif opCode == OUT:
        source1        = registers[op2]
        printChar(source1, display)
    
    else:
        raise Exception("FATAL - Attempted to exectute an unrecognised instruction")

    registers[R0] = 0
    if not dontIncrement:
        registers[PC] += 1
        
    registers[PC] &= 0x03FF


