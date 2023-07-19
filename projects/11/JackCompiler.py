import sys
import os

import JackTokenizer
import CompilationEngine


class JackCompiler:

    def __init__(self, input_file):
        self.tokenizer = None  # JackTokenizer variable

        self.compilation_engine = None  # CompilationEngine variable

        # receiving a .jack file as an input
        self.input_jack_file = open(input_file, "r")

        # creating a .vm file for the output
        output_path = input_file.split(".jack")[0] + ".vm"

        self.output_vm_file = open(output_path, 'w')

    def compile_vm(self):
        self.tokenizer = JackTokenizer.JackTokenizer(self.input_jack_file)  # tokenizer initialization

        # compiling the VM file using the tokenizer
        self.compilation_engine = CompilationEngine.CompilationEngine(self.tokenizer, self.output_vm_file)

        self.input_jack_file.close()
        self.output_vm_file.close()


def main():

    # if not enough input arguments
    if len(sys.argv) != 2:
        print("Invalid Argument Amount")
        return exit(1)

    file_path = str(os.path.abspath(sys.argv[1]))  # absolute path of the file

    # Option 1. path is a single file
    if os.path.isfile(file_path):
        JackCompiler(file_path).compile_vm()

    # Option 2.  path is a dir list
    if os.path.isdir(file_path):

        for file in os.listdir(file_path):  # checking all files in folder

            if file.endswith(".jack"):  # if the file is of the type .jack, compile to .vm
                JackCompiler(file_path + "/" + file).compile_vm()


if __name__ == '__main__':
    main()

