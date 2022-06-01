from translator.compiler import Commands
from translator.parser import ParserExpr
from translator.hash_table import HashTable
from translator.memalloc import MemoryAllocator
from translator.stack_deck_queue import Stack


class VirtualMachine:
    def __init__(self, memory_allocator: MemoryAllocator):
        self.logger_file = open('logs/virtual_machine_logs.txt', 'w')
        self.local_variables: HashTable = HashTable(memory_allocator)
        self.stack = Stack(memory_allocator)

    def run(self, program: list):
        current_address = 0
        while True:
            instruction = program[current_address]
            self.log(instruction)
            if current_address < len(program) - 1:
                arg = program[current_address + 1]
            if instruction == Commands.FETCH:
                self.stack.push(self.local_variables.get(arg))
                current_address += 2
            elif instruction == Commands.STORE:
                self.local_variables.set_pair(arg, self.stack.pop())
                current_address += 2
            elif instruction == Commands.PUSH:
                self.stack.push(arg)
                current_address += 2
            elif instruction == Commands.POP:
                self.stack.push(arg)
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.ADD:
                self.stack[-2] += self.stack[-1]
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.SUB:
                self.stack[-2] -= self.stack[-1]
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.MULT:
                self.stack[-2] *= self.stack[-1]
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.DIV:
                self.stack[-2] //= self.stack[-1]
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.LT:
                self.stack[-2] = 1 if self.stack[-2] < self.stack[-1] else 0
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.NOEQUAL:
                self.stack[-2] = 1 if self.stack[-2] != self.stack[-1] else 0
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.SAME_AS:
                self.stack[-2] = 1 if self.stack[-2] == self.stack[-1] else 0
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.JZ:
                current_address = arg if self.stack.pop() == 0 else current_address + 2
            elif instruction == ParserExpr.STDOUT:
                print(self.stack.pop())
                current_address += 1
            elif instruction == Commands.HALT:
                break

        print('Execution finished with exit code 0')

    def log(self, instruction):
        self.logger_file.write(f'Currently {instruction} executing\n')