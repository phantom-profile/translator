from translator.compiler import Commands
from translator.hash_table import HashTable
from translator.memalloc import MemoryAllocator
from translator.stack_deck_queue import Stack


class VirtualMachine:
    __slots__ = 'logger_file', 'local_variables', 'stack'

    def __init__(self, memory_allocator: MemoryAllocator):
        self.logger_file = open('logs/virtual_machine_logs.txt', 'w')
        self.local_variables: HashTable = HashTable(memory_allocator)
        self.stack = Stack(memory_allocator)

    def run(self, program: list) -> None:
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
                result = self.stack[-2] / self.stack[-1]
                self.stack[-2] = int(result) if int(result) == result else result
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.LT:
                self.stack[-2] = 1 if self.stack[-2] < self.stack[-1] else 0
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.NON_EQUAL:
                self.stack[-2] = 1 if self.stack[-2] != self.stack[-1] else 0
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.EQUAL:
                self.stack[-2] = 1 if self.stack[-2] == self.stack[-1] else 0
                self.stack.pop()
                current_address += 1
            elif instruction == Commands.JZ:
                current_address = arg if self.stack.pop() == 0 else current_address + 2
            elif instruction == Commands.JNZ:
                current_address = arg if self.stack.pop() != 0 else current_address + 2
            elif instruction == Commands.JMP:
                current_address = arg
            elif instruction == Commands.INPUT:
                value = input().strip()
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        value = str(value)
                self.stack[-1] = value
                current_address += 1
            elif instruction == Commands.OUTPUT:
                print(self.stack.pop())
                current_address += 1
            elif instruction == Commands.FINISH:
                break

        print('Execution finished with exit code 0')

    def log(self, instruction):
        self.logger_file.write(f'Currently {instruction} executing\n')
