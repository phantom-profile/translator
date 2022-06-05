from translator.memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY
from translator.lexer import Lexer
from translator.parser import Parser
from translator.compiler import Compiler
from translator.virtual_machine import VirtualMachine


def main(program_file_name: str, logs_folder: str = 'logs/'):
    log_files = {
        'memory_allocator': open(f'{logs_folder}memory_allocator_logs.txt', 'w'),
        'lexer': open(f'{logs_folder}lexer_logs.txt', 'w'),
        'parser': open(f'{logs_folder}parser_logs.txt', 'w'),
        'compiler': open(f'{logs_folder}compile_logs.txt', 'w'),
        'virtual_machine': open(f'{logs_folder}virtual_machine_logs.txt', 'w'),
    }

    read_from = open(program_file_name, 'r')

    memory_allocator = MemoryAllocator(MY_OPERATIVE_MEMORY, log_to=log_files['memory_allocator'])
    lexer = Lexer(read_from, log_to=log_files['lexer'])
    parser = Parser(lexer, log_to=log_files['parser'])
    compiler = Compiler(log_to=log_files['compiler'])
    vm = VirtualMachine(memory_allocator, log_to=log_files['virtual_machine'])

    parsed_program = parser.parse()
    compiled_program = compiler.compile(parsed_program)

    vm.run(compiled_program)

    for file in log_files.values():
        file.close()


if __name__ == '__main__':
    main('prog.txt')
