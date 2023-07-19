import sys
import os

import JackTokenizer
import CompilationEngine


class JackCompiler:

    def __init__(self, inputFile):
        self.tokenizer = None
        self.compilationEngine = None  

        # receiving the .jack
        self.inputJack = open(inputFile, "r")

        # output
        outputPath = inputFile.split(".jack")[0] + ".vm"
        self.outputVm = open(outputPath, 'w')

    def compile_vm(self):
        self.tokenizer = JackTokenizer.JackTokenizer(self.inputJack)  # initializing

        # compiling
        self.compilationEngine = CompilationEngine.CompilationEngine(self.tokenizer, self.outputVm)
        self.inputJack.close()
        self.outputVm.close()


def main():

    if len(sys.argv) != 2:
        print("Not Enough Arguments!")
        return exit(1)

    file_path = str(os.path.abspath(sys.argv[1]))
    # Compilation of a file
    if os.path.isfile(file_path):
        JackCompiler(file_path).compile_vm()

    # Iteration over the files in the directory
    if os.path.isdir(file_path):
        for file in os.listdir(file_path):
            if file.endswith(".jack"): 
                JackCompiler(file_path + "/" + file).compile_vm()


if __name__ == '__main__':
    main()
