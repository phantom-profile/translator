# Custom translator

It translates primitive c-like language made by me. 
Check grammars.txt file to see grammars, which can be translated

Translating does in four main steps provided by Lexer, Parser, Compiler and VirtualMachine

1) Lexer reads source text of program from file and splits it to tokens
    which can be parsed to tree-like structure in next step. On this step
    we check that all symbols of user input are correct and there are no non-existing
    tokens in program
2) Parser gets tokens from Lexer one by one and depends on current token generates
    nodes of tree. In this step we check that all legal lexems are in right order
    and can be parsed in compilable structure
3) Compiler gets parsed tree and recursively generates from parsed nodes code
    for virtual machine. It is easy to execute commands which can be performed
    by virtual machine
4) VirtualMachine gets compiled program and executes it, using two structures: 
    stack for storing numbers and hash table for storing and getting variables