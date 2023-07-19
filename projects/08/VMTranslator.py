import sys
import os

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

#restore value in the stack
def restore_val():
    return "D=D-A\nA=D\nD=M\n"


"""Step 1: Push Commands """

# Push Local i
def push_local(index, file_name):
    instruction = "@LCL\n"
    instruction += "D=M\n" #load base address

    instruction += get_index_label(index) + "A=A+D\nD=M\n" #loads index and calculates RAM[LCL + i]

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push constant i
def push_constant(index, file_name):
    instruction = get_index_label(index) + "D=A\n" #inserting into label

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

# Push argument i
def push_argument(index, file_name):
    instruction = "@ARG\n" 
    instruction += "D=M\n" #load argument to D
    
    instruction += get_index_label(index) + "A=D+A\nD=M\n" #loads index and calculates RAM[ARG + i]

    instruction += insert_to_stack() #insert to stack
    instruction += increment_sp()

    return instruction

#Push this i
def push_this(index, file_name):
    instruction = get_index_label(index) + "D=A\n" #load this from A

    instruction += "@THIS\n"
    instruction += "A=M+D\nD=M\n" #loads base address of this 

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#Push that i
def push_that(index, file_name):
    instruction = get_index_label(index) + "D=A\n" #load that from A
   
    instruction += "@THAT\n"
    instruction += "A=M+D\nD=M\n" #loads base address of that 

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push temp i
def push_temp(index, file_name):
    instruction = get_index_label(index) + "D=A\n"

    instruction += "@5\n"
    instruction += "A=A+D\nD=M\n" #saving a temporary variable for calculation

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push pointer i
def push_pointer(index, file_name):
    instruction = get_index_label(index) + "D=A\n"

    instruction += "@3\n"
    instruction += "A=A+D\nD=M\n" #save the value as a temporary pointer variable

    instruction += insert_to_stack()
    instruction += increment_sp()

    return instruction

#push static i
def push_static(index, file_name):
    instruction = "@" + file_name + "." + index + "\n" #save to a static label
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
def pop_argument(index, file_name):
    instruction = "@ARG\nD=M\n" #load argument to D

    instruction += get_index_label(index) + "D=D+A\n"

    instruction += "@R13\n"
    instruction += "M=D\n" #saving the argument

    instruction += pop_value_into_A()
    instruction += change_address()
    instruction += decrement_sp()

    return instruction

#pop Local i
def pop_local(index, file_name):
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
def pop_this(index, file_name):
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
def pop_that(index, file_name):
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
def pop_temp(index, file_name):
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
def pop_pointer(index, file_name):
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
def pop_static(index, file_name):
    instruction = pop_one_var()
    instruction += "@" + file_name + "." + index + "\n"
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


"""Part 4  - Label Calls  """

#Label - Marks the destinations of goto commands 
def label(label_name, list_of_functions):
   
   #if label jumps to an external function
   if len(list_of_functions) > 0: 
    function_name = list_of_functions[-1] #extract last function from list

    instruction = "(" + function_name + "$" + label_name + ")\n"  #marking the destination of the goto from the function

   #if the label is in the main file 
   else: 
    instruction = "(" + label_name + ")\n"

   return instruction 

#if_goto: if condition, jump to execute the command after the label
def if_goto(label_name, list_of_functions):
    
    instruction = pop_one_var() #popping the last boolean value from the stack

    #if refering to an external function
    if len(list_of_functions) > 0:
            function_name = list_of_functions[-1] #extract last function from list

            instruction += "@" + function_name + "$" + label_name + "\n"

   #if referring to a goto inside the current file
    else: 
            instruction += "@" + label_name + "\n"

    instruction += "D;JNE\n" #determining whether to jump to to the Label or not 

    return instruction

#Goto:Jump to execute the command just after label
def goto(label_name, function_list):
    
    instruction = ""

    #if referring to an external function
    if len(function_list) > 0:
            function_name = function_list[-1] #extract last function from list

            instruction += "@" + function_name + "$" + label_name + "\n" #creating the label call
   
    else: 
            instruction += "@" + label_name + "\n"

    instruction += "0;JMP\n" #jumping to the command

    return instruction

#A dictionary that holds the functions of label if-goto and goto
label_dict = {
    "label": label,
    "if-goto": if_goto,
    "goto": goto
} 


"""Part 5 - Function Calls """

# Function: starts the declaration of a function that has name functionName and nVars local variables
def function(function_name, nVars):
   
    instruction = "(" + function_name + ")\n" 

    #marking the entry point for each "function_name" commands, as the ammount of variables inserted 
    for num in range(nVars): #for each argument
        
        instruction += "@0\n"
        instruction += "D=A\n" #extracting address

        instruction += insert_to_stack()
        instruction += increment_sp()

    return instruction

#Return: Ends the function declaration
# Indicates that control will be transferred to the command
def returnC():
    #1. reinstating the segment pointers

