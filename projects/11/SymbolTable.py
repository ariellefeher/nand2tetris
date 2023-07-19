class SymbolTable:
    """
    Provides a symbol table abstraction. The symbol table associates the
    identifier names found in the program with identifier properties needed for
     compilation: type, kind, and running index.
    """

    def __init__(self):
        """
        Creates a new empty symbol table.
        """
        self.staticCount = 0  # static variable counter

        self.fieldCount = 0  # field variables counter

        self.argCount = 0  # args counter

        self.varCount = 0  # var counter

        self.class_variables = {}   # holds all the class variables

        self.subroutine_variables = {}  # holds all the subroutine variables

    def reset(self):
        """
        Empties the symbol table, and resets the four indexes to 0.
        Should be called when starting to compile a subroutine declaration.
        """
        # 1. Empty the Symbol Table
        self.subroutine_variables = {}  # emptying subroutine variables from the table
        # self.class_variables = {}

        # 2. Resets the four indexes to 0
        self.argCount = 0
        self.varCount = 0

        # self.staticCnt = 0
        # self.fieldCnt = 0

    def define(self, name, type, kind):
        """
        Defines a new variable of a given name, type, and kind.
        Assigns to it the index value of that kind, and adds 1 to the index.
        """

        if kind == "static":
            self.class_variables[name] = [type, kind, self.staticCount]
            self.staticCount += 1

        elif kind == "field":
            self.class_variables[name] = [type, kind, self.fieldCount]
            self.fieldCount += 1

        elif kind == "arg":
            self.subroutine_variables[name] = [type, kind, self.argCount]
            self.argCount += 1

        elif kind == "var":
            self.subroutine_variables[name] = [type, kind, self.varCount]
            self.varCount += 1

    def var_count(self, kind):
        """
        Returns the number of variables of the given kind already defined in the table.
        """
        if kind == "static":
            return self.staticCnt

        elif kind == "field":
            return self.fieldCnt

        elif kind == "arg":
            return self.argCnt

        elif kind == "var":
            return self.varCnt

        else:
            return -1

    def kind_of(self, name):
        """
        Returns the kind of the named identifier.
        If the identifier is not found, returns NONE .
        """
        if self.class_variables.get(name):  # if the name variable is a class
            return self.class_variables.get(name)[1]

        elif self.subroutine_variables.get(name):  # if the variable is a subroutine
            return self.subroutine_variables.get(name)[1]

        else:  # invalid
            return None

    def type_of(self, name):
        """Returns the type of the named variable."""

        if self.class_variables.get(name):  # if the name variable is a class
            return self.class_variables.get(name)[0]

        elif self.subroutine_variables.get(name):  # if the name variable is a subroutine
            return self.subroutine_variables.get(name)[0]

        else:  # invalid input
            return None

    def index_of(self, name):
        """Returns the index of the named variable."""

        if self.class_variables.get(name):  # if the name variable is a class
            return self.class_variables.get(name)[2]

        elif self.subroutine_variables.get(name):  # if the name variable is a subroutine
            return self.subroutine_variables.get(name)[2]

        else:  # invalid input
            return -1
