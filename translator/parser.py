from typing import TypeVar, Optional
from enum import Enum

from translator.lexer import Lexer
from translator.sys_exceptions import CustomException, custom_raise


SelfNode = TypeVar("SelfNode", bound="Node")


class ParserExpr(Enum):
    VAR, CONST, ADD, SUB, LT, SET, IF1, IF2, WHILE, EMPTY, SEQ, \
      EXPR, MAIN, MULT, DIV, NON_EQUAL, EQUAL, STDOUT, STDIN = range(19)


class Node:
    __slots__ = 'kind', 'value', 'operands'

    def __init__(self, kind: ParserExpr, value: Optional[int] = None, operands: list[SelfNode] = ()):
        self.kind: ParserExpr = kind
        self.value = value
        self.operands: list[SelfNode] = list(operands)

    def draw_tree(self, depth=1) -> str:
        nodes = '\t' * depth + 'NODES:\n' if self.operands else ''
        for node in self.operands:
            nodes += '\t' * depth + f'{(node.draw_tree(depth + 1))}'
        return f'{self.kind}, VALUE: {self.value} \n{nodes}'


class Parser:
    __slots__ = 'logger_file', 'lexer'

    def __init__(self, lexer: Lexer):
        self.logger_file = open('logs/parser_logs.txt', 'w')
        self.lexer = lexer

    def parse(self) -> Node:
        self.lexer.next_token()
        node = Node(ParserExpr.MAIN, operands=[self._statement()])
        if self.lexer.translated_token != Lexer.EOF:
            custom_raise(CustomException("Invalid statement syntax"))
        self._log(node)
        return node

    # PRIVATE

    def _statement(self) -> Node:
        if self.lexer.translated_token == Lexer.IF:
            node = Node(ParserExpr.IF1)
            self.lexer.next_token()
            node.operands = [
                self._paren_expr(),
                self._statement()
            ]
            if self.lexer.translated_token == Lexer.ELSE:
                node.kind = ParserExpr.IF2
                self.lexer.next_token()
                node.operands.append(self._statement())
        elif self.lexer.translated_token == Lexer.WHILE:
            node = Node(ParserExpr.WHILE)
            self.lexer.next_token()
            node.operands = [self._paren_expr(), self._statement()]
        elif self.lexer.translated_token == Lexer.PUTS:
            node = Node(ParserExpr.STDOUT)
            self.lexer.next_token()
            node.operands = [self._statement()]
        elif self.lexer.translated_token == Lexer.SEMICOLON:
            node = Node(ParserExpr.EMPTY)
            self.lexer.next_token()
        elif self.lexer.translated_token == Lexer.LBRA:
            node = Node(ParserExpr.EMPTY)
            self.lexer.next_token()
            while self.lexer.translated_token != Lexer.RBRA:
                node.kind = ParserExpr.SEQ
                node.operands.append(self._statement())
            self.lexer.next_token()
        else:
            node = Node(ParserExpr.EXPR, operands=[self.expr()])
            if self.lexer.translated_token != Lexer.SEMICOLON:
                custom_raise(CustomException('";" expected'))
            self.lexer.next_token()
        return node

    def _paren_expr(self) -> Node:
        if self.lexer.translated_token != Lexer.LPAR:
            custom_raise(CustomException('"(" expected'))
        self.lexer.next_token()
        node = self._statement()
        if self.lexer.translated_token != Lexer.RPAR:
            custom_raise(CustomException('"(" expected'))
        self.lexer.next_token()
        return node

    def expr(self) -> Node:
        if self.lexer.translated_token != Lexer.ID:
            return self._test()
        node = self._test()
        if node.kind == ParserExpr.VAR and self.lexer.translated_token == Lexer.SET:
            self.lexer.next_token()
            node = Node(ParserExpr.SET, operands=[node, self.expr()])
        return node

    def _test(self) -> Node:
        lexer_compare = {
            Lexer.LESS: ParserExpr.LT,
            Lexer.NON_EQUAL: ParserExpr.NON_EQUAL,
            Lexer.EQUAL: ParserExpr.EQUAL
        }
        node = self._summa()
        if self.lexer.translated_token in lexer_compare:
            kind = lexer_compare[self.lexer.translated_token]
            self.lexer.next_token()
            node = Node(kind, operands=[node, self._summa()])
        return node

    def _summa(self) -> Node:
        lexer_math = {
            Lexer.PLUS: ParserExpr.ADD,
            Lexer.MINUS: ParserExpr.SUB,
            Lexer.MULT: ParserExpr.MULT,
            Lexer.DIV: ParserExpr.DIV,
        }
        node = self._term()
        while self.lexer.translated_token in lexer_math:
            kind = lexer_math[self.lexer.translated_token]
            self.lexer.next_token()
            node = Node(kind, operands=[node, self._term()])
        return node

    def _term(self) -> Node:
        if self.lexer.translated_token == Lexer.ID:
            node = Node(ParserExpr.VAR, self.lexer.value)
            self.lexer.next_token()
            return node
        elif self.lexer.translated_token == Lexer.GETS:
            node = Node(ParserExpr.STDIN, self.lexer.value)
            self.lexer.next_token()
            return node
        elif self.lexer.translated_token in (Lexer.NUM, Lexer.STRING):
            node = Node(ParserExpr.CONST, self.lexer.value)
            self.lexer.next_token()
            return node
        else:
            return self._paren_expr()

    def _log(self, node) -> None:
        self.logger_file.write(node.draw_tree())
