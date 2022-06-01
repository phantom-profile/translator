from enum import Enum
from pprint import pprint

from parser import ParserExpr, Parser, Lexer


class Instructions(Enum):
    PUT = 1
    GET = 2
    OUT = 3
    CALC = 4
    FINISH = 5


class Commands(Enum):
    FETCH, STORE, PUSH, POP, ADD, PLUS, DIV, MULT, SUB, LT, NOEQUAL, SAME_AS, JZ, JNZ, JMP, HALT = range(16)


class Compiler:
    CALCULATION_COMMANDS = {
        ParserExpr.ADD: Commands.ADD,
        ParserExpr.SUB: Commands.SUB,
        ParserExpr.MULT: Commands.MULT,
        ParserExpr.DIV: Commands.DIV
    }

    COMPARE_COMMANDS = {
        ParserExpr.LT: Commands.LT,
        ParserExpr.NOEQUAL: Commands.NOEQUAL,
        ParserExpr.SAME_AS: Commands.SAME_AS
    }

    def __init__(self):
        self.logger_file = open('logs/compile_logs.txt', 'w')
        self.program = []
        self.current_address = 0

    def gen(self, command):
        self.program.append(command)
        self.current_address += 1

    def compile(self, node):
        if node.kind == ParserExpr.VAR:
            self.gen(Commands.FETCH)
            self.gen(node.value)
        elif node.kind == ParserExpr.CONST:
            self.gen(Commands.PUSH)
            self.gen(node.value)
        elif node.kind in self.CALCULATION_COMMANDS:
            self.compile(node.operands[0])
            self.compile(node.operands[1])
            self.gen(self.CALCULATION_COMMANDS[node.kind])
        elif node.kind == ParserExpr.STDOUT:
            self.compile(node.operands[0])
            self.gen(ParserExpr.STDOUT)
        elif node.kind == ParserExpr.SET:
            self.compile(node.operands[1])
            self.gen(Commands.STORE)
            self.gen(node.operands[0].value)
        elif node.kind in self.COMPARE_COMMANDS:
            self.compile(node.operands[0])
            self.compile(node.operands[1])
            self.gen(self.COMPARE_COMMANDS[node.kind])
        elif node.kind == ParserExpr.IF1:
            self.compile(node.operands[0])
            self.gen(Commands.JZ)
            address_of_branch = self.current_address
            # JZ переходит к этому адресу всегда
            self.gen(0)
            # собираем ветку
            self.compile(node.operands[1])
            # после того как будет известно, что за ветка скомпилирована, меняем адрес JZ на фактический
            self.program[address_of_branch] = self.current_address
        elif node.kind == ParserExpr.SEQ:
            for each_node in node.operands:
                self.compile(each_node)
        elif node.kind == ParserExpr.EXPR:
            self.compile(node.operands[0])
            self.gen(Commands.POP)
        elif node.kind == ParserExpr.MAIN:
            self.compile(node.operands[0])
            self.gen(Commands.HALT)
            self.log()
        return self.program

    def log(self):
        for command in self.program:
            self.logger_file.write(str(command) + '\n')
