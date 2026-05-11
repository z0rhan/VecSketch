import sys

import lexer
import syntax_ast
from semantic import init_semdata, populate_symbol_table, semantic_before, semantic_after
from interpret import run_program
from utils import visit_tree
from error import LexError, SyntaxError

# AT the end of input lexer.lexpos moves up 2 char
EOF_OFFSET = 2

lexer = lexer.lexer
parser = syntax_ast.parser


# Construct error msg and print (lexical error)
def print_lex_error_msg(filename, line, lineno, charpos, token, msg):
    # Useful error message
    print(msg)
    line_str = f"{filename}:line {lineno}:"
    ptr_str = " " * len(line_str) + "~" * charpos + "^" * len(token)
    print(f"{line_str}{line}", end="")
    print(ptr_str)
    # Course requirment
    print("Error found!")


# Construct error msg and print (parse error)
def print_parse_error_msg(filename, line, lineno, charpos, token, message):
    # Useful error message
    print(message)
    if token is None:
        charpos -= EOF_OFFSET
        token_len = 1
    else:
        token_len = len(token)

    line_str = f"{filename}:line {lineno}:"
    ptr_str = " " * len(line_str) + "~" * max(charpos, 0) + "^" * token_len
    print(f"{line_str}{line}", end="")
    print(ptr_str)
    # Course requirment
    print("Error found!")


# Line number to line mapping for error msg
source_code = {}


# Apply lexical and syntactic analysis
def parse(filename):
    with open(filename, "r") as f_handler:
        lines = f_handler.readlines()
        buf = ""
        for i, line in enumerate(lines):
            source_code[i] = line
            buf += line

        try:
            ast_tree_root = parser.parse(buf, lexer=lexer, debug=False)
            semdata = init_semdata()
            visit_tree(ast_tree_root, populate_symbol_table, None, semdata)
            visit_tree(ast_tree_root, semantic_before, semantic_after, semdata)

        except LexError as e:
            msg, lineno, lexpos, err_token = e.args[0]
            line = source_code[lineno - 1]
            charpos = lexpos - sum(len(source_code[i]) for i in range(lineno - 1))
            print_lex_error_msg(filename, line, lineno, charpos, err_token, msg)
            return
        except SyntaxError as e:
            msg, lineno, lexpos, err_token = e.args[0]
            line = source_code[lineno - 1]
            charpos = lexpos - sum(len(source_code[i]) for i in range(lineno - 1))
            print_parse_error_msg(filename, line, lineno, charpos, err_token, msg)
            return
    # Course requirment
    print("Program ok.")

    # Run the interpreter after the source code passes the all the prior
    # analysis phases
    run_program(ast_tree_root, semdata)


# Entry point to the compiler/intrepretor
def entry_point():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>", file=sys.stderr)
        return
    else:
        filename = sys.argv[1]
        parse(filename)


if __name__ == '__main__':
    entry_point()
