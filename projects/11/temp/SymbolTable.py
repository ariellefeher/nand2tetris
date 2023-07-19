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
        self.staticCnt = 0  # amount of static variables in the table
        self.fieldCnt = 0  # amount of field variables in the table
        self.argCnt = 0  # amount of args variables in the table
        self.varCnt = 0  # amount of var variables in the table

        self.classVariables = {}  # change name from classIdentifiers
        self.subroutineVariables = {}  # change name from subroutineIdentifiers

    def reset(self):
        """
        Empties the symbol table, and resets the four indexes to 0.
        Should be called when starting to compile a subroutine declaration.
        """
        # Emptying the Symbol table
        self.subroutineVariables = {}

        # Resets the Indexes to 0
        self.argCnt = 0
        self.varCnt = 0

    def define(self, name, type, kind):
        """
        Defines a new variable of a given name, type, and kind.
        Assigns to it the index value of that kind, and adds 1 to the index.
        """

        if kind == "static":
            self.classVariables[name] = [type, kind, self.staticCnt]
            self.staticCnt += 1

        elif kind == "field":
            self.classVariables[name] = [type, kind, self.fieldCnt]
            self.fieldCnt += 1

        elif kind == "arg":
            self.subroutineVariables[name] = [type, kind, self.argCnt]
            self.argCnt += 1

        elif kind == "var":
            self.subroutineVariables[name] = [type, kind, self.varCnt]
            self.varCnt += 1

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

        if self.classVariables.get(name):  # if the variable is a class
            return self.classVariables.get(name)[1]

        elif self.subroutineVariables.get(name):  # if the variable is a subroutine
            return self.subroutineVariables.get(name)[1]

        else:
            return None

    def type_of(self, name):
        """Returns the type of the named variable."""

        if self.classVariables.get(name):  # if the variable is a class
            return self.classVariables.get(name)[0]

        elif self.subroutineVariables.get(name):  # if the variable is a subroutine
            return self.subroutineVariables.get(name)[0]

        else:
            return None

    def index_of(self, name):
        """Returns the index of the named variable."""

        if self.classVariables.get(name):  # if the variable is a class
            return self.classVariables.get(name)[2]

        elif self.subroutineVariables.get(name):  # if the variable is a subroutine
            return self.subroutineVariables.get(name)[2]

        else:
            return -1
