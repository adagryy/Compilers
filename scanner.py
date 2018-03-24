import collections
import re

Token = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])

class Scanner:

  def __init__(self, input):
    self.tokens = []
    self.current_token_number = 0
    for token in self.tokenize(input):
        self.tokens.append(token)
    # for token in self.tokens:
    #     print token.value + " " + token.type
        
 
  def tokenize(self, input_string):
    keywords = {'equals', 'new', 'descending', 'in', 'from', 'orderby', 'select', 'where', 'null', 'var'}
    token_specification = [
        ('number',  r'\d+(\.\d*)?'), # Integer or decimal number
        ('assign',  r'='),          # Assignment operator
        ('semicolon',     r';'),           # Statement terminator
        ('variablename', r'[a-zA-Z0-9_]+'),
        # ('ID',      r'[A-Za-z]+'),   # Identifiers
        ('OP',      r'[+*\/\-]'),    # Arithmetic operators
        ('NEWLINE', r'\n'),          # Line endings
        ('SKIP',    r'[ \t]'),       # Skip over spaces and tabs
        
        ('dot', r'\.'),
        ('op', r'\('),
        ('cb', r'\)'),
        ('ocp', r'\{'),
        ('ccb', r'\}'),
        ('comma', r'\,'),
        ('exclamation_mark', r'\!')
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    get_token = re.compile(tok_regex).match

    line_number = 1
    current_position = line_start = 0
    match = get_token(input_string)
    while match is not None:
        type = match.lastgroup
        if type == 'NEWLINE':
            line_start = current_position
            line_number += 1
        elif type != 'SKIP':
            value = match.group(type)
            # print value
            if (type == 'ID' or type == 'variablename') and value in keywords:
                type = value
            yield Token(type, value, line_number, match.start()-line_start)
        current_position = match.end()
        match = get_token(input_string, current_position)
    if current_position != len(input_string):
        raise RuntimeError('Error: Unexpected character %r on line %d' % \
                              (input_string[current_position], line_number))
    yield Token('EOF', '', line_number, current_position-line_start)

  def next_token(self):
    self.current_token_number += 1
    if self.current_token_number-1 < len(self.tokens):
      return self.tokens[self.current_token_number-1]
    else:
      print "Dupa"
      raise RuntimeError('Error: No more tokens')

