from memalloc import MemoryAllocator
from sys_exceptions import CustomException, custom_raise

SYSTEM_MEMORY = 1024


class Collection:
    def __init__(self, memory: MemoryAllocator):
        self.elements = []
        self.memory: MemoryAllocator = memory

    def __str__(self):
        return str(self.elements)

    def _out_of_elements_alert(self):
        if not self.elements:
            custom_raise(CustomException(1, 'Collection out of elements'))


class Stack(Collection):
    def push(self, element):
        self.memory.allocate(element)
        self.elements.append(element)

    def pop(self):
        self._out_of_elements_alert()

        element = self.elements.pop()
        self.memory.free(element)
        return element


class Deck(Collection):
    def push_first(self, element):
        self.memory.allocate(element)
        self.elements.insert(0, element)

    def pop_first(self):
        self._out_of_elements_alert()

        element = self.elements.pop(0)
        self.memory.free(element)
        return element

    def push_last(self, element):
        self.memory.allocate(element)
        self.elements.append(element)

    def pop_last(self):
        self._out_of_elements_alert()

        element = self.elements.pop()
        self.memory.free(element)
        return element


class Queue(Collection):
    def push(self, element):
        self.memory.allocate(element)
        self.elements.append(element)

    def pop(self):
        self._out_of_elements_alert()

        element = self.elements.pop(0)
        self.memory.free(element)
        return element


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    my_comp_memory = MemoryAllocator(SYSTEM_MEMORY)
    deck = Deck(my_comp_memory)
    stack = Stack(my_comp_memory)
    queue = Queue(my_comp_memory)
    for i, j in (('a', '1'), ('b', '2'), ('c', '3')):
        stack.push(i)
        queue.push(j)
    print('Stack:', stack)
    print('Queue:', queue)
    print(my_comp_memory)

    print('Deleting obj from stack:', stack.pop())
    print('Stack:', stack)
    print(my_comp_memory)

    print('Deleting obj from queue:', queue.pop())
    print('Queue:', queue)
    print(my_comp_memory)

    deck.push_first('a')
    deck.push_first('b')
    deck.push_last('c')
    print('Deck:', deck)
    print(my_comp_memory)

    print('Deleting obj from start of deck:', deck.pop_first())
    print('Deck:', deck)
    print(my_comp_memory)

    print('Deleting obj from end of deck:', deck.pop_last())
    print('Deck:', deck)
    print(my_comp_memory)

    print('Deleting obj from end of deck:', deck.pop_last())
    print('Deck:', deck)
    print(my_comp_memory)

    print('Deleting obj from end of deck:', deck.pop_last())
    print('Deck:', deck)
    print(my_comp_memory)

    print('Deleting obj from end of deck:', deck.pop_last())
    print('Deck:', deck)
    print(my_comp_memory)


