from typing import NamedTuple, Any, Optional
from enum import Enum

from stack_deck_queue import Stack
from hash_table import HashTable
from sys_exceptions import custom_raise, CustomException
from memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY
from parser import ParserExpr, Node

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
        # elif node.kind == ParserExpr.LT:
        #     self.compile(node.operands[0])
        #     self.compile(node.operands[1])
        #     self.gen(ParserExpr.LT)
        elif node.kind == ParserExpr.SET:
            self.compile(node.operands[0])
            self.gen(Commands.STORE)
            self.gen(node.operands[1].value)
        elif node.kind == ParserExpr.IF1:
            self.compile(node.operands[0])
            self.gen(Commands.JZ)
            addr = self.pc
            self.gen(0)
            self.compile(node.operands[1])
            self.program[addr] = self.pc
        elif node.kind == ParserExpr.IF2:
            self.compile(node.operands[0])
            self.gen(Commands.JZ)
            addr1 = self.pc
            self.gen(0)
            self.compile(node.operands[1])
            self.gen(Commands.JMP)
            addr2 = self.pc
            self.gen(0)
            self.program[addr1] = self.pc
            self.compile(node.operands[2])
            self.program[addr2] = self.pc
        elif node.kind == ParserExpr.WHILE:
            addr1 = self.pc
            self.compile(node.operands[0])
            self.gen(Commands.JZ)
            addr2 = self.pc
            self.gen(0)
            self.compile(node.operands[1])
            self.gen(Commands.JMP)
            self.gen(addr1)
            self.program[addr2] = self.pc
        elif node.kind == ParserExpr.SEQ:
            self.compile(node.operands[0])
            self.compile(node.operands[1])
        elif node.kind == ParserExpr.EXPR:
            self.compile(node.operands[0])
            self.gen(Commands.POP)
        elif node.kind == ParserExpr.MAIN:
            self.compile(node.operands[0])
            self.gen(Commands.HALT)
        return self.program
