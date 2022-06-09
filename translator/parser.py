from typing import TypeVar, Optional, TextIO
from enum import Enum

from translator.lexer import Lexer, Tokens
from translator.sys_exceptions import CustomException, custom_raise


SelfNode = TypeVar("SelfNode", bound="Node")


class ParserExpr(Enum):
    VAR, CONST, ADD, SUB, LT, SET, IF1, IF2, WHILE, EMPTY, SEQ, \
      EXPR, MAIN, MULT, DIV, NON_EQUAL, EQUAL, STDOUT, STDIN, RAISE, GOTO, MARK = range(22)


class Node:
    __slots__ = 'kind', 'value', 'operands'

    def __init__(self, kind: ParserExpr, value: Optional[int] = None, operands: list[SelfNode] = ()):
        self.kind: ParserExpr = kind
        self.value = value
        self.operands: list[SelfNode] = list(operands)

    def __str__(self):
        self.draw_tree()

    def draw_tree(self, depth=1) -> str:
        nodes = '\t' * depth + 'NODES:\n' if self.operands else ''
        for node in self.operands:
            nodes += '\t' * depth + f'{(node.draw_tree(depth + 1))}'
        return f'{self.kind}, VALUE: {self.value} \n{nodes}'


class Parser:
    __slots__ = 'logger_file', 'lexer'

    def __init__(self, lexer: Lexer, log_to: TextIO):
        self.logger_file = log_to
        self.lexer = lexer

    def parse(self) -> Node:
        self.lexer.next_token()
        node = Node(ParserExpr.MAIN, operands=[self._statement()])
        if self.lexer.translated_token != Tokens.EOF:
            custom_raise(CustomException(f"Invalid statement syntax at line {self.lexer.current_line_count}"))
        self._log(node)
        return node

    # PRIVATE

    def _statement(self) -> Node:
        if self.lexer.translated_token == Tokens.IF:
            node = Node(ParserExpr.IF1)
            self.lexer.next_token()
            node.operands = [
                self._paren_expr(),
                self._statement()
            ]
            if self.lexer.translated_token == Tokens.ELSE:
                node.kind = ParserExpr.IF2
                self.lexer.next_token()
                node.operands.append(self._statement())
        elif self.lexer.translated_token == Tokens.WHILE:
            node = Node(ParserExpr.WHILE)
            self.lexer.next_token()
            node.operands = [self._paren_expr(), self._statement()]
        elif self.lexer.translated_token == Tokens.GOTO:
            node = Node(ParserExpr.GOTO)
            self.lexer.next_token()
            node.operands = [self._statement()]
        elif self.lexer.translated_token == Tokens.PUTS:
            node = Node(ParserExpr.STDOUT)
            self.lexer.next_token()
            node.operands = [self._statement()]
        elif self.lexer.translated_token == Tokens.RAISE:
            node = Node(ParserExpr.RAISE)
            self.lexer.next_token()
            node.operands = [self._term()]
        elif self.lexer.translated_token == Tokens.SEMICOLON:
            node = Node(ParserExpr.EMPTY)
            self.lexer.next_token()
        elif self.lexer.translated_token == Tokens.LBRA:
            node = Node(ParserExpr.EMPTY)
            self.lexer.next_token()
            while self.lexer.translated_token != Tokens.RBRA:
                node.kind = ParserExpr.SEQ
                node.operands.append(self._statement())
            self.lexer.next_token()
        else:
            node = Node(ParserExpr.EXPR, operands=[self._expr()])
            if self.lexer.translated_token != Tokens.SEMICOLON:
                custom_raise(CustomException(f'";" expected at line {self.lexer.current_line_count}'))
            self.lexer.next_token()
        return node

    def _paren_expr(self) -> Node:
        if self.lexer.translated_token != Tokens.LPAR:
            custom_raise(CustomException(f'"(" expected at line {self.lexer.current_line_count}'))
        self.lexer.next_token()
        node = self._statement()
        if self.lexer.translated_token != Tokens.RPAR:
            custom_raise(CustomException(f'")" expected at line {self.lexer.current_line_count}'))
        self.lexer.next_token()
        return node

    def _expr(self) -> Node:
        if self.lexer.translated_token != Tokens.ID:
            return self._test()
        node = self._test()
        if node.kind == ParserExpr.VAR and self.lexer.translated_token == Tokens.SET:
            self.lexer.next_token()
            node = Node(ParserExpr.SET, operands=[node, self._expr()])
        return node

    def _test(self) -> Node:
        lexer_compare = {
            Tokens.LESS: ParserExpr.LT,
            Tokens.NON_EQUAL: ParserExpr.NON_EQUAL,
            Tokens.EQUAL: ParserExpr.EQUAL
        }
        node = self._summa()
        if self.lexer.translated_token in lexer_compare:
            kind = lexer_compare[self.lexer.translated_token]
            self.lexer.next_token()
            node = Node(kind, operands=[node, self._summa()])
        return node

    def _summa(self) -> Node:
        lexer_math = {
            Tokens.PLUS: ParserExpr.ADD,
            Tokens.MINUS: ParserExpr.SUB,
            Tokens.MULT: ParserExpr.MULT,
            Tokens.DIV: ParserExpr.DIV,
        }
        node = self._term()
        while self.lexer.translated_token in lexer_math:
            kind = lexer_math[self.lexer.translated_token]
            self.lexer.next_token()
            node = Node(kind, operands=[node, self._term()])
        return node

    def _term(self) -> Node:
        node = None
        if self.lexer.translated_token == Tokens.ID:
            node = Node(ParserExpr.VAR, self.lexer.value)
            self.lexer.next_token()
        elif self.lexer.translated_token == Tokens.GETS:
            node = Node(ParserExpr.STDIN, self.lexer.value)
            self.lexer.next_token()
        elif self.lexer.translated_token in (Tokens.NUM, Tokens.STRING):
            node = Node(ParserExpr.CONST, self.lexer.value)
            self.lexer.next_token()
        elif self.lexer.translated_token == Tokens.MARK:
            node = Node(ParserExpr.MARK, self.lexer.value)
            self.lexer.next_token()
        if node is not None:
            return node
        else:
            return self._paren_expr()

    def _log(self, node) -> None:
        self.logger_file.write(node.draw_tree())


if __name__ == '__main__':
    p = Parser(Lexer(open('../prog.txt', 'r')))
    print(p.parse().draw_tree())
