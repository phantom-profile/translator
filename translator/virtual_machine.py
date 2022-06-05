from typing import TextIO

from translator.compiler import Commands
from translator.hash_table import HashTable
from translator.memalloc import MemoryAllocator
from translator.stack_deck_queue import Stack
from translator.sys_exceptions import CustomException, custom_raise


class VirtualMachine:
    __slots__ = 'logger_file', 'local_variables', 'stack'

    SYSTEM_FUNCTIONS = ['puts', 'gets', 'raise']

    def __init__(self, memory_allocator: MemoryAllocator, log_to: TextIO):
        self.logger_file = log_to
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
                if arg in self.SYSTEM_FUNCTIONS:
                    custom_raise(
                        CustomException(
                            f'invalid operation. "{arg}" is a system functions. finished with code 1'
                        )
                    )
                    break
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
                if self.stack[-1] == 0:
                    custom_raise(CustomException('division by zero detected'))
                    break
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
            elif instruction == Commands.ARRAY:
                new_array = []
                length = self.stack.pop()
                for element in range(length):
                    new_array.append(self.stack.pop())
                self.stack.push(list(reversed(new_array)))
                current_address += 1
            elif instruction == Commands.RAISE:
                custom_raise(
                    CustomException(
                        f'raised an exception: "{self.stack.pop()}"', 2
                    )
                )
                break
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
                print('Execution finished with exit code 0')
                break

    def log(self, instruction):
        self.logger_file.write(f'Currently {instruction} executing\n')
