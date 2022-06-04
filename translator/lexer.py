from string import ascii_letters, digits
from typing import TextIO
from enum import Enum

from translator.sys_exceptions import CustomException, custom_raise


class Tokens(Enum):
    NUM, ID, IF, ELSE, WHILE, LBRA, RBRA, LPAR, RPAR, PLUS, MINUS, MULT, DIV, LESS, \
      SET, NON_EQUAL, SEMICOLON, PUTS, EQUAL, QUOTE, STRING, GETS, EOF = range(23)


class Lexer:
    NUM, ID, IF, ELSE, WHILE, LBRA, RBRA, LPAR, RPAR, PLUS, MINUS, MULT, DIV, LESS, \
      SET, NON_EQUAL, SEMICOLON, PUTS, EQUAL, QUOTE, STRING, GETS, EOF = Tokens

    LANGUAGE_SYMBOLS = {
        '{': LBRA,
        '}': RBRA,
        '=': SET,
        ';': SEMICOLON,
        '(': LPAR,
        ')': RPAR,
        '+': PLUS,
        '-': MINUS,
        '*': MULT,
        '/': DIV,
        '<': LESS,
        '~': NON_EQUAL,
        '^': EQUAL,
        '"': QUOTE,
    }

    RESERVED_WORDS = {
        'if': IF,
        'else': ELSE,
        'while': WHILE,
        'puts': PUTS,
        'gets': GETS,
    }

    def __init__(self, program_file: TextIO):
        self.hash_table = hash
        self.program_file = program_file
        self.logger_file = open('logs/lexer_logs.txt', 'w')
        self.current_char = ''
        self.value = None
        self.translated_token = None
        self.greedy_perform = False

    def get_char(self):
        char = self.program_file.read(1)
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
            elif self.translated_token != self.EOF:
                custom_raise(CustomException(f'Unexpected symbol: {self.current_char}'))
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
        self.translated_token = self.STRING
        self.value = string_const

    def tokenize_number(self):
        value = ''
        while self.current_char in digits + '.':
            value += self.current_char
            self.get_char()
            self.greedy_perform = True
        float_value = float(value)
        self.value = int(float_value) if int(float_value) == float_value else float_value
        self.translated_token = self.NUM

    def tokenize_ids_and_reserved_words(self):
        ident = ''
        while self.current_char in ascii_letters + '_':
            ident += self.current_char.lower()
            self.get_char()
            self.greedy_perform = True
        if ident in self.RESERVED_WORDS:
            self.translated_token = self.RESERVED_WORDS[ident]
        else:
            self.translated_token = self.ID
            self.value = ident

    def return_end_of_input(self):
        if self.greedy_perform:
            return

        self.get_char()
        if len(self.current_char) == 0:
            self.translated_token = self.EOF

    def skip_space(self):
        while self.current_char in (' ', '\n', '\t'):
            self.get_char()

    def log_token(self):
        log = f'{self.translated_token} = {self.value}\n' if self.value is not None else f'{self.translated_token}\n'
        self.logger_file.write(log)

    def __str__(self):
        return f'LAST TRANSLATED: {self.translated_token} NOW: {self.current_char if self.current_char else "EMPTY"}'
