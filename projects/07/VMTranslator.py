import sys

"""0. Helper Functions"""

# Pops one variable from the stack, inserts into D
def pop_one_var():
    return "@SP\nAM=M-1\nD=M\n"

# Pops two variables from the stack, inserts the first into D and second to M
def pop_two_vars():
    return "@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\n"

# inserts variable into the stack
def insert_to_stack():
    return "@SP\nA=M\nM=D\n"

#Pops two variables from the stack
#relevant for the comparison commands: eq, gt, lt
def pop_two_vars_compare():
    return "@SP\nA=M-1\nD=M\nA=A-1\n"

#pushes value back to stack following calculation
#relevant for the comparison commands: eq, gt, lt
def push_bool_to_stack():
    return "@SP\nA=M-1\nA=A-1\nM=D\n"

# creates a label using the index argument
def get_index_label(index):
    return "@" + index + "\n"

#extract value from stack into D (only into A, and not into M)
def pop_value_into_A():
    return "@SP\nA=M-1\nD=M\n"

#updating the address saved in A
def change_address():
    return "@R13\nA=M\nM=D\n" 

# increments the stack pointer in the RAM
def increment_sp():
    return "@SP\nM=M+1\n"
    
#decrements the stack pointer in the RAM
def decrement_sp():
     return "@SP\nM=M-1\n"


"""Step 1: Push Commands """

# Push Local i
def push_local(index):
    instruction = "@LCL\n"
    instruction += "D=M\n" #load base address

    instruction += get_index_label(index) + "A=A+D\nD=M\n" #loads index and calculates RAM[LCL + i]

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push constant i
def push_constant(index):
    instruction = get_index_label(index) + "D=A\n" #inserting into label

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

# Push argument i
def push_argument(index):
    instruction = "@ARG\n" 
    instruction += "D=M\n" #load argument to D
    
    instruction += get_index_label(index) + "A=D+A\nD=M\n" #loads index and calculates RAM[ARG + i]

    instruction += insert_to_stack() #insert to stack
    instruction += increment_sp()

    return instruction

#Push this i
def push_this(index):
    instruction = get_index_label(index) + "D=A\n" #load this from A

    instruction += "@THIS\n"
    instruction += "A=M+D\nD=M\n" #loads base address of this 

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#Push that i
def push_that(index):
    instruction = get_index_label(index) + "D=A\n" #load that from A
   
    instruction += "@THAT\n"
    instruction += "A=M+D\nD=M\n" #loads base address of that 

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction


#push temp i
def push_temp(index):
    instruction = get_index_label(index) + "D=A\n"

    instruction += "@5\n"
    instruction += "A=A+D\nD=M\n" #saving a temporary variable for calculation

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push pointer i
def push_pointer(index):
    instruction = get_index_label(index) + "D=A\n"

    instruction += "@3\n"
    instruction += "A=A+D\nD=M\n" #save the value as a temporary pointer variable

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push static i
def push_static(index):
    instruction = "@LABEL." + index + "\n" #save to a static label
    instruction += "D=M\n"

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#dictionary that represents the push functions in the VM
push_memory_Segments = { 
    "local": push_local,
    "argument": push_argument,
    "this": push_this,
    "that": push_that,
    "constant": push_constant,
    "static": push_static,
    "temp": push_temp,
    "pointer": push_pointer
}

"""Step 2: Pop Commands """

