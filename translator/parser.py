from typing import TypeVar, Optional
from enum import Enum

from translator.lexer import Lexer
from translator.sys_exceptions import CustomException, custom_raise


SelfNode = TypeVar("SelfNode", bound="Node")


class ParserExpr(Enum):
    VAR, CONST, ADD, SUB, LT, SET, IF1, IF2, WHILE, EMPTY, SEQ, \
      EXPR, MAIN, MULT, DIV, NOEQUAL, SAME_AS, STDOUT = range(18)


class Node:
    def __init__(self, kind: ParserExpr, value: Optional[int] = None, operands: list[SelfNode] = ()):
        self.kind: ParserExpr = kind
        self.value = value
        self.operands: list[SelfNode] = list(operands)

    def draw_tree(self, depth=1):
        nodes = '\t' * depth + 'NODES:\n' if self.operands else ''
        for node in self.operands:
            nodes += '\t' * depth + f'{(node.draw_tree(depth + 1))}'
        return f'{self.kind}, VALUE: {self.value} \n{nodes}'


class Parser:
    def __init__(self, lexer: Lexer):
        self.logger_file = open('logs/parser_logs.txt', 'w')
        self.lexer = lexer

    def parse(self) -> Node:
        self.lexer.next_token()
        node = Node(ParserExpr.MAIN, operands=[self.statement()])
        if self.lexer.translated_token != Lexer.EOF:
            custom_raise(CustomException("Invalid statement syntax"))
        self.log(node)
        return node

    def statement(self) -> Node:
        if self.lexer.translated_token == Lexer.IF:
            node = Node(ParserExpr.IF1)
            self.lexer.next_token()
            node.operands = [
                self.paren_expr(),
                self.statement()
            ]
            if self.lexer.translated_token == Lexer.ELSE:
                node.kind = ParserExpr.IF2
                self.lexer.next_token()
                node.operands.append(self.statement())
        elif self.lexer.translated_token == Lexer.WHILE:
            node = Node(ParserExpr.WHILE)
            self.lexer.next_token()
            node.operands = [self.paren_expr(), self.statement()]
        elif self.lexer.translated_token == Lexer.PUTS:
            node = Node(ParserExpr.STDOUT)
            self.lexer.next_token()
            node.operands = [self.statement()]
        elif self.lexer.translated_token == Lexer.SEMICOLON:
            node = Node(ParserExpr.EMPTY)
            self.lexer.next_token()
        elif self.lexer.translated_token == Lexer.LBRA:
            node = Node(ParserExpr.EMPTY)
            self.lexer.next_token()
            while self.lexer.translated_token != Lexer.RBRA:
                node.kind = ParserExpr.SEQ
                node.operands.append(self.statement())
            self.lexer.next_token()
        else:
            node = Node(ParserExpr.EXPR, operands=[self.expr()])
            if self.lexer.translated_token != Lexer.SEMICOLON:
                custom_raise(CustomException('";" expected'))
            self.lexer.next_token()
        return node

    def paren_expr(self) -> Node:
        if self.lexer.translated_token != Lexer.LPAR:
            custom_raise(CustomException('"(" expected'))
        self.lexer.next_token()
        node = self.statement()
        if self.lexer.translated_token != Lexer.RPAR:
            custom_raise(CustomException('"(" expected'))
        self.lexer.next_token()
        return node

    def expr(self):
        if self.lexer.translated_token != Lexer.ID:
            return self.test()
        node = self.test()
        if node.kind == ParserExpr.VAR and self.lexer.translated_token == Lexer.EQUAL:
            self.lexer.next_token()
            node = Node(ParserExpr.SET, operands=[node, self.expr()])
        return node

    def test(self):
        lexer_compare = {
            Lexer.LESS: ParserExpr.LT,
            Lexer.NOEQUAL: ParserExpr.NOEQUAL,
            Lexer.SAME_AS: ParserExpr.SAME_AS
        }
        node = self.summa()
        if self.lexer.translated_token in lexer_compare:
            kind = lexer_compare[self.lexer.translated_token]
            self.lexer.next_token()
            node = Node(kind, operands=[node, self.summa()])
        return node

    def summa(self):
        lexer_math = {
            Lexer.PLUS: ParserExpr.ADD,
            Lexer.MINUS: ParserExpr.SUB,
            Lexer.MULT: ParserExpr.MULT,
            Lexer.DIV: ParserExpr.DIV,
        }
        node = self.term()
        while self.lexer.translated_token in lexer_math:
            kind = lexer_math[self.lexer.translated_token]
            self.lexer.next_token()
            node = Node(kind, operands=[node, self.term()])
        return node

    def term(self):
        if self.lexer.translated_token == Lexer.ID:
            node = Node(ParserExpr.VAR, self.lexer.value)
            self.lexer.next_token()
            return node
        elif self.lexer.translated_token == Lexer.NUM:
            node = Node(ParserExpr.CONST, self.lexer.value)
            self.lexer.next_token()
            return node
        else:
            return self.paren_expr()

    def log(self, node):
        self.logger_file.write(node.draw_tree())
