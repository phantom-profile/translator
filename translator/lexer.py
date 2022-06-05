from string import ascii_letters, digits
from typing import TextIO
from enum import Enum

from translator.sys_exceptions import CustomException, custom_raise


class Tokens(Enum):
    NUM, ID, IF, ELSE, WHILE, LBRA, RBRA, LPAR, RPAR, PLUS, MINUS, MULT, DIV, LESS, \
      SET, NON_EQUAL, SEMICOLON, PUTS, EQUAL, QUOTE, STRING, GETS, EOF, LARRBR, RARRBR, DOT, RAISE = range(27)


class Lexer:
    LANGUAGE_SYMBOLS = {
        '{': Tokens.LBRA,
        '}': Tokens.RBRA,
        '=': Tokens.SET,
        ';': Tokens.SEMICOLON,
        '(': Tokens.LPAR,
        ')': Tokens.RPAR,
        '+': Tokens.PLUS,
        '-': Tokens.MINUS,
        '*': Tokens.MULT,
        '/': Tokens.DIV,
        '<': Tokens.LESS,
        '~': Tokens.NON_EQUAL,
        '^': Tokens.EQUAL,
        '"': Tokens.QUOTE,
        '[': Tokens.LARRBR,
        ']': Tokens.RARRBR,
        '.': Tokens.DOT,
    }

    RESERVED_WORDS = {
        'if': Tokens.IF,
        'else': Tokens.ELSE,
        'while': Tokens.WHILE,
        'puts': Tokens.PUTS,
        'gets': Tokens.GETS,
        'raise': Tokens.RAISE,
    }

    __slots__ = (
        'hash_table',
        'program_file',
        'logger_file',
        'current_char',
        'value',
        'translated_token',
        'greedy_perform',
        'current_line_count',
        'current_char_count',
    )

    def __init__(self, program_file: TextIO, log_to: TextIO):
        self.hash_table = hash
        self.program_file = program_file
        self.logger_file = log_to
        self.current_char = ''
        self.value = None
        self.translated_token = None
        self.greedy_perform = False
        self.current_line_count = 1
        self.current_char_count = 0

    def get_char(self):
        char = self.program_file.read(1)
        self.current_char_count += 1
        if char == '\n':
            self.current_line_count += 1
            self.current_char_count = 0
        self.current_char = char if char else ''

    def next_token(self):
        self.value = None
        self.translated_token = None

        while self.translated_token is None:
            self.return_end_of_input()
            self.skip_space()
            if self.current_char in self.LANGUAGE_SYMBOLS:
                self.tokenize_special_symbol()
            elif self.current_char.isdigit():
                self.tokenize_number()
            elif self.current_char.isalpha():
                self.tokenize_ids_and_reserved_words()
            elif self.translated_token != Tokens.EOF:
                custom_raise(
                    CustomException(
                        f'Unexpected symbol at {self.current_line_count}:{self.current_char_count}: {self.current_char}'
                    )
                )
            self.log_token()

    def tokenize_special_symbol(self):
        self.greedy_perform = False
        if self.current_char == '"':
            return self.tokenize_string()
        self.translated_token = self.LANGUAGE_SYMBOLS[self.current_char]

    def tokenize_string(self):
        string_const = ''
        self.get_char()
        while self.current_char != '"':
            string_const += self.current_char
            self.get_char()
            self.greedy_perform = True
        self.get_char()
        self.translated_token = Tokens.STRING
        self.value = string_const

    def tokenize_number(self):
        value = ''
        while self.current_char in digits + '.':
            value += self.current_char
            self.get_char()
            self.greedy_perform = True
        float_value = float(value)
        self.value = int(float_value) if int(float_value) == float_value else float_value
        self.translated_token = Tokens.NUM

    def tokenize_ids_and_reserved_words(self):
        ident = ''
        while self.current_char in ascii_letters + '_':
            ident += self.current_char.lower()
            self.get_char()
            self.greedy_perform = True
        if ident in self.RESERVED_WORDS:
            self.translated_token = self.RESERVED_WORDS[ident]
        else:
            self.translated_token = Tokens.ID
            self.value = ident

    def return_end_of_input(self):
        if self.greedy_perform:
            return

        self.get_char()
        if len(self.current_char) == 0:
            self.translated_token = Tokens.EOF

    def skip_space(self):
        while self.current_char in (' ', '\n', '\t'):
            self.get_char()

    def log_token(self):
        log = f'{self.translated_token} = {self.value}\n' if self.value is not None else f'{self.translated_token}\n'
        self.logger_file.write(log)

    def __str__(self):
        return f'LAST TRANSLATED: {self.translated_token} NOW: {self.current_char if self.current_char else "EMPTY"}'


if __name__ == '__main__':
    read_from = open('../prog.txt', 'r')
    lexer = Lexer(read_from)
    while lexer.translated_token != Tokens.EOF:
        lexer.next_token()