#gets the address at the frame's end
    instruction = "@LCL\n"
    instruction += "D=M\n" 

    instruction += "@ENDFRAME\n"
    instruction += "M=D\n" #ENDFRAME = LCL

#Gets the return address
    instruction += "@5\n"
    instruction += restore_val() 

    instruction += "@RETURNADDRESS\n"
    instruction += "M=D\n" #returnAddress = *(ENDFRAME - 5)

#Pushes the return value for the caller
    instruction += pop_one_var()

    instruction += "@ARG\n"
    instruction += "A=M\n"
    instruction += "M=D\n" #*ARG = pop()
    
#Reposition SP
    instruction += "@ARG\n"
    instruction += "D=M+1\n"

    instruction += "@SP\n"
    instruction += "M=D\n" #SP = ARG + 1

#Restores THAT
    instruction += "@ENDFRAME\n"
    instruction += "D=M\n"

    instruction += "@1\n"
    instruction += restore_val()

    instruction += "@THAT\n"
    instruction += "M=D\n" # THAT = *(ENDFRAME - 1)

#Restores THIS
    instruction += "@ENDFRAME\n"
    instruction += "D=M\n"

    instruction += "@2\n"
    instruction += restore_val()

    instruction += "@THIS\n"
    instruction += "M=D\n" #THIS = *(ENDFRAME - 2)

#Restores ARG
    instruction += "@ENDFRAME\n"
    instruction += "D=M\n"

    instruction += "@3\n"
    instruction += restore_val()

    instruction += "@ARG\n"
    instruction += "M=D\n" #ARG = *(ENDFRAME - 3)

#Restores LCL
    instruction += "@ENDFRAME\n"
    instruction += "D=M\n"

    instruction += "@4\n"
    instruction += restore_val()

    instruction += "@LCL\n"
    instruction += "M=D\n"  #LCL = *(ENDFRAME - 4)

#Jumping to the return address
    instruction += "@RETURNADDRESS\n" 
    instruction += "A=M\n"
    
    instruction += "0;JMP\n" #goto return Address

    return instruction


def call(function_name, nVars, function_label_index):
    #generates and pushes the label 
        instruction = "@" + function_name + "$ret." + function_label_index + "\n"
        instruction += "D=A\n" #push return address label

        instruction += insert_to_stack()
        instruction += increment_sp()

    #saves the caller's LCL
        instruction += "@LCL\n"
        instruction += "D=M\n" #push LCL

        instruction += insert_to_stack()
        instruction += increment_sp()

    #Saves the caller's ARG
        instruction += "@ARG\n"
        instruction += "D=M\n" #push ARG

        instruction += insert_to_stack()
        instruction += increment_sp()

    #Saves the caller's THIS
        instruction += "@THIS\n"
        instruction += "D=M\n" #push THIS

        instruction += insert_to_stack()
        instruction += increment_sp()

    #Saves the caller's THAT
        instruction += "@THAT\n"
        instruction += "D=M\n" #push THAT

        instruction += insert_to_stack()
        instruction += increment_sp()
    
    #Repositions ARG
        instruction += "D=M\n"

        instruction += "@" + str(5 + nVars) + "\n" 
        instruction += "D=D-A\n" 

        instruction += "@ARG\n"
        instruction += "M=D\n" #ARG = SP - 5 - nVARS

    #Repositions LCL
        instruction += "@SP\n"
        instruction += "D=M\n"

        instruction += "@LCL\n"
        instruction += "M=D\n" #LCL = SP

    #Transfers control to the callee
        instruction += "@" + function_name + "\n"
        instruction += "0;JMP\n" #goto function_name

    #injects the label into this code
        instruction += "(" + function_name + "$ret." + function_label_index + ")\n"

        return instruction


"""Part 6 - Bootstrap Code - Code Conventions"""

def bootstrap_code():
    instruction = ""

# SP=256
    instruction += "@256\n"
    instruction += "D=A\n"

    instruction += "@SP\n"
    instruction += "M=D\n"

# call Sys.init

# pushing the return address
    instruction += "@Bootstrap$ret\n"
    instruction += "D=A\n" #push return address

    instruction += insert_to_stack()
    instruction += increment_sp()

#Push LCL
    instruction += "@LCL\n"
    instruction += "D=M\n" #push LCL

    instruction += insert_to_stack()
    instruction += increment_sp()

# Push ARG
    instruction += "@ARG\n"
    instruction += "D=M\n" #push ARG

    instruction += insert_to_stack()
    instruction += increment_sp()

#Push THIS
    instruction += "@THIS\n"
    instruction += "D=M\n" #push THIS

    instruction += insert_to_stack()
    instruction += increment_sp()

#Push THAT
    instruction += "@THAT\n"
    instruction += "D=M\n" #push THAT

    instruction += insert_to_stack()
    instruction += increment_sp()

