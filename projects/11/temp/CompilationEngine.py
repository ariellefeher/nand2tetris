from SymbolTable import SymbolTable
from VMWriter import VMWriter

SYMBOL_LIST = [
    "{", "}", "(", ")", "[", "]", ".", ",", ";", "+",
    "-", "*", "/", "&", "|", "<", ">", "=", "~"
]
subroutine_dec = {"constructor", "function", "method"}


class CompilationEngine:

    if_count: int
    vm_writer: VMWriter

    def __init__(self, tokenizer, output_file):
        """
        Creates a new compilation
        engine with the given input and
        output. The next routine called
        must be compileClass() .
        """
        self.tab_cnt = 0
        self.is_new_line = False
        self.output_file = output_file
        self.token = tokenizer
        self.vm_writer = VMWriter(output_file)

        # make a new symbol table for the new class
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.if_count = 0
        self.loop_count = 0

        # get first token
        self.token.advance()

        if self.token.token_type() != "keyword" or self.token.keyWord() != "class":
            raise CompilerError(self, "File must begin with \"class\"")

        self.compileClass()

    def compileClass(self):
        """
        Compiles a complete class.
        """
        # class
        self.token.advance()

        # name
        if self.token.token_type() != "identifier":
            raise CompilerError(self, "Class must begin with class name")

        self.class_name = self.token.identifier()
        self.token.advance()

        self.isCompileSymbolValid("{", "Class must begin with {")

        while self.token.token_type() == "keyword" and self.token.keyWord() in {'static', 'field'}:
            #  static or field
            self.compileClassVarDec()

        # while next token match subroutineDec, compile subroutineDec
        while self.token.token_type() == "keyword" and self.token.keyWord() in {'constructor', 'function', 'method'}:
            self.compileSubroutine()

        # ensure next token is }
        self.isCompileSymbolValid("}", "} expected at end of Class.")

    def compileClassVarDec(self):
        """
        Compiles a static declaration or a field declaration.
        """
        # static | field  (this is the kind)
        kind = self.token.keyWord()
        self.token.advance()
        # type or class type
        if self.token.token_type() == "keyword":
            var_type = self.token.keyWord()
        else:
            var_type = self.token.identifier()
        self.token.advance()
        name = self.token.identifier()
        self.token.advance()
        self.declareVariable(name, var_type, kind)

        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()
            name = self.token.identifier()
            self.token.advance()
            self.declareVariable(name, var_type, kind)

        self.isCompileSymbolValid(";", "expected closing \";\" for declaration")

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        """
        # subroutineBody
        # 'constructor' | 'function' | 'method'
        self.symbol_table.reset()
        subroutine_type = self.token.keyWord()
        is_constructor = False
        is_method = False
        if subroutine_type == "constructor":
            is_constructor = True
        elif subroutine_type == "method":
            self.declareVariable("this", self.class_name, "arg")
            is_method = True
        self.token.advance()

        # save name as (classname.sub routine name), to be used later when writing the call
        self.token.advance()
        name = self.token.identifier()
        if self.token.token_type() == "symbol" and self.token.symbol() == ".":
            self.token.advance()
            name = name + "." + self.token.identifier()
        else:
            self.token.advance()
            name = self.class_name + "." + name

        # (
        self.isCompileSymbolValid("(", "expected opening \"(\" for parameterList ")

        # parameterList
        self.compileParameterList()

        # )
        self.isCompileSymbolValid(")", "expected closing \")\" for parameterList  ")

        # subroutineBody
        self.compileSubroutineBody(name, is_constructor, is_method)

    def compileParameterList(self):
        """
        compiles a (possibly empty) parameter list, not including the enclosing parentheses (and).
        """

        # ( (type varName) ( ',' type varName)*)?

        # if empty - ?
        if self.token.token_type() == "symbol" and self.token.symbol() == ")":
            return None

        # single type or class type
        if self.token.token_type() == "keyword":
            var_type = self.token.keyWord()
        else:
            var_type = self.token.identifier()
        self.token.advance()
        name = self.token.identifier()
        self.token.advance()
        self.declareVariable(name, var_type, "arg")

        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()
            if self.token.token_type() == "keyword":
                var_type = self.token.keyWord()
            else:
                var_type = self.token.identifier()
            self.token.advance()
            name = self.token.identifier()
            self.token.advance()
            self.declareVariable(name, var_type, "arg")

    def compileSubroutineBody(self, name, is_constructor, is_method):
        """
        Compiles a subroutine's body.
        """

        # '{'
        self.isCompileSymbolValid("{", "Expected { to open method body")

        num_locals = 0
        while self.token.token_type() == "keyword" and self.token.keyWord() == "var":
            num_locals += self.compileVarDec()
            # write the function declaration
        self.write_function(name, num_locals)
        # if constructor, write alloc
        if is_constructor:
            self.write("push constant " + str(self.symbol_table.fieldCnt) + "\n")
            self.write("call Memory.alloc 1\n")
            self.write("pop pointer 0\n")
        #  method, point this
        elif is_method:
            self.write("push argument 0\n")
            self.write("pop pointer 0\n")

        # statements
        self.compileStatements()

        # '}'
        self.isCompileSymbolValid("}", "Expected } to close method body")

    def compileSubroutineCall(self):
        """
        Compiles a subroutine's call. Helper function.
        """
        self.token.advance()
        args_num = 0

        if self.token.token_type() == "symbol" and self.token.symbol() == "(":
            # subroutineName '(' expressionList ')'
            self.token.go_back()
            self.write("push pointer 0\n")

            # subroutineName
            subroutine_name = self.class_name + "." + self.token.identifier()
            self.token.advance()

            # (
            self.isCompileSymbolValid("(", "expected ( for function arguments")
            args_num += self.compileExpressionList()

            # )
            self.isCompileSymbolValid(")", "expected ) for function arguments")
            #self.write("push pointer 0\n")
            self.write_call(subroutine_name, args_num + 1)

        elif self.token.token_type() == "symbol" and self.token.symbol() == ".":
            # (className |varName) '.' subroutineName '(' expressionList ')'
            self.token.go_back()

            # (className |varName)
            class_or_var_name = self.token.identifier()
            self.token.advance()

            # '.'
            self.isCompileSymbolValid(".", "expected . for class.method")

            # subroutineName  (method / func name)
            subroutine_name = self.token.identifier()
            if (class_or_var_name in self.symbol_table.subroutineVariables) \
                    or (class_or_var_name in self.symbol_table.classVariables):
                object_name = class_or_var_name
                # the type is in our vars
                objects_class_name = self.symbol_table.type_of(object_name)
                self.write_push(object_name)
                subroutine_name = objects_class_name + "." + subroutine_name
                args_num += 1
            else:
                func_class_name = class_or_var_name
                subroutine_name = func_class_name + "." + subroutine_name

            self.token.advance()

            # '('
            self.isCompileSymbolValid("(", "expected ( for function arguments")

            # expressionList
            args_num += self.compileExpressionList()

            # )
            self.isCompileSymbolValid(")", "expected ) for function arguments")
            self.write_call(subroutine_name, args_num)
        else:
            raise CompilerError(self, "Expected func(list) or class.func(list)")

    def compileVarDec(self):
        """
        Compiles a var declaration.
        """
        num_vars = 0
        # var
        if self.token.token_type() != "keyword" and self.token.keyWord() != "var":
            raise CompilerError(self, "expected \"var\" in variable declaration")
        self.token.advance()

        # type or class type
        if self.token.token_type() == "keyword":
            var_type = self.token.keyWord()
        else:
            var_type = self.token.identifier()
        self.token.advance()
        # var name
        name = self.token.identifier()
        self.token.advance()
        # declare
        self.declareVariable(name, var_type, "var")
        num_vars += 1

        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()
            name = self.token.identifier()
            self.token.advance()
            self.declareVariable(name, var_type, "var")
            num_vars += 1

        # ';'
        self.isCompileSymbolValid(";", "expected ; at end of variable declaration")
        return num_vars

    def compileVarName(self):
        """
        Compiles a variable name. Helper function.
        """
        self.write_push(self.token.identifier())
        self.token.advance()

    def compileStatements(self):
        """
        Compiles a sequence of statements. Does not handle the enclosing curly bracket tokens {and}.
        """
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
        """
        # let
        self.token.advance()

        # varname
        var_name = self.token.identifier()
        self.token.advance()

        # possible [ expression ]
        if self.token.token_type() == "symbol" and self.token.symbol() == "[":
            self.write_push(var_name)
            self.token.advance()
            self.compileExpression()
            self.isCompileSymbolValid("]", "expected to match [")

            # =
            self.isCompileSymbolValid("=", "expected in assignment")
            self.compileExpression()
            self.write("pop temp 1\n")
            self.write("add\n")
            self.write("pop pointer 1\n")
            self.write("push temp 1\n")
            self.write("pop that 0\n")
        else:
            self.isCompileSymbolValid("=", "expected in assignment")
            self.compileExpression()
            self.write_pop(var_name)
        # ;
        self.isCompileSymbolValid(";", "expected ; at end of assignment")

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else clause.
        """
        self.token.advance()

        # '(' expression ')'
        self.isCompileSymbolValid("(", "expected ( in (expression) for if")
        self.compileExpression()
        self.isCompileSymbolValid(")", "expected ) in (expression) for if")

        self.write_arithmetic("not")
        if_num = self.if_count
        self.if_count += 1
        self.write_if_goto("ifElse" + str(if_num))

        # '{' statements '}'
        self.isCompileSymbolValid("{", "expected { in {statements} for if")
        self.compileStatements()
        self.isCompileSymbolValid("}", "expected } in {statements} for if")

        self.write_goto("ifEnd" + str(if_num))
        self.write_label("ifElse" + str(if_num))
        # else
        if self.token.token_type() == "keyword" and self.token.keyWord() == "else":
            # else
            self.token.advance()

            # '{' statements '}'
            self.isCompileSymbolValid("{", "expected { in {statements} for else")
            self.compileStatements()
            self.isCompileSymbolValid("}", "expected } in {statements} for else")

        self.write_label("ifEnd" + str(if_num))

    def compileWhile(self):
        """
        Compiles a while statement.
        """
        loop_num = str(self.loop_count)
        self.loop_count += 1
        self.write_label("whileStart" + loop_num)

        # while
        self.token.advance()

        # '(' expression ')
        self.isCompileSymbolValid("(", "expected ( in (expression) for while")
        self.compileExpression()
        self.isCompileSymbolValid(")", "expected ) in (expression) for while")

        # if not expression - go to end
        self.write_arithmetic("not")
        self.write_if_goto("whileEnd" + loop_num)

        # '{' statements '}'
        self.isCompileSymbolValid("{", "expected { in {statements} for while")
        self.compileStatements()
        self.isCompileSymbolValid("}", "expected } in {statements} for while")
        self.write_goto("whileStart" + loop_num)
        self.write_label("whileEnd" + loop_num)

    def compileDo(self):
        """
        Compiles a do statement.
        """
        self.token.advance()
        self.compileSubroutineCall()
        self.write("pop temp 0\n")
        self.isCompileSymbolValid(";", "expected ; after subroutine call")

    def compileReturn(self):
        """
        Compiles a return statement.
        """
        self.token.advance()
        # expression
        if self.token.token_type() != "symbol" or self.token.symbol() != ";":
            self.compileExpression()
        elif self.token.token_type() == "symbol" and self.token.symbol() == ";":
            self.write("push constant 0\n")

        # ';'
        self.isCompileSymbolValid(";", "expected ; for return")
        self.write_return()

    def compileExpression(self):
        """
        Compiles an expression.
        """
        # term
        self.compileTerm()
        op_dict = {
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
        while self.token.token_type() == "symbol" and self.token.symbol() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            op = op_dict[self.token.symbol()]
            self.token.advance()
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
        first_type = self.token.token_type()
        if first_type == "integerConstant":
            if self.token.intVal() < 0:
                self.vm_writer.write_push("constant", -1 * self.token.intVal())
                self.vm_writer.write_arithmetic("neg")
            else:
                self.vm_writer.write_push("constant", self.token.intVal())
            self.token.advance()

        elif first_type == "stringConstant":
            length = len(self.token.stringVal())
            self.write("push constant " + str(length) + "\n")
            self.write("call String.new 1\n")
            string_const = self.token.stringVal()
            string_const = self.replaceEscapedChars(string_const)
            for char in string_const:
                self.write("push constant " + str(ord(char)) + "\n")
                self.write("call String.appendChar 2\n")  # see if correct - way to create string
            self.token.advance()

        elif first_type == "keyword":
            keyword = self.token.keyWord()
            if keyword not in {"true", "false", "null", "this"}:
                raise CompilerError(self, "bad keyword constant")
            if keyword == "true":
                self.write("push constant 0\n")
                self.write("not\n")
            # False / Null
            elif keyword in {"false", "null"}:
                self.write("push constant 0\n")
            elif keyword == "this":
                self.write("push pointer 0\n")
            self.token.advance()

        elif first_type == "identifier":
            self.token.advance()
            if self.token.token_type() == "symbol":
                if self.token.symbol() == "[":
                    self.token.go_back()
                    # varname
                    self.compileVarName()

                    # [
                    self.isCompileSymbolValid("[", "[ expected for array index")

                    #  expression
                    self.compileExpression()

                    # [
                    self.isCompileSymbolValid("]", "] expected for array index")

                    self.write_arithmetic("add")
                    self.write("pop pointer 1\n")
                    self.write("push that 0\n")

                elif self.token.symbol() in {"(", "."}:
                    self.token.go_back()
                    self.compileSubroutineCall()

                else:
                    self.token.go_back()
                    self.write_push(self.token.identifier())
                    self.token.advance()

            else:
                self.token.go_back()
                self.write_push(self.token.identifier())
                self.token.advance()

        elif first_type == "symbol" and self.token.symbol() == "(":
            # (expression)

            # (
            self.token.advance()

            # expression
            self.compileExpression()

            # )
            self.isCompileSymbolValid(")", "expression should end with ) ")

        elif first_type == "symbol" and self.token.symbol() in {'-', '~'}:
            op = self.token.symbol()
            self.token.advance()
            self.compileTerm()
            if op == "-":
                self.write_arithmetic("neg")
            elif op == "~":
                self.write_arithmetic("not")
        else:
            raise CompilerError(self, "invalid term")

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        Returns a number of expressions in the list.
        """
        args_num = 0

        if self.token.token_type() == "symbol" and self.token.symbol() == ")":
            return args_num

        # one expression
        self.compileExpression()
        args_num += 1

        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.token.advance()
            self.compileExpression()
            args_num += 1

        return args_num

    # sub functions

    def isCompileSymbolValid(self, symbol, message):
        """
        Checks if the symbol is valid.
        """
        if self.token.token_type() != "symbol" or self.token.symbol() != symbol:
            print()
            raise CompilerError(self, message)

        self.token.advance()

    # helpers
    def makeSymbolTable(self):
        """make a new symbol table"""
        self.symbol_table = SymbolTable()

    def declareVariable(self, name, var_type, kind):
        """declare a variable in the symbol table"""
        self.symbol_table.define(name, var_type, kind)

    def write_push(self, name):
        kind = self.symbol_table.kind_of(name)
        idx = self.symbol_table.index_of(name)
        if kind == "arg":
            self.vm_writer.write_push("argument", idx)
        elif kind == "static":
            self.vm_writer.write_push("static", idx)
        elif kind == "var":
            self.vm_writer.write_push("local", idx)
        elif kind == "field":
            self.vm_writer.write_push("this", idx)

    def write_pop(self, name):
        kind = self.symbol_table.kind_of(name)
        idx = self.symbol_table.index_of(name)
        if kind == "arg":
            self.vm_writer.write_pop("argument", idx)
        elif kind == "static":
            self.vm_writer.write_pop("static", idx)
        elif kind == "var":
            self.vm_writer.write_pop("local", idx)
        elif kind == "field":
            self.vm_writer.write_pop("this", idx)

    def write_function(self, name, n_locals):
        self.vm_writer.write_function(name, n_locals)

    def write_return(self):
        self.vm_writer.write_return()

    def write_call(self, name, index):
        self.vm_writer.write_call(name, index)

    def write(self, string):  #
        """
        writes a string to output file
        """
        self.vm_writer.write(string)

    def write_arithmetic(self, command):
        """Writes a VM arithmetic command."""
        self.vm_writer.write_arithmetic(command)

    def write_if_goto(self, label):
        self.vm_writer.write_if(label)

    def write_goto(self, label):
        self.vm_writer.write_goto(label)

    def write_label(self, label):
        self.vm_writer.write_label(label)

    def replaceEscapedChars(self, string):
        replace = {"\t": "\\t", "\n": "\\n", "\r": "\\r", "\b": "\\b"}
        for escaped in replace.keys():
            string = string.replace(escaped, replace[escaped])
        return string


class CompilerError(SyntaxError):
    def __init__(self, engine, message=""):
        num = engine.token.cnt
        s = 10
        max1 = min([num + s, len(engine.token.tokens)])
        token_list = [engine.token.tokens[i] for i in range(num - s, max1)]
        words = ""
        for word in token_list:
            words += word + " "
        self.msg = "error in file\n" + engine.output_file.name + message + "\n" + "line:  " + words
