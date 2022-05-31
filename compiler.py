from enum import Enum
from pprint import pprint

from hash_table import HashTable
from sys_exceptions import custom_raise, CustomException
from memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY
from parser import ParserExpr, Parser, Lexer

# PUT x - положить переменную в хэш
# GET x - get var from hash
# CALC a b - calculate a and b
# OUT x - print x
# FINISH - terminate program with code 0


class Instructions(Enum):
    PUT = 1
    GET = 2
    OUT = 3
    CALC = 4
    FINISH = 5


class Commands(Enum):
    FETCH, STORE, PUSH, POP, ADD, SUB, LT, JZ, JNZ, JMP, HALT = range(11)


class Compiler:

    def __init__(self):
        self.program = []
        self.pc = 0

    def gen(self, command):
        self.program.append(command)
        self.pc = self.pc + 1

    def compile(self, node):
        if node.kind == ParserExpr.VAR:
            self.gen(Commands.FETCH)
            self.gen(node.value)
        elif node.kind == ParserExpr.CONST:
            self.gen(Commands.PUSH)
            self.gen(node.value)
        elif node.kind in (ParserExpr.ADD, ParserExpr.SUB, ParserExpr.DIV, ParserExpr.MULT):
            self.compile(node.operands[0])
            self.compile(node.operands[1])
            self.gen(node.kind)
        elif node.kind == ParserExpr.STDOUT:
            self.compile(node.operands[0])
            self.gen(ParserExpr.STDOUT)
        elif node.kind == ParserExpr.SET:
            self.compile(node.operands[1])
            self.gen(Commands.STORE)
            self.gen(node.operands[0].value)
        elif node.kind == ParserExpr.SEQ:
            for each_node in node.operands:
                self.compile(each_node)
        elif node.kind == ParserExpr.EXPR:
            self.compile(node.operands[0])
            self.gen(Commands.POP)
        elif node.kind == ParserExpr.MAIN:
            self.compile(node.operands[0])
            self.gen(Commands.HALT)
        return self.program


if __name__ == '__main__':
    read_from = open('prog.txt', 'r')
    log_to = open('lexer_logs.txt', 'w')

    lexer = Lexer(read_from, log_to)
    compiler = Compiler()
    parsed_program = Parser(lexer).parse()
    pprint(compiler.compile(parsed_program))
