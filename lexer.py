import ply.lex

from error import LexError

# Reserved keywords
reserved = {
    'number': 'NUMBER',
    'shape': 'SHAPE',
    'define': 'DEFINE',
    'is': 'IS',
    'end': 'END',
    'return': 'RETURN',
    'draw': 'DRAW',
    'clear': 'CLEAR',
    'pause': 'PAUSE',
    'wait': 'WAIT',
    'while': 'WHILE',
    'endwhile': 'ENDWHILE',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'endif': 'ENDIF',
    'print': 'PRINT'
}

# All possbile tokens
tokens = [
    # One or two char token
    'LPAREN',
    'RPAREN',
    'LSQUARE',
    'RSQUARE',
    'LCURLY',
    'RCURLY',
    'ASSIGN',
    'ARROW',
    'AMPERSAND',
    'COMMA',
    'COLON',
    'SEMICOLON',
    'DOT',
    'EQ',
    'NOTEQ',
    'LT',
    # 'GT',   # why not gt if lt
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    # Longer token
    'STRING',
    'INT_LITERAL',
    'IDENT',
    'PROC_IDENT',
    'FUNC_IDENT',
] + list(reserved.values())

# Rule for the tokens
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_ASSIGN = r':='
t_ARROW = r'->'
t_AMPERSAND = r'&'
t_COMMA = r','
t_COLON = r':'
t_SEMICOLON = r';'
t_DOT = r'\.'
t_EQ = r'='
t_NOTEQ = r'/='
t_LT = r'<'
# t_GT = r'>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_FUNC_IDENT = r'[A-Z][A-Z][A-Z0-9_]*'
# Seems this should be list of char and not regex
t_ignore = " \t\r"


# Do not produce tokens for comments
def t_COMMENT(t):
    r'/%[\s\S]*?%/'  # Seems ? is needed
    t.lexer.lineno += t.value.count('\n')
    pass


# Rule for IDENT, if word in reserved then return reserved type else IDENT
def t_IDENT(t):
    r'[a-z][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    else:
        if len(t.value) > 64:
            msg = "Max char for IDENT exceeded: 64 char"
            charpos_offset = len(t.value.strip())
            raise LexError((msg, t.lexer.lineno, t.lexer.lexpos - charpos_offset, t.value.strip()))
        t.type = 'IDENT'
    return t


# Rule for PROC_IDENT, if word in reserved then return reserved type
def t_PROC_IDENT(t):
    r'[A-Z][a-z0-9_]+'
    if t.value in reserved:
        t.type = reserved[t.value]
    else:
        t.type = 'PROC_IDENT'
    return t


# Rule for STRING, remove the first and last quotation when storing the value
def t_STRING(t):
    r'"[^"]*"'
    t.value = str(t.value.lstrip('"').strip('"'))
    return t


# Rule for Int Literal, define upper and lower limit
def t_INT_LITERAL(t):
    r'-?[0-9]+'
    if int(t.value) > 1000000000 or int(t.value) < -1000000000:
        msg = f"Integer limit exceeded: -10^9 < {t.value.strip()} < 10^9 "
        # Since regex allows it token is genereated and lexpos also increases
        charpos_offset = len(t.value.strip())
        raise LexError((msg, t.lexer.lineno, t.lexer.lexpos - charpos_offset, t.value.strip()))

    t.value = int(t.value)
    return t


# Record number line
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


# Send metadata with exception
def t_error(t):
    msg = f"LexError: Illegal token {t.value.strip()}"
    raise LexError((msg, t.lexer.lineno, t.lexer.lexpos, t.value.strip()))


lexer = ply.lex.lex()
