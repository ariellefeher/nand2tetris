class VMWriter:

    """Writes individual VM commands to the output .vm file."""

    def __init__(self, output_file):
        """
        Creates a new output .vm file, and prepares it for writing.
        """
        self.output_file = output_file

    def write(self, string):
        """Helper function that writes a string directly to a file and doesn't include newlines """
        self.output_file.write(string)

    def write_push(self, segment, index):
        """Writes a VM push command"""
        self.output_file.write("push " + str(segment) + " " + str(index) + "\n")

    def write_pop(self, segment, index):
        """Writes a VM pop command."""
        self.output_file.write("pop " + str(segment) + " " + str(index) + "\n")

    def write_arithmetic(self, command):
        """Writes a VM arithmetic command."""
        self.output_file.write(command + "\n")

    def write_label(self, label):
        """Writes a VM label command."""
        self.output_file.write("label " + label + "\n")

    def write_goto(self, label):
        """Writes a VM goto command"""
        self.output_file.write("goto " + label + "\n")

    def write_if(self, label):
        """Writes a VM if-goto command."""
        self.output_file.write("if-goto " + label + "\n")

    def write_call(self, name, n_args):
        """Writes a VM call command"""
        self.output_file.write("call " + str(name) + " " + str(n_args) + "\n")

    def write_function(self, name, nVars):
        """Writes a VM function command."""
        self.output_file.write("function " + str(name) + " " + str(nVars) + "\n")

    def write_return(self):
        """Writes a VM return command."""
        self.output_file.write("return" + "\n")

    def close(self):
        """Closes the output file / stream ."""
        self.output_file.close()

