from antlr4 import *
from rule.java.JavaLexer import JavaLexer
from rule.java.JavaParser import JavaParser
from tempfile import NamedTemporaryFile
import codecs
from source_code import FileSourceCode

class Parsing:
    def __init__(self, code):
        self.file_code = code
        self.tmp_f = NamedTemporaryFile(delete=False)
        self.parse = self.parse()
        self.parse_tree = self.parse.compilationUnit()
        self.tmp_f.close()

    def parse(self):
        input = FileStream(self.string_to_file(self.file_code),encoding='utf-8')
        lexer = JavaLexer(input)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        return parser
    def string_to_file(self,code):
        self.tmp_f.write(code.encode('utf-8'))
        self.tmp_f.flush()
        self.tmp_f.seek(0)
        return self.tmp_f.name

class CmpParse:
    def __init__(self, code1, code2):
        self.par1 = Parsing(code1)
        self.par2 = Parsing(code2)
        self.tree1 = self.par1.parse_tree
        self.tree2 = self.par2.parse_tree
        if code1==code2:
            self.cmp = True
        else:
            self.cmp = self.compare_tree(self.tree1, self.tree2)
        # self.cmp = self.tree1==self.tree2
        # print("tree1: ",self.tree1)
        # print("tree2: ",self.tree2)

    def compare_tree(self, node1, node2):
        if hasattr(node1, 'parser') != hasattr(node2, 'parser'):
            return False
        if hasattr(node1, "parser"):
            if node1.__class__.__name__ != node2.__class__.__name__:
                return False
        else:
            if JavaLexer.symbolicNames[node1.symbol.type]!=JavaLexer.symbolicNames[node2.symbol.type] or node1.getText()!=node2.getText():
                return False
            return True
        if len(node1.children)!=len(node2.children):
            return False
        cmp = True
        ch1 = node1.getChildren()
        ch2 = node2.getChildren()
        for n1,n2 in zip(ch1,ch2):
            cmp = cmp and self.compare_tree(n1,n2)
            if cmp==False:
                return False
        return cmp

    def compare_code(self,code1,code2):
        return code1==code2
#print(CmpParse('import a;\n import c;','import b;').cmp)