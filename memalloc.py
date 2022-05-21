from typing import List, Any
from sys import getsizeof

from sys_exceptions import CustomException, custom_raise


MY_OPERATIVE_MEMORY = 8 * 1024 * 1024 * 1024


class Block:
    def __init__(self, start: int, size: int, is_used: bool):
        self.size: int = size
        self.is_used: bool = is_used
        self.start: int = start
        self.finish: int = self.start + self.size - 1

    def free(self):
        self.is_used = False

    def use(self):
        self.is_used = True

    def __str__(self):
        return f'|{self.start} - {self.finish}, size: {self.size}, is_used: {self.is_used}| '


class MemoryAllocator:
    def __init__(self, memory_size: int):
        self.memory_size: int = memory_size
        self.blocks: List[Block] = []

    def allocate(self, any_object: Any) -> None:
        size = getsizeof(any_object)

        self._run_of_memory_alert(size)

        insertion_place = None
        for block in self._unused_blocks():
            if size == 0:
                return
            if size >= block.size:
                block.use()
                self.memory_size -= block.size
                size -= block.size
            elif size < block.size:
                insertion_place = self.blocks.index(block)
                block_in_use = Block(block.start, size, is_used=True)
                free_block = Block(block_in_use.finish + 1, block.size - size, is_used=False)
                self.memory_size -= size
                size -= block_in_use.size

        if insertion_place is not None:
            self.blocks[insertion_place] = block_in_use
            self.blocks.insert(insertion_place + 1, free_block)

        if size > 0:
            self.memory_size -= size
            self.blocks.append(Block(self._new_block_start(), size, is_used=True))

    def free(self, any_object: Any) -> None:
        size = getsizeof(any_object)

        insertion_place = None
        for block in self._used_blocks():
            if size == 0:
                return
            if size >= block.size:
                block.free()
                self.memory_size += block.size
                size -= block.size
            elif size < block.size:
                insertion_place = self.blocks.index(block)
                block_in_use = Block(block.start, block.size - size, is_used=True)
                free_block = Block(block_in_use.finish + 1, size, is_used=False)
                self.memory_size += size
                size -= free_block.size

        if insertion_place is not None:
            self.blocks[insertion_place] = block_in_use
            self.blocks.insert(insertion_place + 1, free_block)

    def __str__(self):
        output = ''
        for block in self.blocks:
            output += str(block)
        return output

    # PRIVATE

    def _new_block_start(self) -> int:
        if not self.blocks:
            return 0
        return self.blocks[-1].finish + 1

    def _run_of_memory_alert(self, size) -> None:
        if size > self.memory_size:
            custom_raise(CustomException('Run out of memory'))

    def _unused_blocks(self) -> List[Block]:
        return list(filter(lambda block: (not block.is_used), self.blocks))

    def _used_blocks(self) -> List[Block]:
        return list(filter(lambda block: block.is_used, self.blocks))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    memory = MemoryAllocator(1000)
    memory.allocate(5)
    memory.free(5)
    memory.allocate('hkjhkhjkhsdsvdvdsvs')
    print(memory.memory_size)
    print(memory)
