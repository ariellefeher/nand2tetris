import re

keyword_list = [
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do",
    "if", "else", "while", "return"
]

symbol_list = [
    "{", "}", "(", ")", "[", "]", ".", ",", ";", "+",
    "-", "*", "/", "&", "|", "<", ">", "=", "~"
]


class JackTokenizer:
    def __init__(self, input_file):
        self.tokens = []  # an array of the tokens

        self.cnt = 0 # a counter that serves as a pointer to the token in the file

        self.lines = input_file.readlines()  # amount of lines in the file

        self.create_tokens_list()  # initializing the token list

        # starting the initializations

        self.input = input_file # saving the input file

        self.line = "" # initializing the line count

        self.current_token = ""  # initializing the current token

    def create_tokens_list(self):
        for line in self.lines:
            cleaned = self.clean_lines(line)

            if cleaned:
                for obj in cleaned:
                    self.tokens.append(obj)

    def clean_lines(self, line):

        line = line.strip()

        # removing the lines with comments
        if line.startswith("/**") or line.startswith("*") or line == "*/" or line.startswith("//"):
            return ""

        # if the comment is at the end of a line of code
        elif line.find("//") != -1:
            line = line[:line.find("//")]

        # handling string variables that have spaces in them
        matches = re.findall(r'\"(.+?)\"', line)

        for match in matches:
            match_quoted = match.replace(" ", "__QUOTE__")

            line = line.replace(match, match_quoted)

        split_line = line

        # Adding spaces to symbols, so that they will split later in the function
        for char in line:
            if char in symbol_list:
                split_line = split_line.replace(f"{char}", f" {char} ")

        split_line = split_line.split()

        # erasing the strings that match __QUOTE__ from earlier
        for i, word in enumerate(split_line):

            if "__QUOTE__" in word:
                split_line[i] = word.replace("__QUOTE__", " ")

        return split_line

    def hasMoreTokens(self):
        """
        Are there more tokens in the input?
        """
        return bool( self.cnt + 1 < len(self.tokens))

    def advance(self):
        """
        Gets the next token from the input, and makes it the current token
        This method should be called only is hasMoreTokens is true
        initially there is no current token
        """

        if self.hasMoreTokens():
            self.current_token = self.tokens[self.cnt]

            self.cnt += 1

    def token_type(self):
        """
        Returns the type of the current token,
        as a constant
        """

        current_token = self.current_token

        if current_token in keyword_list:
            return "keyword"

        elif current_token in symbol_list:
            return "symbol"

        elif current_token.isnumeric():
            return "integerConstant"

        elif current_token[0] == '"' and current_token[-1] == '"':
            return "stringConstant"

        elif current_token != "\n":
            return "identifier"

    def keyWord(self):
        """
        Returns the keyword which is the current token, as a constant
        this method should only be called if tokenType is KEYWORD
        """

        return self.current_token

    def symbol(self):
        """
        Returns the character which is the current token
        this method should only be called if tokenType is SYMBOL
        """

        return self.current_token

    def identifier(self):
        """
        Returns the string which is the current token
        this method should only be called if tokenType is IDENTIFIER
        """

        return self.current_token

    def intVal(self):
        """
        Returns the integer which is the current token
        this method should only be called if tokenType is INT_CONST
        """
        integer_value = int(self.current_token)
        return integer_value

    def stringVal(self):
        """
        Returns the string value of the current token,
        without the opening and closing double quotes
        this method should only be called if tokenType is STRING_CONST
        """
        string_value = str( self.current_token[1:-1])
        return string_value

    def go_back(self):
        """
        Auxiliary function for ease of use in Compilation Engine
        goes back to the previous token
        """
        self.cnt -= 2

        # returning back to the previous token
        self.current_token = self.tokens[self.cnt]

        self.cnt += 1