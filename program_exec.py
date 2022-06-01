from translator.memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY
from translator.lexer import Lexer
from translator.parser import Parser
from translator.compiler import Compiler
from translator.virtual_machine import VirtualMachine


def main():
    read_from = open('prog.txt', 'r')

    memory_allocator = MemoryAllocator(MY_OPERATIVE_MEMORY)
    lexer = Lexer(read_from)
    parser = Parser(lexer)
    compiler = Compiler()
    vm = VirtualMachine(memory_allocator)

    parsed_program = parser.parse()
    compiled_program = compiler.compile(parsed_program)

    vm.run(compiled_program)


if __name__ == '__main__':
    main()
