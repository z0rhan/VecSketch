program ::= { definitions } statement_list

statement_list ::= statement { statement }

definitions ::= function_definition
              | procedure_definition
              | variable_definition

variable_definition ::= type IDENT EQ rvalue

type ::= IDENT | SHAPE | NUMBER
rvalue ::= expression
         | [PLUS] coordinate_list

coordinate_list ::= coordinate { MINUS coordinate }
coordinate ::= LSQUARE expression COMMA expression RSQUARE


function_definition ::= DEFINE FUNC_IDENT LCURLY [formals] RCURLY
                        RETURN type
                        { variable_definition } IS
                        rvalue
                        END

procedure_definition ::= DEFINE PROC_IDENT LSQUARE [formals] RSQUARE
                         { variable_definition } IS
                         statement_list
                         [ RETURN expression ]
                         END

formals ::= formal_arg { SEMICOLON formal_arg }
formal_arg ::= IDENT COLON type

arguments ::= expression { COMMA expression }

assignment ::= lvalue ASSIGN ( rvalue | procedure_call )
lvalue ::= IDENT
procedure_call ::= PROC_IDENT LPAREN [arguments] RPAREN

print_statement ::= PRINT print_item { AMPERSAND print_item }
print_item ::= STRING | expression

statement ::= procedure_call
           | assignment
           | print_statement
           | IF expression THEN statement_list [ELSE statement_list] ENDIF
           | WHILE expression IS statement_list ENDWHILE
           | CLEAR
           | PAUSE
           | WAIT expression
           | DRAW expression [ rgb ]
rgb ::= LPAREN expression COMMA expression COMMA expression RPAREN

expression ::= simple_expr
             | expression (EQ|NOTEQ|LT) simple_expr
simple_expr ::= term
              | simple_expr (PLUS | MINUS) term
              | simple_expr ARROW coordinate
       term ::= factor
              | term (MULT | DIV) factor

     factor ::= [MINUS|PLUS] atom
       atom ::= INT_LITERAL
              | IDENT
              | IDENT DOT IDENT
              | function_call
              | LPAREN expression RPAREN

function_call ::= FUNC_IDENT LPAREN [ arguments ] RPAREN
