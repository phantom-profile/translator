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
            elif instruction == ILT:
                if stack[-2] < stack[-1]:
                    stack[-2] = 1
                else:
                    stack[-2] = 0
                stack.pop()
                current_address += 1
            elif instruction == JZ:
                if stack.pop() == 0:
                    current_address = arg
                else:
                    current_address += 2
            elif instruction == JNZ:
                if stack.pop() != 0:
                    current_address = arg
                else:
                    current_address += 2
            elif instruction == JMP:
                current_address = arg
            elif instruction == HALT:
                break

        print('Execution finished.')
        print(self.local_variables)


if __name__ == '__main__':
    pass
    # l = Lexer()
    # p = Parser(l)
    #
    # ast = p.parse()
    #
    # c = Compiler()
    # program = c.compile(ast)
    #
    # vm = VirtualMachine()
    # vm.run(program)
