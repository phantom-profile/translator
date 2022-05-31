from compiler import Compiler, Commands
from parser import Parser, ParserExpr
from hash_table import HashTable
from lexer import Lexer
from memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY

IFETCH, ISTORE, IPUSH, IPOP, IADD, ISUB, ILT, JZ, JNZ, JMP, HALT = range(11)


class VirtualMachine:
    def __init__(self, memory_allocator: MemoryAllocator):
        self.local_variables: HashTable = HashTable(memory_allocator)

    def run(self, program: list):
        stack = []
        current_address = 0
        while True:
            instruction = program[current_address]
            if current_address < len(program) - 1:
                arg = program[current_address + 1]
            if instruction == Commands.FETCH:
                stack.append(self.local_variables.get(arg))
                current_address += 2
            elif instruction == Commands.STORE:
                self.local_variables.set_pair(arg, stack.pop())
                current_address += 2
            elif instruction == Commands.PUSH:
                stack.append(arg)
                current_address += 2
            elif instruction == Commands.POP:
                stack.append(arg)
                stack.pop()
                current_address += 1
            elif instruction == ParserExpr.ADD:
                stack[-2] += stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == ParserExpr.SUB:
                stack[-2] -= stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == ParserExpr.MULT:
                stack[-2] *= stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == ParserExpr.DIV:
                stack[-2] //= stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == ParserExpr.STDOUT:
                print(stack.pop())
                current_address += 1
            elif instruction == Commands.HALT:
                break

        print('Execution finished with exit code 0')


if __name__ == '__main__':
    read_from = open('prog.txt', 'r')
    log_to = open('lexer_logs.txt', 'w')

    lexer = Lexer(read_from, log_to)
    compiler = Compiler()
    parsed_program = Parser(lexer).parse()

    vm = VirtualMachine(MemoryAllocator(MY_OPERATIVE_MEMORY))
    vm.run(compiler.compile(parsed_program))
