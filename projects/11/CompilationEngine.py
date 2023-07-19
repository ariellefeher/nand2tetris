from SymbolTable import SymbolTable
from VMWriter import VMWriter

#  list of all the symbol characters
symbol_list = [
    "{", "}", "(", ")", "[", "]", ".", ",", ";", "+",
    "-", "*", "/", "&", "|", "<", ">", "=", "~"
]

#  list of all the subroutine declarations
subroutine_dec = {"constructor", "function", "method"}

#  dictionary of all the VM operation commands
operation_dict = {
    '+': "add",
    '*': "call Math.multiply 2",
    '>': "gt",
    '=': "eq",
    '&': "and",
    '|': "or",
    '-': "sub",
    '<': "lt",
    '/': "call Math.divide 2",
}


class CompilationEngine:
    """
    the main module of the syntax analyzer that generates the Compiler's Output

    Consists of a set of compile xxx methods,
    One for each grammar rule xxx
    """

    vm_writer: VMWriter

    def __init__(self, tokenizer, output_file):
        """
        Creates a new compilation engine with the given input and output.
        """

        self.tab_counter = 0  # counts the amount of tabs needed to write the tags

        self.need_new_line = False  # checking if needed a new line, for aesthetic purposes

        self.output_file = output_file  # the .VM file we will write the output into

        self.token = tokenizer  # the JackTokenizer received as an input

        self.vm_writer = VMWriter(output_file)

    #  Initialize a new Symbol Table
        self.symbol_table = SymbolTable()

        self.class_name = ""

        self.if_counter = 0

        self.loop_counter = 0

        # 1. extract the first token
        self.token.advance()

        if self.token.token_type() != "keyword" or self.token.keyWord() != "class":
            raise CompilerError(self, "file doesn't start with a class")

        # The next routine called (by the JackAnalyzer module) must be compileClass() .
        self.compileClass()

    def compileClass(self):
        """
        Compiles a complete class.
        """

        # 1. Adding the relevant tag
        self.token.advance()

        # 2.  compiling the class name
        if self.token.token_type() != "identifier":
            raise CompilerError(self, "The class doesn't start with a name!")

        # Writing the tag into the output file and advancing the pointer of the token
        self.class_name = self.token.identifier()
        self.token.advance()

        self.check_if_symbol("{", "The class doesn't start with {")

        # 4. compiling the Class Body

        # 4.1 checking if there are variable declarations (if static or field), and calling ClassVarDec
        while self.token.token_type() == "keyword" and self.token.keyWord() in {'static', 'field'}:
            self.compileClassVarDec()

        # 4.2 checking if there are subroutine declarations, and compile subroutineDec
        while self.token.token_type() == "keyword" and self.token.keyWord() in {'constructor', 'function', 'method'}:
            self.compileSubroutine()

        # 4. Compiling the closing bracket: }
        self.check_if_symbol("}", "Class must contain only variable declarations and then subroutine declarations")

    def compileClassVarDec(self):
        """
        Compiles a static declaration, or a field declaration.
        variable declaration is of the following syntax:
        ( 'static' | 'field' ) type varName ( ',' varName)* ';'
        """

        # 1. extracting the token's keyword
        kind = self.token.keyWord()
        self.token.advance()

        # 2. extracting the variable type
        if self.token.token_type() == "keyword":
            var_type = self.token.keyWord()

        else:
            var_type = self.token.identifier()

        # 3. extracting the varName
        self.token.advance()
        name = self.token.identifier()

        # 4. declaring the variable in the symbol table
        self.token.advance()
        self.declare_var_in_symbol_table(name, var_type, kind)

        # 5. compiling the varname , also checking if there is a comma
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()
            name = self.token.identifier()

            self.token.advance()

            # adding the variable to the symbol table
            self.declare_var_in_symbol_table(name, var_type, kind)

        self.check_if_symbol(";", "missing ;")

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
            Subroutine is of the following syntax:
             ( 'constructor' | 'function' | 'method' )
            ( 'void' | type) subroutineName '(' parameterList ')'
             subroutineBody
        """

        # 1. resetting the symbol table for the subroutine
        self.symbol_table.reset()

        # 2. compiling the constructor / functon / method keyword
        subroutine_type = self.token.keyWord()

        # assuming the subroutine is a function
        is_constructor = False
        is_method = False

        #  checking if subroutine is a constructor
        if subroutine_type == "constructor":
            is_constructor = True

        #  checking if subroutine is a method
        elif subroutine_type == "method":
            self.declare_var_in_symbol_table("this", self.class_name, "arg")
            is_method = True

        self.token.advance()

        # 3. compiling the subroutineName
        self.token.advance()
        name = self.token.identifier()

        # 4. checking if the function has a .
        if self.token.token_type() == "symbol" and self.token.symbol() == ".":
            self.token.advance()

            name = name + "." + self.token.identifier()

        else:
            self.token.advance()
            name = self.class_name + "." + name

        # 5. compiling the opening bracket (
        self.check_if_symbol("(", "expected /")

        # 6. compiling the parameterList
        self.compileParameterList()

        # 7. compiling the closing bracket
        self.check_if_symbol(")", " expected )  ")

        # 8. compiling the subroutineBody
        self.compileSubroutineBody(name, is_constructor, is_method)

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list.
        Does not handle the enclosing parentheses tokens (and)

        is of the following syntax: ( (type varName) ( ',' type varName)*)?
        """

        # checking if the parameter list is empty
        if self.token.token_type() == "symbol" and self.token.symbol() == ")":
            return None

        # 3. compiling type
        if self.token.token_type() == "keyword":
            var_type = self.token.keyWord()
        else:
            var_type = self.token.identifier()

        # 4. compiling varName
        self.token.advance()
        name = self.token.identifier()

        # 5. compiling the type and the varName for each element in the parameter list

        # compiling the first parameter
        self.token.advance()
        self.declare_var_in_symbol_table(name, var_type, "arg")

        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()

            # 5.1 compiling the type
            if self.token.token_type() == "keyword":
                var_type = self.token.keyWord()

            else:
                var_type = self.token.identifier()

            # 5.2 compiling VarName
            self.token.advance()
            name = self.token.identifier()

            self.token.advance()
            self.declare_var_in_symbol_table(name, var_type, "arg")

    def compileSubroutineBody(self, name, is_constructor, is_method):
        """
        compiles a subroutine's body
        is of the syntax :'{' varDec* statements '}'
        """

        # 1. compiling the opening curly bracket {
        self.check_if_symbol("{", "Expected { ")

        num_locals = 0  # local counter

        # 3. compiling the variable declaration
        while self.token.token_type() == "keyword" and self.token.keyWord() == "var":
            num_locals += self.compileVarDec()

        # 4. compile the function declaration
        self.write_function(name, num_locals)

        # 4.1 adding memory allocation if the function is a constructor
        if is_constructor:
            self.write("push constant " + str(self.symbol_table.fieldCount) + "\n")

            self.write("call Memory.alloc 1\n")

            self.write("pop pointer 0\n")

        #  4.2 adding a pointer if the function is a method
        elif is_method:
            self.write("push argument 0\n")

            self.write("pop pointer 0\n")

        # 5. compiling the statements
        self.compileStatements()

        # 6. compiling the closing curly bracket
        self.check_if_symbol("}", "missing }")

    def compileVarDec(self):
        """
        Compiles a var declaration.
        Is of the syntax: 'var' type varName ( ',' varName)* ';'
        """

        var_counter = 0  # counter for the amount of variables in the declaration

        # 1. compiling the variable
        if self.token.token_type() != "keyword" and self.token.keyWord() != "var":
            raise CompilerError(self, "missing variable in the declaration")

        self.token.advance()

        # 2. compiling the type
        if self.token.token_type() == "keyword":
            var_type = self.token.keyWord()

        else:  # if the token is an identifier
            var_type = self.token.identifier()

        self.token.advance()

        # 3. compiling the variable name
        name = self.token.identifier()
        self.token.advance()

        # 4. declaring the variable in the symbol table
        self.declare_var_in_symbol_table(name, var_type, "var")
        var_counter += 1

        # 5. compiling the  additional variable names
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()
            name = self.token.identifier()

            self.token.advance()

            #  adding to symbol table
            self.declare_var_in_symbol_table(name, var_type, "var")

            var_counter += 1

        # 6. compiling the semicolon';'
        self.check_if_symbol(";", "missing semicolon ;")

        return var_counter

    def compileStatements(self):
        """
            Compiles a sequence of statements.
             Does not handle the enclosing curly bracket tokens {and}.
             is of the syntax :  statement*  0 or more times
        """

        # 1. checking the type of statement in order to compile
        while self.token.token_type() == "keyword" and self.token.keyWord() in {"let", "if", "while", "do", "return"}:
            statement_type = self.token.keyWord()

            if statement_type == "let":
                self.compileLet()

            elif statement_type == "if":
                self.compileIf()

            elif statement_type == "while":
                self.compileWhile()

            elif statement_type == "do":
                self.compileDo()

            elif statement_type == "return":
                self.compileReturn()

    def compileLet(self):
        """
         Compiles a let statement.
         is of the syntax : # 'let' varName ( '[' expression ']' )? '=' expression ';'
         """

        # 1. compiling the let
        self.token.advance()

        # 2. compiling the variable name
        var_name = self.token.identifier()
        self.token.advance()

        # 3. checking if there is an expression
        if self.token.token_type() == "symbol" and self.token.symbol() == "[":
            self.write_push(var_name)

            # 3.2 compiling the expression in the square bracket
            self.token.advance()
            self.compileExpression()

            # 3.3. checking if closed expression with bracket
            self.check_if_symbol("]", "missing closing bracket")

            # 4. compiling the equals =
            self.check_if_symbol("=", "missing variable assignment")
            self.compileExpression()

            # updating the stack
            self.write("pop temp 1\n")
            self.write("add\n")
            self.write("pop pointer 1\n")
            self.write("push temp 1\n")
            self.write("pop that 0\n")

        else:  # if there is no equals sign in the expression
            self.check_if_symbol("=", "expected in assignment")

            self.compileExpression()
            self.write_pop(var_name)  # removing from stack

        # compiling the semicolon ;
        self.check_if_symbol(";", "missing ;")

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else clause.
        is of the syntax: 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        """

        # 1. compiling the if keyword
        self.token.advance()

        # 2. compiling the (expression)
        self.check_if_symbol("(", "missing ( for if statement")

        self.compileExpression()

        self.check_if_symbol(")", "missing ) for if statement")

        self.vm_writer.write_arithmetic("not")

        # 3. writing the amount of "if" statements
        count_if = self.if_counter
        self.if_counter += 1

        self.vm_writer.write_if("ifElse" + str(count_if))

        #  4. compiling the {statements}
        self.check_if_symbol("{", "missing { for if statement")

        self.compileStatements()

        self.check_if_symbol("}", "missing } for if statement")

        # writing the goto and labels
        self.vm_writer.write_goto("ifEnd" + str(count_if))
        self.vm_writer.write_label("ifElse" + str(count_if))

        # 5. compiling the else statement
        if self.token.token_type() == "keyword" and self.token.keyWord() == "else":

            # 5.1 compiling the else keyword
            self.token.advance()

            # 5.2 compiling the {statements}
            self.check_if_symbol("{", "missing { in else statement")

            self.compileStatements()

            self.check_if_symbol("}", "missing } in else statement")

        # 6. adding end labels
        self.vm_writer.write_label("ifEnd" + str(count_if))

    def compileWhile(self):
        """
        Compiles a while statement.
        is of the syntax : 'while' '(' expression ')' '{' statements '}'
        """

        #  counts the amount of loops
        count_loops = str(self.loop_counter)
        self.loop_counter += 1

        #  1. adding the starting label
        self.vm_writer.write_label("whileStart" + count_loops)

        # 2. compiling the while keyword
        self.token.advance()

        # 3. compiling the (expression)
        self.check_if_symbol("(", "missing ( for while expression")

        self.compileExpression()

        self.check_if_symbol(")", "missing ) for while expression")

        # 3.1 if there's not an expression
        self.vm_writer.write_arithmetic("not")

        self.vm_writer.write_if("whileEnd" + count_loops)  # adding goto end for the label

        # 4. compiling the { statements }
        self.check_if_symbol("{", "missing { for while expression")

        self.compileStatements()

        self.check_if_symbol("}", "missing } for while expression")

        #  5. adding goto and ending labels
        self.vm_writer.write_goto("whileStart" + count_loops)
        self.vm_writer.write_label("whileEnd" + count_loops)

    def compileDo(self):
        """
        Compiles a do statement.
        is of the syntax: 'do' subroutineCall ';'
        """

        # 1. compiling the do keyword
        self.token.advance()

        # 2. compiling the subroutineCall
        self.compile_subroutine_call()

        # 3. popping the following from the stack
        self.write("pop temp 0\n")

        # 4. compiling the semicolon ;
        self.check_if_symbol(";", "missing ;")

    def compileReturn(self):
        """
        Compiles a return statement.
        is of the syntax: 'return' expression? ';'
        """

        # 1. compiling the return keyword
        self.token.advance()

        # 2. checking if there is an expression
        if self.token.token_type() != "symbol" or self.token.symbol() != ";":
            self.compileExpression()

        # 3.  compiling the semicolon
        elif self.token.token_type() == "symbol" and self.token.symbol() == ";":
            self.write("push constant 0\n")

        self.check_if_symbol(";", "expected ; for return")

        # 4, adding the return statement
        self.vm_writer.write_return()

    def compileExpression(self):
        """
        Compiles an expression.
        is of the syntax: term (op term)*
        """

        # 2. compiling the term
        self.compileTerm()

        # 3. compiling the (op term)*  - will occur 0 or more times
        while self.token.token_type() == "symbol" and self.token.symbol() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:

            # 3.1. adding the relevant operation
            op = operation_dict[self.token.symbol()]

            self.token.advance()

            # 3.2. compiling the term
            self.compileTerm()

            self.write(op + "\n")

    def compileTerm(self):
        """
            Compiles a term. If the current token is an identifier, the routine must resolve it into a variable,
            an array entry, and a subroutine call.
            A single lookahead token,which may be one of [, (, or ,
            suffices to distinguish between the three possibilities.
            Any other token is not part of this term and should not be advanced over.
        """

        # 1. extracting the first token's type
        term_type = self.token.token_type()

        # 2. compiling based on the term's type

        # 2.1 if term is an integer
        if term_type == "integerConstant":

            if self.token.intVal() >= 0:  # if integer value is positive
                self.vm_writer.write_push("constant", self.token.intVal())

            else:  # if the integer value is negative
                self.vm_writer.write_push("constant", -1 * self.token.intVal())

                self.vm_writer.write_arithmetic("neg")

            self.token.advance()

        # 2.2 if the term is a string
        elif term_type == "stringConstant":

            length = len(self.token.stringVal())  # length of the string

            self.write("push constant " + str(length) + "\n")
            self.write("call String.new 1\n")

            string_const = self.token.stringVal()
            string_const = self.replace_chars(string_const)

            for char in string_const:  # for each character in the string
                self.write("push constant " + str(ord(char)) + "\n")
                self.write("call String.appendChar 2\n")

            self.token.advance()

        # 2.3 if the term is a keyword
        elif term_type == "keyword":
            keyword = self.token.keyWord()

            if keyword not in {"true", "false", "null", "this"}:
                raise CompilerError(self, "incorrect keyword constant")

            if keyword == "true":
                self.write("push constant 0\n")
                self.write("not\n")

            # if keyword is false or null
            elif keyword == "false" or keyword == "null":
                self.write("push constant 0\n")

            elif keyword == "this":
                self.write("push pointer 0\n")

            self.token.advance()

        # 2.4 if the term is an identifier
        elif term_type == "identifier":
            self.token.advance()

            if self.token.token_type() == "symbol":

                # if the expression is of the type varname[expression]
                if self.token.symbol() == "[":
                    self.token.go_back()

                    # compiling the varname
                    self.compile_var_name()

                    # compiling the [
                    self.check_if_symbol("[", "missing [")

                    #  compiling the expression inside the bracket
                    self.compileExpression()

                    # compiling the closing bracket
                    self.check_if_symbol("]", "missing ]")

                    self.vm_writer.write_arithmetic("add")
                    self.write("pop pointer 1\n")

                    self.write("push that 0\n")

                # if the symbol is a subroutine call
                elif self.token.symbol() in {"(", "."}:
                    self.token.go_back()

                    self.compile_subroutine_call()

                # if the symbol is any other identifier
                else:
                    self.token.go_back()

                    self.write_push(self.token.identifier())
                    self.token.advance()

            # if the token is not a symbol
            else:
                self.token.go_back()

                self.write_push(self.token.identifier())  # manually insert
                self.token.advance()

        # 2.5 if the type is an (expression)
        elif term_type == "symbol" and self.token.symbol() == "(":
            # (expression)

            # compiling the (
            self.token.advance()

            # compiling the expression
            self.compileExpression()

            # compiling the closing bracket
            self.check_if_symbol(")", "missing ) ")

        # if term doesn't match the  term, advancing over it
        elif term_type == "symbol" and self.token.symbol() in {'-', '~'}:
            op = self.token.symbol()
            self.token.advance()

            self.compileTerm()

            # if the term is negated
            if op == "-":
                self.vm_writer.write_arithmetic("neg")

            # if the term has a not logic expression
            elif op == "~":
                self.vm_writer.write_arithmetic("not")

        # if invalid term
        else:
            raise CompilerError(self, "unidentified term")

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        Returns a number of expressions in the list.

        is of the syntax: (expression ( ',' expression)* )?
        """

        args_counter = 0  # counter for the amount of arguments

        # 1. checking if the expression is empty
        if self.token.token_type() == "symbol" and self.token.symbol() == ")":
            return args_counter

        # 2. compiling the first expression
        self.compileExpression()
        args_counter += 1

        # 3. compiling additional expressions if they exist
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()

            self.compileExpression()

            args_counter += 1

        return args_counter

    # ___________ Auxiliary Functions _______________

    def compile_subroutine_call(self):
        """
        Auxiliary function to subroutine body that compiles the subroutine's call

        """

        args_counter = 0  # counter for the amount of args

        self.token.advance()

        # if the call is of the syntax :  subroutineName '(' expressionList ')'
        if self.token.token_type() == "symbol" and self.token.symbol() == "(":

            self.token.go_back()
            self.write("push pointer 0\n")

            # compiling the subroutineName
            subroutine_call = self.class_name + "." + self.token.identifier()
            self.token.advance()

            # compiling the (
            self.check_if_symbol("(", "error: ( expected")
            args_counter += self.compileExpressionList()

            # compiling the closing bracket
            self.check_if_symbol(")", "error: ) expected")
            self.write_call(subroutine_call, args_counter + 1)

        # if the call is of the syntax:  # (className |varName) '.' subroutineName '(' expressionList ')'
        elif self.token.token_type() == "symbol" and self.token.symbol() == ".":

            self.token.go_back()

            # compiling the varName or className
            var_class_name = self.token.identifier()
            self.token.advance()

            # compiling the .
            self.check_if_symbol(".", "error: . expected")

            # compiling the subroutine name
            subroutine_call = self.token.identifier()
            if var_class_name in self.symbol_table.subroutine_variables \
                    or var_class_name in self.symbol_table.class_variables:
                object_name = var_class_name

                # pushing hte object's type
                class_objects_name = self.symbol_table.type_of(object_name)
                self.write_push(object_name)

                #  preparing the subroutine name
                subroutine_call = class_objects_name + "." + subroutine_call
                args_counter += 1

            #  if the call is a function or class
            else:
                function_class_name = var_class_name
                subroutine_call = function_class_name + "." + subroutine_call

            self.token.advance()

            # compiling the (
            self.check_if_symbol("(", "error: ( expected")

            # compiling the expressionList
            args_counter += self.compileExpressionList()

            # compiling the closing bracket
            self.check_if_symbol(")", "error: ) expected")
            self.write_call(subroutine_call, args_counter)

        # if the subroutine call is invalid
        else:
            raise CompilerError(self, "error: expected func(list) or class.func(list)")

    def compile_var_name(self):
        """
        auxiliary function to compileVarDec that writes a variable's name
        """

        self.write_push(self.token.identifier())

        self.token.advance()

    def check_if_symbol(self, symbol, message):
        """
        auxiliary function that checks if a variable is a symbol
        """

        if self.token.token_type() != "symbol" or self.token.symbol() != symbol:
            print()

            raise CompilerError(self, message)

        self.token.advance()

    def new_symbol_table(self):
        """
        Auxiliary function that declares a new symbol table
         """

        self.symbol_table = SymbolTable()

    def declare_var_in_symbol_table(self, name, var_type, kind):
        """
        declaring a new variable in a symbol table
        """

        self.symbol_table.define(name, var_type, kind)

    def replace_chars(self, string):
        """
        Auxiliary function that adds an extra slash to certain chars
        """

        replace = {"\t": "\\t", "\n": "\\n", "\r": "\\r", "\b": "\\b"}

        for escaped in replace.keys():
            string = string.replace(escaped, replace[escaped])

        return string

    # ____________________Writing Functions __________________________

    def write(self, string):
        """
        Auxiliary function that writes string to output VM file
        """

        self.vm_writer.write(string)

    def write_push(self, name):
        """
       Auxiliary function that writes a push statement to the VM file
        """

        kind = self.symbol_table.kind_of(name)  # extracting kind type
        index = self.symbol_table.index_of(name)  # extracting index in symbol table

        if kind == "arg":
            self.vm_writer.write_push("argument", index)

        elif kind == "static":
            self.vm_writer.write_push("static", index)

        elif kind == "var":
            self.vm_writer.write_push("local", index)

        elif kind == "field":
            self.vm_writer.write_push("this", index)

    def write_pop(self, name):
        """
        Auxiliary function that writes a pop statement to the VM file
        """

        kind = self.symbol_table.kind_of(name)  # extracting kind type
        index = self.symbol_table.index_of(name)   # extracting index in symbol table

        if kind == "arg":
            self.vm_writer.write_pop("argument", index)

        elif kind == "static":
            self.vm_writer.write_pop("static", index)

        elif kind == "var":
            self.vm_writer.write_pop("local", index)

        elif kind == "field":
            self.vm_writer.write_pop("this", index)

    def write_call(self, name, index):
        """
        Auxiliary Function that writes a call statement to the VM file
        """

        self.vm_writer.write_call(name, index)

    def write_function(self, name, num_local_vars):
        """
       Auxiliary function that writes a function statement to the VM file
        """

        self.vm_writer.write_function(name, num_local_vars)


class CompilerError(SyntaxError):
    def __init__(self, engine, message=""):
        num = engine.token.cnt

        test_amount = 10

        max1 = min([num + test_amount, len(engine.token.tokens)])
        token_list = [engine.token.tokens[i] for i in range(num - test_amount, max1)]

        words = ""

        for word in token_list:
            words += word + " "

        self.msg = "error in file\n" + engine.output_file.name + message + "\n" + "line:  " + words
