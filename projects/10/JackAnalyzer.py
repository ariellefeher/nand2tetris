import sys
import os

import JackTokenizer
import CompilationEngine


class JackAnalyzer:

    def __init__(self, input_file):
        self.tokenizer = None  # variable that will hold the JackTokenizer

        self.compilation_engine = None # variable that will hold the CompilationEngine

        # receiving the .jack file as an input
        self.input_jack_file = open(input_file, "r")

        # output XML file: creating a xml file that we'll write into
        output_path = input_file.split(".jack")[0] + ".xml"

        self.output_xml_file = open(output_path, 'w')

    def analyzer_compilation(self):
        self.tokenizer = JackTokenizer.JackTokenizer(self.input_jack_file)  # initializing the tokenizer

        self.compilation_engine = CompilationEngine.CompilationEngine(self.tokenizer, self.output_xml_file) # compiling using the tokenizer


def main():

    if len(sys.argv) != 2:  # if the input arguments are incorrect
        print("Not Enough Arguments!")
        return exit(1)

    file_path = str(os.path.abspath(sys.argv[1])) # extracting the absolute path of the file

    # if the path is a single file
    if os.path.isfile(file_path):
        JackAnalyzer(file_path).analyzer_compilation()

    # if the path is a dir
    if os.path.isdir(file_path):

        for file in os.listdir(file_path): # checking all the files in the dir

            if file.endswith(".jack"): # compile if the file is a jack file
                JackAnalyzer(file_path + "/" + file).analyzer_compilation()


if __name__ == '__main__':
    main()
