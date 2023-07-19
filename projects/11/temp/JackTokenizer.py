import re

keyword_list = [
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do",
    "if", "else", "while", "return"
]

symbol_list = [
    "{", "}", "(", ")", "[", "]", ".", ",", "+",
    "*", "/", "&", "|", "<", ">", "=", "~", ";"
]


class JackTokenizer:
    def __init__(self, inputFile):
        self.tokens = []
        self.cnt = 0
        self.lines = inputFile.readlines()
        self.create_tokens_list()

        self.input = inputFile
        self.line = ""
        self.current_token = ""

    def create_tokens_list(self):
        for line in self.lines:
            cleaned = self.cleaner(line)

            if cleaned:
                for obj in cleaned:
                    self.tokens.append(obj)

    def cleaner(self, line):
        line = line.strip()

        # removing comments
        if line.startswith("/**") or line.startswith("*") or line == "*/" or line.startswith("//"):
            return ""

        # Comment at the end
        elif line.find("//") != -1:
            line = line[:line.find("//")]

        line = line.strip()
        matches = re.findall(r'\"(.+?)\"', line)

        for match in matches:
            match_quoted = match.replace(" ", "__QUOTE__")
            match_quoted = match_quoted.replace(";", "__SEMI__")

            line = line.replace(match, match_quoted)

        split_line = line

        for idx, char in enumerate(line):
            if char in symbol_list:
                split_line = split_line.replace(f"{char}", f" {char} ")
            if char == "-":
                if line[idx-1].isdigit() and line[idx+1].isdigit():
                    split_line = split_line.replace(f"{char}", f" {char} ")

        split_line = split_line.split()

        # Replace match __QUOTE__, __SEMI__
        for i, word in enumerate(split_line):

            if "__QUOTE__" in word:
                split_line[i] = word.replace("__QUOTE__", " ")
            if "__SEMI__" in word:
                split_line[i] = split_line[i].replace("__SEMI__", ";")
        return split_line

    def hasMoreTokens(self):
        return bool( self.cnt + 1 < len(self.tokens))

    def advance(self):
        if self.hasMoreTokens():
            self.current_token = self.tokens[self.cnt]

            self.cnt += 1

    def token_type(self):
        current_token = self.current_token

        if current_token in keyword_list:
            return "keyword"

        elif current_token in symbol_list or current_token == '-':
            return "symbol"

        elif (current_token.isnumeric()) or (current_token[0] == "-" and current_token[1:].isnumeric()):
            return "integerConstant"

        elif current_token[0] == '"' and current_token[-1] == '"':
            return "stringConstant"

        elif current_token != "\n":
            return "identifier"

    def keyWord(self):
        return self.current_token

    def symbol(self):
        return self.current_token

    def identifier(self):
        return self.current_token

    def intVal(self):
        return int(self.current_token)

    def stringVal(self):
        string_value = str( self.current_token[1:-1])
        return string_value

    def go_back(self):
        self.cnt -= 2
        self.current_token = self.tokens[self.cnt]
        self.cnt += 1
