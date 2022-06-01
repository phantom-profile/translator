from compiler import Compiler, Commands
from parser import Parser, ParserExpr
from hash_table import HashTable
from lexer import Lexer
from memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY

IFETCH, ISTORE, IPUSH, IPOP, IADD, ISUB, ILT, JZ, JNZ, JMP, HALT = range(11)


class VirtualMachine:
    def __init__(self, memory_allocator: MemoryAllocator):
        self.logger_file = open('logs/virtual_machine_logs.txt', 'w')
        self.local_variables: HashTable = HashTable(memory_allocator)

    def run(self, program: list):
        stack = []
        current_address = 0
        while True:
            instruction = program[current_address]
            self.log(instruction)
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
            elif instruction == Commands.ADD:
                stack[-2] += stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == Commands.SUB:
                stack[-2] -= stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == Commands.MULT:
                stack[-2] *= stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == Commands.DIV:
                stack[-2] //= stack[-1]
                stack.pop()
                current_address += 1
            elif instruction == Commands.LT:
                stack[-2] = 1 if stack[-2] < stack[-1] else 0
                stack.pop()
                current_address += 1
            elif instruction == Commands.NOEQUAL:
                stack[-2] = 1 if stack[-2] != stack[-1] else 0
                stack.pop()
                current_address += 1
            elif instruction == Commands.SAME_AS:
                stack[-2] = 1 if stack[-2] == stack[-1] else 0
                stack.pop()
                current_address += 1
            elif instruction == Commands.JZ:
                current_address = arg if stack.pop() == 0 else current_address + 2
            elif instruction == ParserExpr.STDOUT:
                print(stack.pop())
                current_address += 1
            elif instruction == Commands.HALT:
                break

        print('Execution finished with exit code 0')

    def log(self, instruction):
        self.logger_file.write(f'Currently {instruction} executing\n')


if __name__ == '__main__':
    read_from = open('prog.txt', 'r')

    lexer = Lexer(read_from)
    compiler = Compiler()
    parsed_program = Parser(lexer).parse()

    vm = VirtualMachine(MemoryAllocator(MY_OPERATIVE_MEMORY))
    vm.run(compiler.compile(parsed_program))
