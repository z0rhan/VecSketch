import ply.yacc

import lexer
from error import SyntaxError


class ASTnode:
    def __init__(self, type: str):
        self.nodetype = type


def p_empty(p):
    '''empty : '''
    p[0] = None


def p_program(p):
    '''program : multiple_definitions statement_list
    '''
    definitions = p[1]
    stmt_list = p[2]
    node = ASTnode("program")
    node.child_definitions = definitions
    node.children_statements = stmt_list

    p[0] = node


def p_statement_list(p):
    '''statement_list : statement_list statement
    '''
    stml_list = p[1]
    stml_list.append(p[2])

    p[0] = stml_list


def p_statement_single(p):
    '''statement_list : statement
    '''
    p[0] = [p[1]]


# Extra rule for program [0 or more definitions] ==============================
def make_multiple_definitions_node():
    node = ASTnode("multiple_definitions")

    node.children_variable_definitions = []
    node.children_function_definitions = []
    node.children_procedure_definitions = []

    return node


def p_multiple_function_definitions(p):
    '''multiple_definitions : multiple_definitions function_definition
    '''
    node = p[1]
    node.children_function_definitions.append(p[2])

    p[0] = node


def p_multiple_function_definitions_single(p):
    '''multiple_definitions : function_definition
    '''
    node = make_multiple_definitions_node()
    node.children_function_definitions = [p[1]]

    p[0] = node


def p_multiple_procedure_definitions(p):
    '''multiple_definitions : multiple_definitions procedure_definition
    '''
    node = p[1]
    node.children_procedure_definitions.append(p[2])

    p[0] = node


def p_multiple_procedure_definitions_single(p):
    '''multiple_definitions : procedure_definition
    '''
    node = make_multiple_definitions_node()
    node.children_procedure_definitions = [p[1]]

    p[0] = node


def p_multiple_variable_definitions(p):
    '''multiple_definitions : multiple_definitions variable_definition
    '''
    node = p[1]
    node.children_variable_definitions.append(p[2])

    p[0] = node


def p_multiple_variable_definitions_single(p):
    '''multiple_definitions : variable_definition
    '''
    node = make_multiple_definitions_node()
    node.children_variable_definitions = [p[1]]

    p[0] = node


def p_multiple_definitions_empyt(p):
    '''multiple_definitions : empty
    '''
    # multiple_definitions node with empty lists
    p[0] = make_multiple_definitions_node()
# Extra rule ends here ========================================================


def p_variable_definition(p):
    '''variable_definition : type IDENT EQ rvalue
    '''
    node = ASTnode("variable_definition")
    node.lineno = p.lineno(1)

    identifier_node = ASTnode("identifier")
    identifier_node.lineno = p.lineno(2)
    identifier_node.lexpos = p.lexpos(2)
    identifier_node.value = p[2]

    node.child_type = p[1]
    node.child_identifier = identifier_node
    node.child_rvalue = p[4]

    p[0] = node


# Extra rule needed for function_definition [0 or more variable_definitions]===
def p_variable_definitions(p):
    '''variable_definitions : variable_definitions variable_definition
    '''
    definition_list = p[1]
    definition_list.append(p[2])

    p[0] = definition_list


def p_variable_definitions_single(p):
    '''variable_definitions : variable_definition
    '''
    p[0] = [p[1]]


def p_variable_definitions_empty(p):
    '''variable_definitions : empty
    '''
    p[0] = None
# Extra rule ends here ========================================================


# Extra rule for function/procedure definition [formals or noe formals]========
def p_opt_formals_empty(p):
    '''opt_formals : empty
    '''
    # It was originally None, but changed to empty list for length comparison
    p[0] = []


def p_opt_formals(p):
    '''opt_formals : formals
    '''
    p[0] = p[1]
# Extra rule ends here ========================================================


def p_function_definition(p):
    '''function_definition : DEFINE FUNC_IDENT LCURLY opt_formals RCURLY RETURN type variable_definitions IS rvalue END
    '''
    node = ASTnode("function_definition")
    node.lineno = p.lineno(1)

    identifier_node = ASTnode("identifier")
    identifier_node.lineno = p.lineno(2)
    identifier_node.lexpos = p.lexpos(2)
    identifier_node.value = p[2]

    node.child_identifier = identifier_node
    node.children_formals = p[4]
    node.child_return_type = p[7]
    node.children_variable_definitions = p[8]
    node.child_rvalue = p[10]

    p[0] = node


def p_procedure_definition(p):
    '''procedure_definition : DEFINE PROC_IDENT LSQUARE opt_formals RSQUARE variable_definitions IS statement_list RETURN expression END
                            | DEFINE PROC_IDENT LSQUARE opt_formals RSQUARE variable_definitions IS statement_list END
    '''
    node = ASTnode("procedure_definition")
    node.lineno = p.lineno(1)

    identifier_node = ASTnode("identifier")
    identifier_node.lineno = p.lineno(2)
    identifier_node.lexpos = p.lexpos(2)
    identifier_node.value = p[2]

    node.child_identifier = identifier_node
    node.children_formals = p[4]
    node.children_variable_definitions = p[6]
    node.children_statements = p[8]
    if len(p) == 10:
        node.child_return_expression = None
    else:
        node.child_return_expression = p[10]

    p[0] = node


