from typing import TextIO
from enum import Enum

from translator.parser import ParserExpr
from translator.sys_exceptions import custom_raise, CustomException


class Commands(Enum):
    FETCH = 1        # FETCH x   - push to stack value of ID x
    STORE = 2        # STORE x   - save to ID x value from top of stack
    PUSH = 3         # PUSH  n   - push to stack n
    POP = 4          # POP       - pop from stack
    ADD = 5          # ADD       - sum two numbers on top of stack
    DIV = 6          # DIV       - div two numbers on top of stack
    MULT = 7         # MULT      - multiply two numbers on top of stack
    SUB = 8          # SUB       - substitute two numbers on top of stack
    LT = 9           # LT        - compare two numbers on top of stack (a < b). Result - 0 или 1
    NON_EQUAL = 10   # NON_EQUAL - compare two numbers on top of stack (a != b). Result - 0 или 1
    EQUAL = 11       # EQUAL     - compare two numbers on top of stack (a == b). Result - 0 или 1
    JZ = 12          # JZ    A   - if 0 on top of stack - jump to A address.
    JNZ = 13         # JNZ   A   - if NOT 0 on top of stack - jump to A address.
    JMP = 14         # JMP   A   - jump to A address
    FINISH = 15      # FINISH    - terminate executing
    INPUT = 16       # INPUT     - get object from standard input
    OUTPUT = 17      # OUTPUT    - print object to standard output
    ARRAY = 18       # ARRAY     - describe new array and fill it with values
    INDEX = 19       # INDEX i   - gets element from array by index i
    RAISE = 20       # RAISE     - raises runtime error with text got as argument


class Compiler:
    CALCULATION_COMMANDS = {
        ParserExpr.ADD: Commands.ADD,
        ParserExpr.SUB: Commands.SUB,
        ParserExpr.MULT: Commands.MULT,
        ParserExpr.DIV: Commands.DIV
    }

    COMPARE_COMMANDS = {
        ParserExpr.LT: Commands.LT,
        ParserExpr.NON_EQUAL: Commands.NON_EQUAL,
        ParserExpr.EQUAL: Commands.EQUAL
    }

    __slots__ = 'logger_file', 'program', 'current_address', 'marks', 'jumps'

    def __init__(self, log_to: TextIO):
        self.logger_file = log_to
        self.program = []
        self.current_address = 0
        self.marks = {}
        self.jumps = {}

    def gen(self, command) -> None:
        self.program.append(command)
        self.current_address += 1

    def compile(self, node) -> list[int, Commands]:
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
            self.gen(Commands.OUTPUT)
        elif node.kind == ParserExpr.RAISE:
            self.compile(node.operands[0])
            self.gen(Commands.RAISE)
        elif node.kind == ParserExpr.STDIN:
            self.gen(Commands.PUSH)
            self.gen(0)
            self.gen(Commands.INPUT)
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
            self.gen(0)
            self.compile(node.operands[1])
            self.program[address_of_branch] = self.current_address
        elif node.kind == ParserExpr.IF2:
            self.compile(node.operands[0])
            self.gen(Commands.JZ)
            addr1 = self.current_address
            self.gen(0)
            self.compile(node.operands[1])
            self.gen(Commands.JMP)
            addr2 = self.current_address
            self.gen(0)
            self.program[addr1] = self.current_address
            self.compile(node.operands[2])
            self.program[addr2] = self.current_address
        elif node.kind == ParserExpr.WHILE:
            addr1 = self.current_address
            self.compile(node.operands[0])
            self.gen(Commands.JZ)
            addr2 = self.current_address
            self.gen(0)
            self.compile(node.operands[1])
            self.gen(Commands.JMP)
            self.gen(addr1)
            self.program[addr2] = self.current_address
        elif node.kind == ParserExpr.SEQ:
            for each_node in node.operands:
                self.compile(each_node)
        elif node.kind == ParserExpr.EXPR:
            self.compile(node.operands[0])
            self.gen(Commands.POP)
        elif node.kind == ParserExpr.GOTO:
            mark = node.operands[0].operands[0]
            mark_id = mark.value
            self.gen(Commands.JMP)
            if self.marks.get(mark_id):
                self.gen(self.marks[mark_id])
            else:
                self.jumps[mark_id] = self.current_address
                self.gen(-1)
        elif node.kind == ParserExpr.MARK:
            mark = self.marks.get(node.value)
            if mark:
                custom_raise(CustomException(f'Mark {node.value} was declared more than once'))
            self.marks[node.value] = self.current_address
            planed_jump = self.jumps.get(node.value)
            if planed_jump:
                self.program[planed_jump] = self.current_address
        elif node.kind == ParserExpr.MAIN:
            self.compile(node.operands[0])
            self.gen(Commands.FINISH)
            self.log()
        return self.program

    def log(self):
        for command in self.program:
            self.logger_file.write(str(command) + '\n')


