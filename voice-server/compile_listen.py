# -----------------------------------------------------------------------------
# compile_listen.py
# 
#   statement : 
#             | simple_stmt
#             | compound_stmt
# 
#    simple_stmt : 
#              | assignment
#              | expression
#              | return_stmt
#
#    compound_stmt : 
#              | if_stmt
#              | function_def
#              | class_def
#              | while_stmt
#              | for_stmt
#
#   expression : 
#              | disjunction
#
#   disjunction :
#              | conjunction OR disjunction
#              | conjunction
#
#   conjunction :
#              | inversion AND conjunction
#              | inversion
#
#   inversion :
#              | NOT inversion
#              | comparison
#
#   comparison :
#              | bitwise_or compare_op_bitwise_or_pair+
#              | bitwise_or
#
#   compare_op_bitwise_or_pair :
#              | eq_op bitwise_or
#              | ne_op bitwise_or
#              | lt_op bitwise_or
#              | le_op bitwise_or
#              | gt_op bitwise_or
#              | ge_op bitwise_or
#
#   bitwise_or :
#              | bitwise_or '|' bitwise_xor
#              | bitwise_xor
# 
#   bitwise_xor :
#              | bitwise_xor '^' bitwise_and
#              | bitwise_and
# 
#   bitwise_and :
#              | bitwise_and '&' shift_expr
#              | shift_expr
# 
#   shift_expr :
#              | shift_expr '<<' arith_expr
#              | shift_expr '>>' arith_expr
#              | arith_expr
# 
#   arith_expr :
#              | arith_expr '+' term
#              | arith_expr '-' term
#              | term
# 
#   term :
#              | term '*' factor
#              | term '/' factor
#              | factor
# 
#   factor :
#              | '+' factor
#              | '-' factor
#              | primary
# 
#   primary :
#              | primary '.' NAME
#              | atom
# 
#   atom :
#              | NAME
#              | NUMBER
#
# -----------------------------------------------------------------------------

import sys
import speech_recognition as sr
from server import send_message
from ply import yacc
from ply import lex

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'return': 'RETURN',
    'lambda': 'LAMBDA',
    'False': 'FALSE',
    'True': 'TRUE',
    'None': 'NONE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'as': 'AS',
    'assert': 'ASSERT',
    'class': 'CLASS',
    'def': 'DEF',
    'del': 'DEL',
    'except': 'EXCEPT',
    'finally': 'FINALLY',
    'global': 'GLOBAL',
    'import': 'IMPORT',
    'in': 'IN',
    'is': 'IS',
    'nonlocal': 'NONLOCAL',
    'pass': 'PASS',
    'raise': 'RAISE',
    'try': 'TRY',
    'with': 'WITH',
    'yield': 'YIELD',
    'from': 'FROM',
    'elif': 'ELIF',
    'equals': 'EQ',
    'times': 'TIMES',
    'divide': 'DIVIDE',
    'plus': 'PLUS',
    'minus': 'MINUS',
    'greater': 'GREATER',
    'less': 'LESS',
    'assign': 'ASSIGN',
    'open': 'OPEN',
    'close': 'CLOSE',
    'parentheses': 'PARENTHESES',
    'start': 'START',
    'end': 'END',
}

tokens = [
            'NUMBER', 
            'NAME',
            'NE',
            'LT',
            'LE',
            'GT',
            'GE',
            'BITWISE_OR',
            'BITWISE_XOR',
            'BITWISE_AND',
            'SHIFT_LEFT',
            'SHIFT_RIGHT',
            'DOT',
            'INDENT',
          ] + list(reserved.values())

t_ignore = ' \t'
t_NUMBER = r'\d+'
t_BITWISE_OR = r'\|'
t_BITWISE_XOR = r'\^'
t_BITWISE_AND = r'&'
t_SHIFT_LEFT = r'<<'
t_SHIFT_RIGHT = r'>>'
t_DOT = r'\.'


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'NAME')
    return t

lexer = lex.lex(debug=True)

start = 'statement'

def p_statements(p):
    """statements : 
                  | statement statements"""
    if len(p) == 1:
        p[0] = ""
    else:
        p[0] = f"{p[1]}\n{p[2]}"

def p_simple_stmts(p):
    """simple_stmts : 
                    | simple_stmt simple_stmts"""
    if len(p) == 1:
        p[0] = ""
    else:
        p[0] = f"{p[1]}\n{p[2]}"

def p_statement(p):
    """statement : simple_stmt
                 | compound_stmt"""
    p[0] = p[1]

def p_simple_stmt(p):
    """simple_stmt : expression
                   | assignment"""
    p[0] = p[1]

def p_compound_stmt(p):
    """compound_stmt : if_stmt"""
    p[0] = p[1]

def p_if_stmt(p):
    """if_stmt : IF expression START block END"""
    p[0] = f"if {p[2]}:\n{p[4]}"

def p_block(p):
    """block : 
            | simple_stmt block"""
    if len(p) == 1:
        p[0] = ""
    else:
        p[0] = f"\t{p[1]}\n{p[2]}"