def p_statement_assignment(p):
    '''statement :  assignment
    '''
    p[0] = p[1]


def p_assignment(p):
    '''assignment : lvalue ASSIGN rvalue
                  | lvalue ASSIGN procedure_call
    '''
    node = ASTnode("assignment")
    node.lineno = p.lineno(1)
    node.child_left = p[1]
    node.child_right = p[3]

    p[0] = node


def p_print_statement(p):
    '''statement :  print_statement
    '''
    p[0] = p[1]


def p_print_statement_single_item(p):
    '''print_statement : PRINT print_item
    '''
    node = ASTnode("print_statement")
    node.lineno = p.lineno(1)
    node.children_print_items = [p[2]]

    p[0] = node


def p_print_statement_multiple_item(p):
    '''print_statement : print_statement AMPERSAND print_item
    '''
    node = p[1]
    node.children_print_items.append(p[3])

    p[0] = node


def p_if_then_statement(p):
    '''statement : IF expression THEN statement_list ENDIF
    '''
    node = ASTnode("if_statement")
    node.lineno = p.lineno(1)
    node.child_condition = p[2]
    node.children_then_statements = p[4]
    node.children_else_statements = []

    p[0] = node


def p_if_then_else_statement(p):
    '''statement : IF expression THEN statement_list ELSE statement_list ENDIF
    '''
    node = ASTnode("if_statement")
    node.lineno = p.lineno(1)
    node.child_condition = p[2]
    node.children_then_statements = p[4]
    node.children_else_statements = p[6]

    p[0] = node


def p_while_statement(p):
    '''statement : WHILE expression IS statement_list ENDWHILE
    '''
    node = ASTnode("while_statement")
    node.lineno = p.lineno(1)
    node.child_condition = p[2]
    node.children_statements = p[4]

    p[0] = node


def p_procedure_call_statement(p):
    '''statement : procedure_call
    '''
    p[0] = p[1]


def p_procedure_call(p):
    '''procedure_call : PROC_IDENT LPAREN RPAREN
                      | PROC_IDENT LPAREN arguments RPAREN
    '''
    node = ASTnode("procedure_call")
    node.lineno = p.lineno(1)

    identifier_node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    identifier_node.value = p[1]

    node.child_identifier = identifier_node
    if len(p) == 4:
        node.children_arguments = []
    else:
        node.children_arguments = p[3]

    p[0] = node


def p_arguments_single(p):
    '''arguments : expression
    '''
    p[0] = [p[1]]


def p_arguments(p):
    '''arguments : arguments COMMA expression
    '''
    argument_list = p[1]
    argument_list.append(p[3])

    p[0] = argument_list


def p_clear_statement(p):
    '''statement : CLEAR
    '''
    node = ASTnode("clear_statement")
    node.lineno = p.lineno(1)

    p[0] = node


def p_pause_statement(p):
    '''statement : PAUSE
    '''
    node = ASTnode("pause_statement")
    node.lineno = p.lineno(1)

    p[0] = node


def p_wait_statement(p):
    '''statement : WAIT expression
    '''
    node = ASTnode("wait_statement")
    node.lineno = p.lineno(1)
    node.child_expression = p[2]

    p[0] = node


def p_draw_statement(p):
    '''statement : DRAW expression
                 | DRAW expression rgb
    '''
    node = ASTnode("draw_statement")
    node.lineno = p.lineno(1)
    node.child_expression = p[2]
    if len(p) == 3:
        node.child_rgb = None
    else:
        node.child_rgb = p[3]

    p[0] = node


def p_rgb(p):
    '''rgb : LPAREN expression COMMA expression COMMA expression RPAREN
    '''
    node = ASTnode("rgb")
    node.lineno = p.lineno(1)
    node.child_r = p[2]
    node.child_g = p[4]
    node.child_b = p[6]

    p[0] = node


def p_expression(p):
    '''expression : simple_expr
                  | expression EQ simple_expr
                  | expression NOTEQ simple_expr
                  | expression LT simple_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = ASTnode("comparison")
        node.lineno = p.lineno(1)
        node.child_left = p[1]
        node.child_right = p[3]
        node.value = p[2]

        p[0] = node


def p_simple_expr(p):
    '''simple_expr : term
                   | simple_expr PLUS term
                   | simple_expr MINUS term
                   | simple_expr ARROW coordinate
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = ASTnode("binary_operation")
        node.lineno = p.lineno(1)
        node.child_left = p[1]
        node.child_right = p[3]
        node.value = p[2]

        p[0] = node