#pop argument i
def pop_argument(index):
    instruction = "@ARG\nD=M\n" #load argument to D

    instruction += get_index_label(index) + "D=D+A\n"

    instruction += "@R13\n"
    instruction += "M=D\n" #saving the argument

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop Local i
def pop_local(index):
    instruction = get_index_label(index) + "D=A\n" #loads index 

    instruction += "@LCL\n"
    instruction += "D=M+D\n" #load base address RAM[LCL + i]

    instruction += "@R13\n"
    instruction += "M=D\n" #saving the value

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop this i
def pop_this(index):
    instruction = get_index_label(index) + "D=A\n" #load this from D

    instruction += "@THIS\n"
    instruction += "D=M+D\n" #loads base address of this 

    instruction += "@R13\n"
    instruction += "M=D\n" #saving the value

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop that i
def pop_that(index):
    instruction = get_index_label(index) + "D=A\n" #load that from D

    instruction += "@THAT\n"
    instruction += "D=M+D\n" #loads base address of that 

    instruction += "@R13\n"
    instruction += "M=D\n"

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop temp i
def pop_temp(index):
    instruction = get_index_label(index) + "D=A\n"

    instruction += "@5\n"
    instruction += "D=A+D\n" #saving the variable

    instruction += "@R13\n"
    instruction += "M=D\n"

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop pointer i
def pop_pointer(index):
    instruction = get_index_label(index) + "D=A\n"

    instruction += "@3\n"
    instruction += "D=A+D\n" #saving the vairiable

    instruction += "@R13\n"
    instruction += "M=D\n"

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop static i
def pop_static(index):
    instruction = pop_one_var()
    instruction += "@LABEL." + index + "\n"
    instruction += "M=D\n" #inserting the variable into the static label

    return instruction

#dictionary that represents the pop functions in the VM
pop_memory_Segments = { 
    "local": pop_local,
    "argument": pop_argument,
    "this": pop_this,
    "that": pop_that,
    "static": pop_static,
    "temp": pop_temp,
    "pointer": pop_pointer
}

""" Step 2. Arithmetic Logic Operators """

#1. Addition: pops two values from the stack and adds them: x + y 
def add(count):
    instruction = pop_two_vars()

    instruction += "M=D+M\n" #adding x and y values

    instruction += increment_sp() #adding the sum to the stack

    return instruction
    
#     x = stack.pop()
#     y = stack.pop()
#     stack.append(x + y)


#Subtraction: pops two values from stack and subtracts them x - y
def sub(count):
   instruction = pop_two_vars()

   instruction += "M=M-D\n" #subtracting x and y

   instruction += increment_sp() #adding the remainder to the stack

   return instruction

    # y = stack.pop()
    # x = stack.pop()
    # stack.append( x - y)

#Negative: pops a value from the stack and negates it: -y
def neg(count):
    instruction = pop_one_var()

    instruction += "M=-M\n" #negating  the value

    instruction += increment_sp() #Adding negated value to stack

    return instruction

    # y = stack.pop()
    # stack.append(-y)

#Equals : pops two variables from the stack and checks if  x == y
def eq(count):
    instruction = pop_two_vars_compare()
    instruction += "D=D-M\n" #calculatng the remainder between D and M

    instruction += "@EQUALS" + str(count) + "\n" #if the value is 0
    instruction += "D;JEQ\n"

    instruction += "@NOTEQUAL" + str(count) + "\n" 
    instruction += "0;JMP\n"

    instruction += "(EQUALS" + str(count) + ")\n"
    instruction += "D=-1\n" #if equal, set D to -1 for insertion to stack

    instruction += "@EQEND" + str(count) + "\n"
    instruction += "0;JMP\n"

    instruction += "(NOTEQUAL" + str(count) + ")\n"
    instruction += "D=0\n" #if not equal, set D as 0 for instertion to stack

    instruction += "@EQEND" + str(count) + "\n"
    instruction += "0;JMP\n"

    instruction += "(EQEND" + str(count) + ")\n"

    instruction += push_bool_to_stack()
    instruction += decrement_sp()

    return instruction

    # x = stack.pop()
    # y = stack.pop()
    # stack.append(x == y)

#Greater Than:pops two variables from the stac and checks if  x > y
def gt(count):
    instruction = pop_two_vars_compare()
    instruction += "D=M-D\n" #checking what the value of the remainder

    instruction += "@GREATERTHAN" + str(count) + "\n" #if x is greater than y
    instruction += "D;JGT\n" 

    instruction += "@LESSTHAN" + str(count) + "\n" #if x is smaller than y
    instruction += "0;JMP\n"

    instruction += "(GREATERTHAN" + str(count) + ")\n"
    instruction += "D=-1\n" #if it is greater than set D for insertion to stack

    instruction += "@GTEND" + str(count) + "\n"
    instruction += "0;JMP\n"

    instruction += "(LESSTHAN" + str(count) + ")\n"
    instruction += "D=0\n" #else, set D for insertion to stack as 0

    instruction += "@GTEND" + str(count) + "\n"
    instruction += "0;JMP\n"

    instruction += "(GTEND" + str(count) + ")\n"

    instruction += push_bool_to_stack()
    instruction += decrement_sp()

    return instruction

    # x = stack.pop()
    # y = stack.pop()
    # stack.append( y > x)