def p_assignment(p):
    """assignment : NAME ASSIGN expression"""
    p[0] = f"{p[1]} = {p[3]}"

def p_expression(p):
    """expression : disjunction"""
    p[0] = p[1]

def p_disjunction(p):
    """disjunction : conjunction OR disjunction
                   | conjunction"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} or {p[3]}"

def p_conjunction(p):
    """conjunction : inversion AND conjunction
                   | inversion"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        print(len(p))
        print(f"{p.lexpos(0)} & {p.lexpos(1)}")
        p[0] = f"{p[1]} and {p[3]}"

def p_inversion(p):
    """inversion : NOT inversion
                 | comparison"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"not {p[2]}"

def p_comparison(p):
    """comparison : bitwise_or compare_op_bitwise_or_pair_repeat
                  | bitwise_or"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} {p[2]}"

def p_bitwise_or(p):
    """bitwise_or : bitwise_or BITWISE_OR bitwise_xor
                  | bitwise_xor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} | {p[3]}"

def p_compare_op_bitwise_or_pair_repeat(p):
    """compare_op_bitwise_or_pair_repeat : 
                                         | compare_op_bitwise_or_pair compare_op_bitwise_or_pair_repeat"""
    if len(p) == 1:
        p[0] = ""
    else:
        p[0] = f"{p[1]} {p[2]}"

def p_compare_op_bitwise_or_pair(p):
    """compare_op_bitwise_or_pair : eq_op bitwise_or
                                  | ne_op bitwise_or
                                  | lt_op bitwise_or
                                  | le_op bitwise_or
                                  | gt_op bitwise_or
                                  | ge_op bitwise_or"""
    p[0] = f"{p[1]} {p[2]}"

def p_eq_op(p):
    """eq_op : EQ"""
    p[0] = "=="

def p_ne_op(p):
    """ne_op : NOT EQ"""
    p[0] = "!="

def p_lt_op(p):
    """lt_op : LESS"""
    p[0] = "<"

def p_le_op(p):
    """le_op : LESS EQ"""
    p[0] = "<="

def p_gt_op(p):
    """gt_op : GREATER"""
    p[0] = ">"

def p_ge_op(p):
    """ge_op : GREATER EQ"""
    p[0] = ">="

def p_bitwise_xor(p):
    """bitwise_xor : bitwise_xor BITWISE_XOR bitwise_and
                   | bitwise_and"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} ^ {p[3]}"

def p_bitwise_and(p):
    """bitwise_and : bitwise_and BITWISE_AND shift_expr
                   | shift_expr"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} & {p[3]}"

def p_shift_expr(p):
    """shift_expr : shift_expr SHIFT_LEFT arith_expr
                  | shift_expr SHIFT_RIGHT arith_expr
                  | arith_expr"""
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '<<':
        p[0] = f"{p[1]} << {p[3]}"
    else:
        p[0] = f"{p[1]} >> {p[3]}"

def p_arith_expr(p):
    """arith_expr : arith_expr MINUS term
                  | term"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} - {p[3]}"

def p_arith_expr_add(p):
    """arith_expr : arith_expr PLUS term"""
    p[0] = f"{p[1]} + {p[3]}"

def p_term(p):
    """term : term DIVIDE factor
            | factor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} / {p[3]}"

def p_term_multiply(p):
    """term : term TIMES factor"""
    p[0] = f"{p[1]} * {p[3]}"

def p_factor(p):
    """factor : PLUS factor
              | MINUS factor
              | primary"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} {p[2]}"

def p_primary(p):
    """primary : primary DOT NAME
               | atom"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]}.{p[3]}"

def p_atom(p):
    """atom : NAME
            | NUMBER"""
    p[0] = p[1]

def p_LPAREN(p):
    """LPAREN : OPEN PARENTHESES"""
    p[0] = "("

def p_RPAREN(p):
    """RPAREN : CLOSE PARENTHESES"""
    p[0] = ")"

parser = yacc.yacc(debug=True)

#Currently just used for testing the parser with a hardcoded input from main.py
def compile_listen(parser_input):
    result = parser.parse(parser_input, lexer=lexer)
    print(result)
    send_message({"route": "message",
                  "data": {"text": result}})
    return

    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while (True):
                send_message({"route": "message",
                              "data": {"message": 'Please give your command. Listening...'}})

                try:
                    audio = r.listen(source, timeout=7, phrase_time_limit=5)
                    cmd = r.recognize_google(audio)
                    result = parser.parse(cmd)
                    send_message({"route": "message",
                                  "data": {"text": result}})

                except (Exception, sr.exceptions.WaitTimeoutError) as e:
                    if type(e) != sr.exceptions.WaitTimeoutError and type(e) != sr.exceptions.UnknownValueError:
                        send_message({"route": "message",
                                      "data": {"message": 'There was an issue with the microphone input.'}})
    except OSError:
        send_message({"route": "message",
                      "data": {"message": 'Microphone not detected. Please check your microphone connection.'}})
        exit(0)