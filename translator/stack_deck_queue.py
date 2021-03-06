from translator.memalloc import MemoryAllocator
from translator.sys_exceptions import CustomException, custom_raise


class Collection:
    __slots__ = '_elements', 'memory'

    def __init__(self, memory: MemoryAllocator):
        self._elements = []
        self.memory: MemoryAllocator = memory

    def __str__(self) -> str:
        return str(self._elements)

    def _out_of_elements_alert(self) -> None:
        if not self._elements:
            custom_raise(CustomException('Collection out of elements'))

    def __len__(self) -> int:
        return len(self._elements)


class Stack(Collection):
    def push(self, element):
        self.memory.allocate(element)
        self._elements.append(element)

    def pop(self):
        self._out_of_elements_alert()

        element = self._elements.pop()
        self.memory.free(element)
        return element


class Deck(Collection):
    def push_first(self, element):
        self.memory.allocate(element)
        self._elements.insert(0, element)

    def pop_first(self):
        self._out_of_elements_alert()

        element = self._elements.pop(0)
        self.memory.free(element)
        return element

    def push_last(self, element):
        self.memory.allocate(element)
        self._elements.append(element)

    def pop_last(self):
        self._out_of_elements_alert()

        element = self._elements.pop()
        self.memory.free(element)
        return element


class Queue(Collection):
    def push(self, element):
        self.memory.allocate(element)
        self._elements.append(element)

    def pop(self):
        self._out_of_elements_alert()

        element = self._elements.pop(0)
        self.memory.free(element)
        return element