#repositions ARG
    instruction += "@SP\n"
    instruction += "D=M\n"

    instruction += "@5\n"
    instruction += "D=D-A\n"

    instruction += "@ARG\n"
    instruction += "M=D\n" #ARG =SP - 5 - nVars

#Repositions LCL
    instruction += "@SP\n"
    instruction += "D=M\n"

    instruction += "@LCL\n"
    instruction += "M=D\n" # LCL = SP

#Transfers control to the callee
    instruction += "@Sys.init\n"
    instruction += "0;JMP\n" #goto function name

#injects the label into this code
    instruction += "(Bootstrap" +"$ret)\n" # (return address)

    return instruction


""" Part 7 - Cleaning and Parsing the Directories from VM to ASM"""

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
def command_parser(input_path, output_path, label_function_data):
   
    output_file = open(output_path, 'a') 

    with open(input_path, 'r') as asm_file:
        
        lines = asm_file.readlines()
        file_name = input_path.split('/')[-1].split('.')[0] #extracting the name of the file after the last / in the directory

        for count, line in enumerate(lines): #going over every line in the file
           
            line = cleaner(line) #read current line 
            
            if line:
                split_code = line.split()
                command = split_code[0] #extracting first commands (either push/pop or arithmetic)
                
                #1. If the command is an Arithmetic command
                if line in arith_logic_commands.keys():
                    output_file.write(arith_logic_commands[line](count))

                    continue
                
                #2. if the command is push
                elif command == "push":
                   segment = line.split()[1] #extracting the segment type 
                   index = line.split()[2] #extracting "i" - an integer that works as an index

                   output_file.write(push_memory_Segments[segment](index, file_name))
                   continue

                #3. if the command is pop
                elif command == "pop":
                    segment = line.split()[1] #extracting the segment type 
                    index = line.split()[2] #extracting "i" - an integer that works as an index

                    output_file.write(pop_memory_Segments[segment](index, file_name))
                    continue

                #4. if the command is label, if_goto, or goto
                elif command in label_dict.keys():
                    label_name = split_code[-1] #extracting the name of the label from the end of the line 

                    output_file.write(label_dict[command](label_name, label_function_data["function_list"]))

                #5. if the command is "function"
                elif command == 'function':
                    function_name = split_code[1] #extracting the function name

                    #inserting the function name to the list of all functions in the file
                    label_function_data["function_list"].append(function_name) 

                    #extracting the ammount of variables in the command line
                    nVars = int(split_code[-1])

                    output_file.write(function(function_name, nVars))

                #6. if the command is "return"
                elif command =='return':
                    output_file.write(returnC())

                #7. if the command is call
                elif command == 'call':
                    function_name = split_code[1] #extracting the filename in the command line

                    nVars = int(split_code[-1]) #extracting ammount of variables

                    output_file.write(call(function_name, nVars, str(label_function_data["function_label_index"])))
                    
                    label_function_data["function_label_index"] += 1 #incrementing the ammount of functions used
                
                #8. for debugging purposes 
                else:
                    print("Unrecognised line in file")

        if len(label_function_data["function_list"]) > 0: 
            label_function_data["function_list"].pop() #removing the last function from the list, following translation
            
    output_file.close() #when finished going over file 

def main():
 if len(sys.argv) == 2:
      
        #A dictionary that holds several variables for ease of use while translating to the Hack language
        label_function_data = {

            #holds the ammount of labels that were named by the user (and not the predefined labels)
            "custom_label_index": 0, 

            #holds the ammount of labels that were named by the user (and not the predefined labels)
            "function_label_index": 0,

            #a list that holds all the calls to external functions in the directory
              "function_list": []
        }

        ## I. if the input is a single file ##
        
        if sys.argv[1].endswith(".vm"):

            # 1. Defining the Output Path 
            file_path = sys.argv[1]

            # 2. Getting the input from the command line 
            output_path = sys.argv[1].replace(".vm", ".asm")

            # 3. Reading the file and translate into asm file 
            command_parser(file_path, output_path, label_function_data)

        ##  II. if the input is a directory with several files ##
        else:
            directory_path = sys.argv[1] #saving the path of the entire directory

            bootstrap = bootstrap_code() #generating the bootstrap code convention

            # Defining the output path of the asm file that will be created 
            output_path = os.path.join(directory_path, directory_path.split("/")[-1] + ".asm")

            for file_name in os.listdir(directory_path):
                
                if file_name.endswith(".vm"): #if the file is a VM file, needs to be translated to ASM

                    # Getting input from the command line
                    file_path = os.path.join(directory_path, file_name)

                    # writing the bootstrap code to the output file
                    with open(output_path, 'a') as out:
                        out.write(bootstrap)
                    
                    #translating the file to ASM
                    command_parser(file_path, output_path, label_function_data)


if __name__ == '__main__':
    main()  