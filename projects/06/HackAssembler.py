import sys
import re

#0. defining general symbols and their values for ease of calculation

# dest -> returns the symbolic dest part of the current C-Instruction
dest = {
    '': '000', 'M=': '001', 'D=': '010', 'MD=': '011',
    'A=': '100', 'AM=': '101', 'AD=': '110', 'AMD=': '111'
}

# jump -> returns the symbolic jump part of the C instruction
jump = {
    '': '000', ';JGT': '001', ';JEQ': '010', ';JGE': '011',
    ';JLT': '100', ';JNE': '101', ';JLE': '110', ';JMP': '111'
}

# comp -> returns the symbolic comp part of the current C instruction 
cmp = {
    '0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
    'A': '0110000', 'M': '1110000', '!D': '0001101', '!A': '0110001',
    '!M': '1110001', '-D': '0001111', '-A': '0110011', '-M': '1110011',
    'D+1': '0011111', 'A+1': '0110111', 'M+1': '1110111', 'D-1': '0001110',
    'A-1': '0110010', 'M-1': '1110010', 'D+A': '0000010', 'D+M': '1000010',
    'D-A': '0010011', 'D-M': '1010011', 'A-D': '0000111', 'M-D': '1000111',
    'D&A': '00000000', 'D&M': '1000000', 'D|A': '0010101', 'D|M': '1010101'
}

#common symbols the the assembly files
symbols = {'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576,
         'R0':0,'R1':1,'R1':1,'R2':2,'R3':3,'R4':4,'R5':5,'R6':6,'R7':7,
         'R8':8,'R9':9,'R10':10,'R11':11,'R12':12,'R13':13,'R14':14,'R15':15}

#1. Preparing the lines for processing - AKA "cleaning" them
def cleaner(line):
    """
   "Cleans" the line for optimal processing - aka deletes the following from the line: spaces, new lines and comments.
   May return empty line.
    """

    line = line.replace("\n", "") # removing whitespaces 
    
    if "//" in line:
        line = line[:line.find("//")]

    line = line.strip() #cleaning comments from line   

    return line

# 2. Symbol Table - handling the symbols in the Assembler
def init(input_path):
    """
    Symbol Table 
    param input_path: includes the path of the assembly file  
    initializing and updating the symbol table
    """

    counter_v = 16 #the binary values will be assembled into string of 16 0's and 1's 

    asm_file = open(input_path, 'r')

    lines = asm_file.readlines()

    index = 0

    for line in lines: 
        line = cleaner(line) #preparing the line for processing

        #if the current instruction is (xxx), a label, return the symbol xxx
        if line and "(" in line:
            symbols[line[1:-1]] = index #updating the symbol table 
            index -= 1

        if line:
            index += 1 #upping the index to continue reviewing the lines 

    for line in lines:
        line = cleaner(line)

        # if instruction is @xxx returns the symbol/ decimal xxx as a string
        if line and re.findall(r"@[a-zA-Z]+.*", line):
           
            if line[1:] not in symbols:
                symbols[line[1:]] = counter_v
                counter_v += 1

    asm_file.close()

#3. Parser - reading and parsing the instructions 
def command_parser(input_path, output_path):
   
    output_file = open(output_path, 'a') 

    with open(input_path, 'r') as asm_file:
        lines = asm_file.readlines()
       
        index = 0 

        for line in lines:
            line = cleaner(line) #read current line 
            
            if line:
                
                if "(" in line: #if label is found 
                    line = re.sub(r"\(.+\)", "", line)
                    
                    if not line:
                        continue

                # handling the A instruction
                if line.startswith("@"):
                    
                    #checking if symbol is in symbol table or not, and translating to binary value
                    if line[1:] in symbols.keys():
                        address = symbols[line[1:]] + 32768 
                   
                    else:
                        address = int(line[1:]) + 32768
                   
                    output_file.write('0' + bin(address)[3:] + '\n')

                #handling the C instruction
                else:
                    # parsing the dest value to binary
                    if re.findall(r".+=", line):
                        d = dest[str(re.findall(r".+=", line)[0])]
                    
                    else:
                        d = dest['']

                    # parsing the Jump value to binary
                    if re.findall(r";.+", line):
                        j = jump[str(re.findall(r";.+", line)[0])]
                   
                    else:
                        j = jump['']

                    #handling the comp value in binary
                    c = cmp[re.sub(r'.+=|;.+', '', line)]
                    
                    output_file.write("111" + c + d + j + "\n")

                index += 1

    output_file.close() #when finished going over file 


def main():
    # 1. Defining the Output Path 
    output_path = sys.argv[1].replace(".asm", ".hack")

    # 2. getting input from the command line 
    file_path = sys.argv[1]

    # 3. Initialize the Symbol Table
    init(file_path)

    # 4. Parsing the program
    command_parser(file_path, output_path)


if __name__ == '__main__':
    main()
