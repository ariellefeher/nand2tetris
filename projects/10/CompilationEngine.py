symbol_list = [
    "{", "}", "(", ")", "[", "]", ".", ",", ";", "+",
    "-", "*", "/", "&", "|", "<", ">", "=", "~"
]
subroutine_dec = {"constructor", "function", "method"}


class CompilationEngine:
    """
    the main module of the syntax analyzer that generates the Compiler's Output

    Consists of a set of compile xxx methods,
    One for each grammar rule xxx

    """

    def __init__(self, tokenizer, output_file):
        """
        Creates a new compilation engine with the given input and output.
        """

        self.tab_counter = 0  # counts the amount of tabs needed to write the tags

        self.need_new_line = False # checking if needed a new line, for aesthetic purposes

        self.output_file = output_file  # the XML file we will write the output into

        self.token = tokenizer  # the JackTokenizer received as an input

        #   1. extract the first token
        self.token.advance()

        if self.token.keyWord() != "class":
            raise CompilationError(self, "file doesn't start with a class")

        # The next routine called (by the JackAnalyzer module) must be compileClass() .
        self.compileClass()

    def compileClass(self):
        """
        Compiles a complete class.
        """

        # 1. Adding the relevant tag
        self.add_open_tag("class")

        self.write("\n")

        # Writing the tag into the output file and advancing the pointer of the token
        self.add_keyword()
        self.token.advance()

        # 2.  compiling the class name
        if self.token.token_type() != "identifier":
            raise CompilationError(self, "The class doesn't start with a name!")

        # Writing the tag into the output file and advancing the pointer of the token
        self.add_identifier()
        self.token.advance()

        # 3. compiling the opening bracket {
        self.check_if_symbol("{", "The class doesn't start with {")

        # 4. compiling the Class Body

        # 4.1 checking if there are variable declarations (if static or field), and calling ClassVarDec
        while self.token.token_type() == "keyword" and self.token.keyWord() in {"static", "field"} :
            self.compileClassVarDec()

        # 4.2 checking if there are subroutine declarations, and compile subroutineDec
        while self.token.token_type() == "keyword" and self.token.keyWord() in {"constructor", "function", "method"}:
            self.compileSubroutine()

        # 4. Compiling the closing bracket: }
        self.check_if_symbol("}", "Class must contain only variable declarations and then subroutine declarations")

        self.add_close_tag("class")

    def compileClassVarDec(self):
        """
        Compiles a static declaration, or a field declaration.
        variable declaration is of the following syntax:
        ( 'static' | 'field' ) type varName ( ',' varName)* ';'
        """
        # 1. Adding the opening tag
        self.add_open_tag("classVarDec")
        self.write("\n")

        # 2. compiling the static / field keyword
        self.add_keyword()
        self.token.advance()

        # 3. compiling the type
        self.compile_type()

        # 4. compiling the variable name
        self.compile_var_name()

        # 5. compiling the varname , also checking if there is a comma
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.add_symbol()
            self.token.advance()

            self.compile_var_name()

        # 6. compiling the semicolon ;
        self.check_if_symbol(";", "missing ;")

        # 7. adding the closing tag
        self.add_close_tag("classVarDec")

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
            Subroutine is of the following syntax:
             ( 'constructor' | 'function' | 'method' )
            ( 'void' | type) subroutineName '(' parameterList ')'
             subroutineBody
        """

        # 1. Adding the opening tag
        self.add_open_tag("subroutineDec")
        self.write("\n")

        # 2. compiling the constructor / functon / method keyword
        self.add_keyword()
        self.token.advance()

        # 3. compiling the void / type keywords
        if self.token.token_type() == "keyword" and self.token.keyWord() == "void":
            self.add_keyword()
            self.token.advance()

        else: # if the keyword is type
            self.compile_type()

        # 4. compiling the subroutineName
        self.add_identifier()
        self.token.advance()

        # 5. compiling the opening bracket (
        self.check_if_symbol("(", "expected / ")

        # 6. compiling the parameterList
        self.compileParameterList()

        # 7. compiling the closing bracket
        self.check_if_symbol(")", " expected )  ")

        # 8. compiling the subroutineBody
        self.compileSubroutineBody()

        # 9. adding the closing tag
        self.add_close_tag("subroutineDec")

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list.
        Does not handle the enclosing parentheses tokens (and)

        is of the following syntax: ( (type varName) ( ',' type varName)*)?
        """

        # 1. adding opening tag
        self.add_open_tag("parameterList")
        self.write("\n")

        # 2. checking if the parameter list is empty
        if self.token.token_type() == "symbol" and self.token.symbol() == ")":
            self.add_close_tag("parameterList")
            return

        # 3. compiling type
        self.compile_type()

        # 4. compiling varName
        self.compile_var_name()

        # 5. compiling the type and the varName for each element in the parameter list
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.add_symbol()
            self.token.advance()

            # 5.1 compiling type
            self.compile_type()

            # 5.2 compiling VarName
            self.compile_var_name()

        # 6. adding closing tag
        self.add_close_tag("parameterList")

    def compileSubroutineBody(self):
        """
        compiles a subroutine's body
        is of the syntax :'{' varDec* statements '}'
        """

        # 1. adding the opening tag
        self.add_open_tag("subroutineBody")
        self.write("\n")

        # 2. compiling the opening curly bracket {
        self.check_if_symbol("{", "Expected { to open method body")

        # 3. compiling the variable declaration
        while self.token.token_type() == "keyword" and self.token.keyWord() == "var":
            self.compileVarDec()

        # 4. compiling the statements
        self.compileStatements()

        # 5. compiling the closing curly bracket
        self.check_if_symbol("}", "missing }")

        # 6. compiling the closing tag
        self.add_close_tag("subroutineBody")

    def compileVarDec(self):
        """
        Compiles a var declaration.
        Is of the syntax: 'var' type varName ( ',' varName)* ';'
        """

        # 1. adding the opening tag
        self.add_open_tag("varDec")
        self.write("\n")

        # 2. compiling the variable
        if self.token.token_type() != "keyword" and self.token.keyWord() != "var":
            raise CompilationError(self, "missing variable in the declaration")

        self.add_keyword()
        self.token.advance()

        # 3. compiling the type
        self.compile_type()

        # 4. compiling the variable name
        self.compile_var_name()

        # 5. compiling the  additional variable names
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.add_symbol()
            self.token.advance()

            self.compile_var_name()

        # 6. compiling the semicolon';'
        self.check_if_symbol(";", "missing semicolon ;")

        # 7. adding the closing tags
        self.add_close_tag("varDec")

    def compileStatements(self):
        """
            Compiles a sequence of statements.
             Does not handle the enclosing curly bracket tokens {and}.
             is of the syntax :  statement*  0 or more times
        """

        # 1. adding the opening tag
        self.add_open_tag("statements")
        self.write("\n")

        # 2. checking the type of statement in order to compile
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

        # 3. adding the closing tag
        self.add_close_tag("statements")

    def compileLet(self):
        """
        Compiles a let statement.
        is of the syntax : # 'let' varName ( '[' expression ']' )? '=' expression ';'
        """

        # 1. adding the opening tag
        self.add_open_tag("letStatement")
        self.write("\n")

        # 2. compiling the let
        self.add_keyword()
        self.token.advance()

        # 3. compiling the variable name
        self.compile_var_name()

        # 4. checking if there is an expression
        if self.token.token_type() == "symbol" and self.token.symbol() == "[":
            self.add_symbol()
            self.token.advance()

            self.compileExpression()
            self.check_if_symbol("]", "missing closing bracket")

        # 5. compiling the equals =
        self.check_if_symbol("=", "missing variable assignment")

        # 6. compiling the expression
        self.compileExpression()

        # 7. compiling the semicolon ;
        self.check_if_symbol(";", "missing ;")

        # 8. adding closing tag
        self.add_close_tag("letStatement")

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else clause.
        is of the syntax: 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        """

        # 1. adding opening tag
        self.add_open_tag("ifStatement")
        self.write("\n")

        # 2. compiling the if keyword
        self.add_keyword()
        self.token.advance()

        # 3. compiling the (expression)
        self.check_if_symbol("(", "missing ( for if statement")

        self.compileExpression()

        self.check_if_symbol(")", "missing ) for if statement")

        # 4. compiling the {statements}
        self.check_if_symbol("{", "missing { for if statement")

        self.compileStatements()

        self.check_if_symbol("}", "missing } for if statement")

        # 5. compiling the else statement
        if self.token.token_type() == "keyword" and self.token.keyWord() == "else":

            # 5.1 compiling the else keyword
            self.add_keyword()
            self.token.advance()

            # 5.2 compiling the {statements}
            self.check_if_symbol("{", "missing { in else statement")

            self.compileStatements()

            self.check_if_symbol("}", "missing } in else statement")

        # 6. adding the closing tag
        self.add_close_tag("ifStatement")

    def compileWhile(self):
        """
        Compiles a while statement.
        is of the syntax : 'while' '(' expression ')' '{' statements '}'
        """

        # 1. adding the opening tag
        self.add_open_tag("whileStatement")
        self.write("\n")

        # 2. compiling the while keyword
        self.add_keyword()
        self.token.advance()

        # 3. compiling the (expression)
        self.check_if_symbol("(", "missing ( for while expression")

        self.compileExpression()

        self.check_if_symbol(")", "missing ) for while expression")

        # 4. compiling the { statements }
        self.check_if_symbol("{", "missing { for while expression")

        self.compileStatements()

        self.check_if_symbol("}", "missing } for while expression")

        # 5. adding the closing tag
        self.add_close_tag("whileStatement")

    def compileDo(self):
        """
        Compiles a do statement.
        is of the syntax: 'do' subroutineCall ';'
        """
        # 1. adding the opening tag
        self.add_open_tag("doStatement")
        self.write("\n")

        # 2. compiling the do keyword
        self.add_keyword()
        self.token.advance()

        # 3. compiling the subroutineCall
        self.compile_subroutine_call()

        # 4. compiling the semicolon ;
        self.check_if_symbol(";", "missing semicolon")

        # 5. adding the closing tag
        self.add_close_tag("doStatement")

    def compileReturn(self):
        """
        Compiles a return statement.
        is of the syntax: 'return' expression? ';'
        """

        # 1. adding the opening tag
        self.add_open_tag("returnStatement")
        self.write("\n")

        # 2. compiling the return keyword
        self.add_keyword()
        self.token.advance()

        # 3, checking if there is an expression
        if not (self.token.token_type() == "symbol" and self.token.symbol() == ";"):
            self.compileExpression()

        # compiling the semicolon;
        self.check_if_symbol(";", "missing semicolon")

        self.add_close_tag("returnStatement")

    def compileExpression(self):
        """
        Compiles an expression.
        is of the syntax: term (op term)*
        """

        # 1. adding the opening tag
        self.add_open_tag("expression")
        self.write("\n")

        # 2. compiling the term
        self.compileTerm()

        # 3. compiling the (op term)*  - will occur 0 or more times
        while self.token.token_type() == "symbol" and self.token.symbol() in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            self.add_symbol()
            self.token.advance()

            self.compileTerm()

        # 4. adding the closing tag
        self.add_close_tag("expression")

    def compileTerm(self):
        """
            Compiles a term. If the current token is an identifier, the routine must resolve it into a variable,
            an array entry, and a subroutine call.
            A single lookahead token,which may be one of [, (, or ,
            suffices to distinguish between the three possibilities.
            Any other token is not part of this term and should not be advanced over.
        """
        # 1. adding the opening tag
        self.add_open_tag("term")
        self.write("\n")

        # 2. extracting the first token's type
        term_type = self.token.token_type()

        # 3. compiling based on the term's type

        if term_type == "integerConstant":
            self.add_open_tag("integerConstant")

            self.write(str(self.token.intVal()))

            self.add_close_tag("integerConstant")

            self.token.advance()

        elif term_type == "stringConstant":
            self.add_open_tag("stringConstant")

            # checking if the string includes one of the 4 jack variables that need to be handled separately
            lst = list(self.token.stringVal())
            new_str = ""

            for char in lst:
                if char in symbol_list:
                    special_char = ""

                    if char == "<":  # if the symbol is less than
                        special_char = "&lt;"

                    elif char == ">":  # if the symbol is greater than
                        special_char = "&gt;"

                    elif char == "&":  # if the symbol is and
                        special_char = "&amp;"

                    elif char == '\"':  # if the symbol is "
                        special_char = '&quot;'

                    else: # if the symbol isn't one of the 4 special ones
                        special_char = char

                    new_str += special_char

                else:
                    new_str += char

            self.write(new_str)

            self.add_close_tag("stringConstant")

            self.token.advance()

        # if the type is a keyword
        elif term_type == "keyword":

            if self.token.keyWord() in {"true", "false", "null", "this"}:
                self.add_keyword()
                self.token.advance()

        # if the type is an identifier
        elif term_type == "identifier":
            self.token.advance()

            if self.token.token_type() == "symbol":

                if self.token.symbol() == "[": # is of the type varname[expression]

                    self.token.go_back()

                    # compiling the varname
                    self.compile_var_name()

                    # compiling the [
                    self.check_if_symbol("[", " missing [")

                    # compiling the expression inside the bracket
                    self.compileExpression()

                    # compiling the closing bracket
                    self.check_if_symbol("]", " missing")

                # if the symbol is a subroutine call
                elif self.token.symbol() in {"(", "."}:
                    self.token.go_back()
                    self.compile_subroutine_call()

                # if the symbol is any other identifier
                else:
                    self.token.go_back()
                    self.add_identifier()

                    self.token.advance()

            # if the token is not a symbol
            else:
                self.token.go_back()
                self.add_identifier()

                self.token.advance()

        # if the type is an (expression)
        elif term_type == "symbol" and self.token.symbol() == "(":

            # compiling the (
            self.add_symbol()
            self.token.advance()

            # compiling the expression
            self.compileExpression()

            # compiling the closing bracket
            self.check_if_symbol(")", "missing ) ")

        # if term doesn't match the  term, advancing over it
        elif term_type == "symbol" and self.token.symbol() in {'-', '~'}:

            self.add_symbol()
            self.token.advance()

            self.compileTerm()

        else:
            raise CompilationError(self, "unidentified term")

        # adding closing tag
        self.add_close_tag("term")

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        Returns a number of expressions in the list.

        is of the syntax: (expression ( ',' expression)* )?
        """
        # 1. adding the opening tag
        self.add_open_tag("expressionList")
        self.write("\n")

        # 2. checking if the expression is empty
        if self.token.token_type() == "symbol" and self.token.symbol() == ")":
            self.add_close_tag("expressionList")
            return

        # 3. compiling the first expression
        self.compileExpression()

        # 4. compiling additional expressions if they exist
        while self.token.token_type() == "symbol" and self.token.symbol() == ",":
            self.add_symbol()
            self.token.advance()

            self.compileExpression()

        # 5. adding closing tags
        self.add_close_tag("expressionList")

    # ___________ Auxiliary Functions _______________

    def compile_subroutine_call(self):
        """
        Auxiliary function to subroutine body that compiles the subroutine's call
        """
        #advancing
        self.token.advance()

        if self.token.token_type() == "symbol" and self.token.symbol() == "(" :

            # subroutineName '(' expressionList ')'
            self.token.go_back()

            # subroutineName
            self.add_identifier()
            self.token.advance()

            # (
            self.check_if_symbol("(", "error: ( expected")

            # expressionList
            self.compileExpressionList()

            # )
            self.check_if_symbol(")", "error: ) expected")

        elif self.token.token_type() == "symbol" and self.token.symbol() == ".":
            # (className |varName) '.' subroutineName '(' expressionList ')'
            self.token.go_back()

            # (className |varName)
            self.add_identifier()
            self.token.advance()

            # '.'
            self.check_if_symbol(".", "error: . expected")

            # subroutineName
            self.add_identifier()
            self.token.advance()

            # '('
            self.check_if_symbol("(", "error: ( expected")

            # expressionList
            self.compileExpressionList()

            # )
            self.check_if_symbol(")", "error: ) expected")

        else:
            raise CompilationError(self, "error: expected func(list) or class.func(list)")

    def compile_type(self):
        """
        auxiliary function that compiles the expected type
        """

        # if the type is int, char or boolean
        if self.token.token_type() == "keyword" and self.token.keyWord() in {"int", "char", "boolean"}:
            self.add_keyword()

        # if the type is any other identifier
        elif self.token.token_type() == "identifier":
            self.add_identifier()

        else:
            raise CompilationError(self, "unexpected type")
        self.token.advance()

    def compile_var_name(self):
        """
        auxiliary function to compileVarDec that writes a variable's name
        """

        self.add_identifier()
        self.token.advance()

    def check_if_symbol(self, symbol, message):
        """
        auxiliary function that checks if a variable is a symbol
        """
        if self.token.token_type() != "symbol" or self.token.symbol() != symbol:
            print(self.token.cnt)

            raise CompilationError(self, message)

        self.add_symbol()
        self.token.advance()

    # ____________________Writing Functions __________________________

    def write(self, string):
        """
        writes string to the output xml file
        """
        # checking if there needs to be a newline
        if "\n" in string:
            self.need_new_line = True
        else:
            self.need_new_line = False

        # if doesn't include tags
        if "<" not in string and ">" not in string and "\n" not in string:
            self.output_file.write(" " +string + " ")

        # if includes tags
        else:
            self.output_file.write(string)

    def add_open_tag(self, string):
        """
        writes opening tag of a variable to output file
        is of the syntax <string>
        """
        self.write("  " * self.tab_counter + "<" + string+ ">" )
        self.tab_counter += 1

    def add_close_tag(self, string):
        """
        writes closing tag of a variable to output file
        is of the syntax </string>
        """
        self.tab_counter -= 1

        if self.need_new_line:
            self.write("  " * self.tab_counter + "</" + string + ">\n")

        else:
            self.write("</" + string + ">\n")

    def add_keyword(self):
        """
        writes keyword tag to the output file
        """
        self.add_open_tag("keyword")

        self.write(self.token.keyWord())

        self.add_close_tag("keyword")

    def add_identifier(self):
        """
        writes identifier tag to the output file
        """
        self.add_open_tag("identifier")

        self.write(self.token.identifier())  # adding to the output file

        self.add_close_tag("identifier")

    def add_symbol(self):
        """
        writes symbol tag to the output file
        """
        self.add_open_tag("symbol")

        # checking if the symbol needs to be handled
        if self.token.symbol() in symbol_list:

            special_char = ""

            if self.token.symbol() == "<": # if the symbol is less than
                special_char = "&lt;"

            elif self.token.symbol() == ">":  # if the symbol is greater than
                special_char = "&gt;"

            elif self.token.symbol() == "&":  # if the symbol is and
                special_char = "&amp;"

            elif self.token.symbol() == '\"':  # if the symbol is "
                special_char = '&quot;'

            else: # if not one of the four special symbols
                special_char = self.token.symbol()

            self.write(special_char)

        else:
            self.write(self.token.symbol()) # adding to the output file

        self.add_close_tag("symbol")


class CompilationError(SyntaxError):
    def __init__(self, engine, message=""):
        self.msg = "file error\n" + engine.output_file.name + \
                   message + "\n"