def p_term(p):
    '''term : factor
            | term MULT factor
            | term DIV factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = ASTnode("binary_operation")
        node.lineno = p.lineno(1)
        node.child_left = p[1]
        node.child_right = p[3]
        node.value = p[2]

        p[0] = node


def p_factor(p):
    '''factor : atom
              | MINUS atom
              | PLUS atom
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = ASTnode("unary_operation")
        node.lineno = p.lineno(1)
        node.value = p[1]
        node.child_expression = p[2]

        p[0] = node


def p_atom_int_literal(p):
    '''atom : INT_LITERAL
    '''
    node = ASTnode("int_literal")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    node.value = p[1]

    p[0] = node


def p_atom_identifier(p):
    '''atom : IDENT
    '''
    node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    node.value = p[1]

    p[0] = node


def p_atom_access(p):
    '''atom : IDENT DOT IDENT
    '''
    node = ASTnode("field_access")
    node.lineno = p.lineno(1)

    target_node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    target_node.value = p[1]
    field_node = ASTnode("identifier")
    node.lineno = p.lineno(3)
    node.lexpos = p.lexpos(3)
    field_node.value = p[3]

    node.child_target = target_node
    node.child_field = field_node

    p[0] = node


def p_atom_expression(p):
    '''atom : LPAREN expression RPAREN
    '''
    p[0] = p[2]


def p_atom_function_call(p):
    '''atom : function_call
    '''
    p[0] = p[1]


def p_function_call(p):
    '''function_call : FUNC_IDENT LPAREN RPAREN
                     | FUNC_IDENT LPAREN arguments RPAREN
    '''
    node = ASTnode("function_call")
    node.lineno = p.lineno(1)

    identifier_node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    identifier_node.value = p[1]
    node.child_identifier = identifier_node
    if len(p) == 4:
        node.children_arguments = []
    else:
        node.children_arguments = p[3]

    p[0] = node


def p_type_identifier(p):
    '''type : IDENT
    '''
    node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    node.value = p[1]

    p[0] = node


def p_type_shape(p):
    '''type : SHAPE
    '''
    node = ASTnode("shape")
    node.value = p[1]

    p[0] = node


def p_type_number(p):
    '''type : NUMBER
    '''
    node = ASTnode("number")
    node.value = p[1]

    p[0] = node


def p_coordinate_list_single(p):
    '''coordinate_list : coordinate
    '''
    node = ASTnode("coordinate_list")
    node.children_coordinates = [p[1]]

    p[0] = node


def p_coordinate_list(p):
    '''coordinate_list : coordinate_list MINUS coordinate
    '''
    node = p[1]
    node.children_coordinates.append(p[3])

    p[0] = node


def p_coordinate(p):
    '''coordinate : LSQUARE expression COMMA expression RSQUARE
    '''
    node = ASTnode("coordinate")
    node.lineno = p.lineno(1)
    node.child_x = p[2]
    node.child_y = p[4]

    p[0] = node


def p_formals_single(p):
    '''formals : formal_arg
    '''
    p[0] = [p[1]]


def p_formals(p):
    '''formals : formals SEMICOLON formal_arg
    '''
    formal_arg_list = p[1]
    formal_arg_list.append(p[3])

    p[0] = formal_arg_list


def p_formal_arg(p):
    '''formal_arg : IDENT COLON type
    '''
    node = ASTnode("formal_arg")
    node.lineno = p.lineno(1)

    identifier_node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    identifier_node.value = p[1]
    node.child_identifier = identifier_node
    node.child_type = p[3]

    p[0] = node


def p_lvalue(p):
    '''lvalue : IDENT
    '''
    node = ASTnode("identifier")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    node.value = p[1]

    p[0] = node


def p_rvalue(p):
    '''rvalue : expression
              | coordinate_list
              | PLUS coordinate_list
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = ASTnode("unary_operation")
        node.lineno = p.lineno(1)
        node.value = p[1]
        node.child_expression = p[2]
        p[0] = node


def p_print_item(p):
    '''print_item : expression
    '''
    p[0] = p[1]


def p_print_item_string(p):
    '''print_item : STRING
    '''
    node = ASTnode("string")
    node.lineno = p.lineno(1)
    node.lexpos = p.lexpos(1)
    node.value = p[1]

    p[0] = node


def p_error(p):
    if p is None:
        # When token is None use previous lexer state
        lineno = getattr(lexer.lexer, 'lineno', None)
        lexpos = getattr(lexer.lexer, 'lexpos', None)
        msg = "SyntaxError: syntax error at end of line"
        raise SyntaxError((msg, lineno - 1, lexpos, None))

    if p.type == "STRING":
        msg = f"SyntaxError: unexpected token \"{p.value}\""
        token = "\"" + p.value + "\""
        raise SyntaxError((msg, p.lineno, p.lexpos, token))
    msg = f"SyntaxError: unexpected token {p.value}"
    raise SyntaxError((msg, p.lineno, p.lexpos, str(p.value)))


tokens = lexer.tokens
parser = ply.yacc.yacc(start="program")