#Less Than:pops two variables from the stac and checks if x < y
def lt(count):
    instruction = pop_two_vars_compare()
    instruction += "D=M-D\n"

    instruction += "@LESS" + str(count) + "\n" #if the value is less than M
    instruction += "D;JLT\n"

    instruction += "@GREATER" + str(count) + "\n" #else - it's not less than
    instruction += "0;JMP\n"

    instruction += "(LESS" + str(count) + ")\n"
    instruction += "D=-1\n" #output to return into the stack

    instruction += "@LTEND" + str(count) + "\n"
    instruction += "0;JMP\n" 

    instruction += "(GREATER" + str(count) + ")\n"
    instruction += "D=0\n" #if the value isn't less than

    instruction += "@LTEND" + str(count) + "\n"
    instruction += "0;JMP\n"

    instruction += "(LTEND" + str(count) + ")\n"

    instruction += push_bool_to_stack()
    instruction += decrement_sp()

    return instruction

    # x = stack.pop()
    # y = stack.pop()
    # stack.append( y < x)

#And: pops two values from the stack and returns to the stack: x & y
def andC(count):
    instruction = pop_two_vars()

    instruction += "M=M&D\n" #checking x&y

    instruction += increment_sp() #adding bool value to stack

    return instruction

    # x = stack.pop()
    # y = stack.pop()
    # stack.append( x & y)

#Or: pops two values from the stack and returns to the stack: x & y
def orC(count):
    instruction = pop_two_vars()

    instruction += "M=M|D\n" #checking if x|y

    instruction += increment_sp() #adding bool value to stack

    return instruction

    # x = stack.pop()
    # y = stack.pop()
    # stack.append( y | x)

#Not: pops a value from the stack and returns it's boolean not value: !x
def notC(count):
    instruction = pop_one_var()

    instruction += "M=!M\n" #changing the value of M to it's Not value

    instruction += increment_sp() #adding bool value into stack

    return instruction
    
    # x = stack.pop()
    # stack.append(not x)

#dictionary that represents the arithmetic and logic operators in the VM
arith_logic_commands = {
    "add": add,
    "sub": sub,
    "neg": neg,
    "not": notC,
    "or": orC,
    "and": andC,
    "eq": eq,
    "gt": gt,
    "lt": lt
}

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

#3. Parser - reads a VM file and translates to the hack machine language based on the command type.
# outputs the contents to an ASM file 
def command_parser(input_path, output_path):
   
    output_file = open(output_path, 'a') 

    with open(input_path, 'r') as asm_file:
        lines = asm_file.readlines()
     
        for count, line in enumerate(lines):
           
            line = cleaner(line) #read current line 
            
            if line:
                
                command = line.split()[0] #extracting first commands (either push/pop or arithmetic)
                
                #1. If the command is an Arithmetic command
                if line in arith_logic_commands.keys():
                    output_file.write(arith_logic_commands[line](count))

                    continue
                
                #2. if the command is push
                elif command == "push":
                   segment = line.split()[1] #extracting the segment type 
                   index = line.split()[2] #extracting "i" - an integer that works as an index

                   output_file.write(push_memory_Segments[segment](index))
                   continue

                #3. if the command is pop
                elif command == "pop":
                    segment = line.split()[1] #extracting the segment type 
                    index = line.split()[2] #extracting "i" - an integer that works as an index

                    output_file.write(pop_memory_Segments[segment](index))
                    continue

                print("Unrecognised line in file")
            
    output_file.close() #when finished going over file 

def main():
    # 1. Defining the Output Path 
    output_path = sys.argv[1].replace(".vm", ".asm")

    # 2. Getting the input from the command line 
    file_path = sys.argv[1]

    # 3. Reading the file and translate into asm file 
    command_parser(file_path, output_path)


if __name__ == '__main__':
    main()

    