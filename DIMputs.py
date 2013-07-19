import collections
import re


class DataInput():
    def __init__(self, file_name):
        self.file = open(file_name, "r")
        self.sentences = None

        
    def read_phrase(self):
        self.sentences = []
        sentence = None
        span_reg = re.compile("\|[0-9]+-[0-9]+\|")
        previous = ""
        for line in self.file:
            sentence = Single()
            for word in line.split():
                if span_reg.match(word):
                    sentence.spans[tuple([int(i) for i in word.strip("|").split("-")])] = previous.strip()
                    previous = " "
                else:
                    previous += word + " "
            sentence.set_length()
            self.sentences.append(sentence)
            sentence.number = len(self.sentences)

    def read_syntax(self):
        self.sentences = []
        sentence = None
        number = -1
        for line in self.file:
            if int(line.split()[2]) != number:
                if sentence is not None:
                    sentence.set_length()
                    self.sentences.append(sentence)
                sentence = Single()
                sentence.number = int(line.split()[2])
                number = sentence.number
            sentence.spans[tuple([int(i) for i in line.split()[3].strip(":[]").split("..")])] \
 = line

        if sentence is not None:
            sentence.set_length()
            self.sentences.append(sentence)
                # = tuple([line.split(":")[1], line.split(":")[2], line.split(":")[3]])
                
    
    def read_syntax_cubes(self, cell_limit):
        self.sentences = []
        sentence = None
        number = -1
        for line in self.file:
            if not line.startswith("Trans Opt"):
                pass  # we dont care for those lines
            else:
                if int(line.split()[2]) != number:
                    if sentence is not None:
                        sentence.set_length()
                        self.sentences.append(sentence)
                    sentence = Multiple()
                    sentence.number = int(line.split()[2])
                    number = sentence.number
                span = tuple([int(i) for i in line.split()[3].strip(":[]").split("..")])
                if len(sentence.spans[span]) < cell_limit:
                    sentence.spans[span].append(line)
        if sentence is not None:
            sentence.set_length()
            self.sentences.append(sentence)
    
    def read_phrase_stack_flag(self, cell_limit):
        self.sentences = []
        sentence = None
        number = -1
        for line in self.file:
            if len(line.split()) < 6:
                pass
#            elif re.match("recombined=[0-9]+", line.split()[6]):
#                pass
            else:
                if int(line.split()[0]) != number:
                    if sentence is not None:
                        sentence.set_length()
                        self.sentences.append(sentence)
                    sentence = Multiple()
                    sentence.number = int(line.split()[0])
                    number = sentence.number
#                span = tuple([int(i) for i in line.split()[8].split("=")[1].split("-")])
                span = re.search(r"covered=([0-9]+\-[0-9]+)", line).expand("\g<1>")
                #print span.expand("\g<1>")
                span = tuple([int(i) for i in span.split("-")])
                if len(sentence.spans[span]) < cell_limit:
                    sentence.spans[span].append(line)
        if sentence is not None:
            sentence.set_length()
            self.sentences.append(sentence)
            
    def read_phrase_stack_verbose(self, cell_limit):
        self.sentences = []
        sentence = None
        number = -1
        span_input = False
        for line in self.file:
            if line.startswith("Translating: "):
                if sentence is not None:
                    sentence.set_length()
                    self.sentences.append(sentence)
                    
                number += 1
                sentence = Multiple()
                sentence.number = number
            else:
                if re.match("\[[A-Z,a-z,\ ]+;\ [0-9]+-[0-9]+\]", line):
                    span = tuple([int(i) for i in line.split(";")[1].strip().strip("]").split("-")])
                    sentence.spans[span].append(line.strip())
                    span_input = True
#                    print line,
                elif span_input is True:
                    if line.strip() == "":
                        span_input = False
#                        print "X"
                    else:
                        if len(sentence.spans[span]) < cell_limit:
                            sentence.spans[span].append(line.strip())
#                        print line,
        if sentence is not None:
            sentence.set_length()
            self.sentences.append(sentence)
            
            

    def read_syntax_cube_flag(self, cell_limit):
        self.sentences = []
        sentence = None
        number = -1
        for line in self.file:
            if len(line.split()) < 6:
                pass
            else:
                if int(line.split()[0]) != number:
                    if sentence is not None:
                        sentence.set_length()
                        self.sentences.append(sentence)
                    sentence = Multiple() # 
                    sentence.number = int(line.split()[0])
                    number = sentence.number
                span = re.search(r"\[([0-9]+)\.\.([0-9]+)\]", line).expand("\g<1> \g<2>")
                span = tuple([int(i) for i in span.split()])
                if len(sentence.spans[span]) < cell_limit:
                    sentence.spans[span].append(line)
        if sentence is not None:
            sentence.set_length()
            self.sentences.append(sentence)
        





class Single():
    def __init__(self):
        self.number = None
        self.spans = {}
        self.length = None

    def set_length(self):
        self.length = max([x[1] for x in self.spans.keys()])
    
    def __str__(self):
        number = str(self.number)
        length = str(self.length)
        spans = "\n"
        for i in self.spans.keys():
            spans += str(i) + " - " + str(self.spans[i]) + "\n"
        return str((number, length, spans))

class Multiple():
    def __init__(self):
        self.number = None
        self.spans = collections.defaultdict(list)
        self.length = None

    def set_length(self):
        self.length = max([x[1] for x in self.spans.keys()])
    
    def __str__(self):
        number = str(self.number)
        length = str(self.length)
        spans = "\n"
        for i in self.spans.keys():
            spans += str(i) + " - " + str(self.spans[i]) + "\n"
        return str((number, length, spans))

#class Syntax():
#    def __init__(self):
#        self.number = None
#        self.spans = {}
#        self.length = None

#    def set_length(self):
#        self.length = max([x[1] for x in self.spans.keys()])
#    
#    def __str__(self):
#        number = str(self.number)
#        length = str(self.length)
#        spans = "\n"
#        for i in self.spans.keys():
#            spans += str(i) + " - " + str(self.spans[i]) + "\n"
#        return str((number, length, spans))
    
#class Syntax_Cube():
#    def __init__(self):
#        self.number = None
#        self.spans = collections.defaultdict(list)
#        self.length = None

#    def set_length(self):
#        self.length = max([x[1] for x in self.spans.keys()])
#    
#    def __str__(self):
#        number = str(self.number)
#        length = str(self.length)
#        spans = "\n"
#        for i in self.spans.keys():
#            spans += str(i) + " - " + str(self.spans[i]) + "\n"
#        return str((number, length, spans))

