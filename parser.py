import collections
import re

# Range = collections.namedtuple('Token', ['type', 'value', 'line', 'column'])
# Conditionals = collections.namedtuple('Conditionals', ['type', 'value', 'line', 'column'])
# Selection = collections.namedtuple('Selection', ['type', 'value', 'line', 'column'])
# End = collections.namedtuple('End', ['type', 'value', 'line', 'column'])



class Parser:
  queryrange = []
  conditionals = []
  selection = []
  end = []

  range_variable = ""
  ##### Parser header #####
  def __init__(self, scanner):
    self.next_token = scanner.next_token
    self.token = self.next_token()

  def take_token(self, token_type):
    if self.token.type != token_type:
      self.error("Unexpected token: %s" % token_type)
    if token_type != 'EOF':
      self.token = self.next_token()

  def error(self,msg):
    raise RuntimeError('Parser error, %s' % msg)

  def errorMsg(self, msg):
    print msg
    return

  ##### Parser body #####
  # start parsaing
  def start(self):
    if self.token.type == 'var': # check if statement starts with keyword
      self.token = self.next_token() # get next token
      self.resultVariable() 
      self.validateEndSection()
    else:
      self.errorMsg('Error: no \'var\' keyword at the beginning')
      return

  # check what is after 'var' and if everything is correct then proceed (correct: 'var test...', not correct: 'var 12test...')
  def resultVariable(self):
    if self.token.type == 'variablename':
      self.token = self.next_token()
      self.equals()
    else:
      self.errorMsg('Result variable name incorrect')
      return

  # check if there is equality sign in the statement (correct: 'var test = from c in...', not correct: 'var test from c in...')
  def equals(self):
    if self.token.type == 'assign':
      # self.token = self.next_token()
      self.divideIntoSections()
    else:
      self.errorMsg('Error - no equality sign')
      return


  def divideIntoSections(self):
    tokenizerFlag = 'range' # indicates in which section we are now (LINQ query divides into range "from c in svcContext.ContactSet")
                            # Conditionals: "where !c.CreditLimit.Equals(null) 
                            # orderby c.CreditLimit descending"
                            # Selections: "select new
                            # {
                            #  limit = c.CreditLimit,
                            #  first = c.FirstName,
                            #  last = c.LastName
                            # };"
    tokenItem = self.next_token()
    if tokenItem.type == 'from':
      self.queryrange.append(tokenItem)
    else:
      self.errorMsg('Error - range section not starts with \'from\' keyword')
      return
    while 1:
      try:
        tokenItem = self.next_token()
        
        if tokenItem.type == 'where':
          tokenizerFlag = 'conditionals'
        if tokenItem.type == 'select':
          tokenizerFlag = 'selection'
        if tokenItem.type == 'semicolon':
          tokenizerFlag = 'end'
        if tokenItem.type == 'EOF':
          break

        self.insertIntoCorrectArray(tokenizerFlag, tokenItem) # insert token (tokenItem) into proper array (indicated by tokenizerFlag)

      except: 
        break
    self.printDividedCode()
    self.validateRangeSection()

  # validates whole range section: 'from c in svcContext.ContactSet'
  def validateRangeSection(self):
    if len(self.queryrange) == 0:
      return
    self.range_variable = self.queryrange[1] # skip "from" keyword - it was verified in divideIntoSections
    
    if re.compile(r'^[0-9].*$').match(self.range_variable.value): # check if range variable starts with number
      self.errorMsg("Error - range variable contains wrong characters in range section")
      return
    
    if self.queryrange[2].value != 'in': # missing "in" keyword
      self.errorMsg("Error - \'in\' keyword missing in range section")
      return

    sequence = ""
    for x in range(3, len(self.queryrange)): # rest of range section - concatenate
      sequence += self.queryrange[x].value   

    if re.compile(r'.*;.*').match(sequence): # rest cannot contain semicolon
      self.errorMsg('Semicolon not allowed here')
    if re.compile(r'^[0-9].*$').match(sequence): # rest starts with number
      self.errorMsg('Iterable variable contains digit at the beginning')

    if re.compile(r'.*\.[0-9]+.*').match(sequence): # rest cannot contain dot and number after dot
      self.errorMsg('Complex iterable variable contains bad fields names')

    if re.compile(r'^.*\.$').match(sequence): # rest ends with dot
      self.errorMsg('Iterable variable ends with dot')

    self.validateConditionalSection()

  # validates whole conditional section: 'where c.CreditLimit.Equals(null) orderby c.CreditLimit descending'
  def validateConditionalSection(self):
    print "sdfsdfgdfsgsdfg "+ str(len(self.conditionals))
    if len(self.conditionals) == 0: # no conditionals
      self.validateSelectionSection()
      return

    if len(self.conditionals) == 1: # no conditionals
      self.errorMsg('Error - expression statement incorrect - possible')
      return
    
    try:
      if self.conditionals[1].type == 'exclamation_mark':
        self.validateConditionalExpression(2)
      # if self.conditionals[1].type == 'variablename' or self.conditionals[1].type == 'dot':
      else:
        self.validateConditionalExpression(1)
    except:
      self.errorMsg('Error - unsupported character detected in expression statement')
      return

    try:      
      self.validateSelectionSection()
      # self.validateEndSection()
    except:
      self.errorMsg('Error - unsupported character detected in selection statement')
      return

  # validates whole select section: 'select new {limit = c.Credit, Limit first = c.FirstName, last = c.LastName}'
  def validateSelectionSection(self):
    if len(self.selection) == 0:
      self.errorMsg('Error - No select statement')
      return
    
    if self.selection[1].value == 'new':
      self.validateSelectBody(2)
    elif self.selection[1].value != self.range_variable.value or len(self.selection) > 2:
      self.errorMsg('Error - after select you should use \'new\' keyword')
    elif self.selection[1].value != self.range_variable.value: 
      self.errorMsg('Error - variable name not matching range variable after \'select\'')

  # Validates conditional expression in two phases: first are validated expression statements and second - sorting ones
  def validateConditionalExpression(self, number):
    expressionCode = ''
    sortingCode = ''
    expressionflag = True
    for item in range(number, len(self.conditionals)):
      if 'orderby' in self.conditionals[item].value or 'groupby' in self.conditionals[item].value:
        expressionflag = False
      if expressionflag:
        expressionCode += (self.conditionals[item].value) + ' '
      else:
        sortingCode += (self.conditionals[item].value) + ' '
    if expressionCode:
      reg = re.compile(r'^' + self.range_variable.value + ' \. [a-zA-Z]+ \. Equals \( [a-zA-Z]+ \) $').match(expressionCode)
      if not reg:
        self.errorMsg('Error - conditional expression statements incorrect')
        return
    else:
      self.errorMsg('Error - no condition')
      return

    if sortingCode:
      reg = re.compile(r'(^(orderby|groupby) ' + self.range_variable.value + ' \. [a-zA-Z]+ descending $)').match(sortingCode)
      if not reg:
        self.errorMsg('Error - sorting statements incorrect')
        return

  # validates selection body (if exists). we start checking 'selection' array from 'number' index (skipping 'number' of starting tokens)
  def validateSelectBody(self, number):

    select_body = ""
    
    # Construct select body into string, which can be easily chceked via regular expression 
    for item in range(number, len(self.selection)):
      select_body += self.selection[item].value      
    
    
    # Chcek if selection body starts and ends with '{' and '}'
    if select_body.startswith('{'):
      if select_body.endswith('}'):
        pass
      else:
        self.errorMsg("No closing bracket in select body")
        return
    else:
      self.errorMsg("No opening bracket in select body")
      return

    # Now remove brackets '{' and '}'
    select_body = select_body.replace(select_body[0],"",1)
    select_body = select_body.replace(select_body[len(select_body) - 1],"",1)

    # So if there is comma at the end it is redundand - error
    if select_body.endswith(','):
      self.errorMsg("Error - Redundant comma at the end of select body")
      return


    lines = [] # stores parts of selection body splitted by comma without comma, for instance: ['limit=c.CreditLimit', 'first=c.FirstName', 'last=c.LastName'] for the follownig input: select new { limit = c . CreditLimit , first = c . FirstName , last = c . LastName }
    line = "" # temporary variable helpful in building 'lines'

    for item in range(number + 1, len(self.selection) - 1):
      if self.selection[item].value != ",":
        line += self.selection[item].value
      if self.selection[item].value == "," or item ==  len(self.selection) - 2:
        lines.append(line)
        line = ""

    regex = '^[a-zA-Z]+=%s+\.[a-zA-Z]+$' % self.range_variable.value # regex for checking coretness (without comma) of one line in selection body (for inmstance: 'limit = c.CreditLimit')
    regex_against_comma = '^[a-zA-Z]+=' + self.range_variable.value + '+\.[a-zA-Z]+='  # regex for checking if comma was not typed (when no comma, then we have the following: 'limit = c.CreditLimit first = c.FirstName,')

    for item in lines:
      if not (re.compile(regex).match(item)): # first above regex validation
        self.errorMsg("Error: Incorrect syntax in select body --> " + item)
        return
      if re.compile(regex_against_comma).match(item):# second above regex validation
        self.errorMsg('Error - no comma between lines')
    # print self.range_variable.value
      # if previous == "" and self.selection[item].type == 'variablename':
      #   previous = self.selection[item].type
      # else:
      #   self.errorMsg('Error - select body starts with: ' + self.selection[item].value)

  def validateEndSection(self): # validates semicolon
    if len(self.end) == 0:      
      self.errorMsg("Error - no semicolon at the end of statement or unsupported character")
      return

      

  def insertIntoCorrectArray(self, tokenizerFlag, tokenItem):
    # Divide tokens from lexer into arrays where each array conforms to its valid section: i.e condition statement into conditions, selection into selections etc 
    if tokenizerFlag == 'range':
      self.queryrange.append(tokenItem)
    elif tokenizerFlag == 'conditionals':
      self.conditionals.append(tokenItem)
    elif tokenizerFlag == 'selection':
      self.selection.append(tokenItem)
    else:
      self.end.append(tokenItem)

  def printDividedCode(self):
    # Prints tokens in arrays created on the base of sections(range, expression, conditional and selection) recognizing
    print ""
    print "Range: "
    string = ""
    for item in self.queryrange:
      string += " " + str(item.value)
    print string

    print ""
    print "Conditionals: "
    string = ""
    for item in self.conditionals:
      string += " " + str(item.value)
    print string

    print ""
    print "Selection: "
    string = ''
    for item in self.selection:
      string += " " + str(item.value)
    print string
    print ""
    print "End: "
    string = ""
    for item in self.end:
      string += " " + str(item.value)         
    print string    







  # if tokenizerFlag == 'range':
  #         if tokenItem.type == 'where':
  #           self.Conditionals.appedn(tokenItem)
  #           tokenizerFlag = 'conditionals'
  #           continue
  #         self.Range.append(tokenItem)
  #       elif tokenizerFlag == 'conditionals':
  #         if tokenItem.type == 'select':
  #           self.Selection.append(tokenItem)
  #           tokenizerFlag = 'selection'
  #           continue
  #         self.Selection.append(tokenItem)
  #       else:
  #         print "df"



  # # Starting symbol
  # def start(self):
  #   # start -> program EOF
  #   print self.token.type
  #   if self.token.type == 'PRINT' or self.token.type == 'var' or self.token.type == 'ID' or self.token.type == 'EOF' or self.token.type == 'IF':
  #     self.program()
  #     self.take_token('EOF')
  #   else:
  #     self.error("Epsilon not allowed")

  # def program(self):
  #   # program -> statement program
  #   if self.token.type == 'PRINT' or self.token.type == 'ID' or self.token.type == 'IF':
  #     self.statement()
  #     self.program()
  #   # program -> eps
  #   else:
  #     pass

  # def statement(self):
  #   # statement -> print_stmt
  #   if self.token.type == 'PRINT':
  #     self.print_stmt()
  #   # statement -> assign_stmt
  #   elif self.token.type == 'ID':
  #     self.assign_stmt()
  #   # statement -> if_stmt
  #   elif self.token.type == 'IF':
  #     self.if_stmt()
  #   else:
  #     self.error("Epsilon not allowed")

  # # print_stmt -> PRINT value END
  # def print_stmt(self):
  #   if self.token.type == 'PRINT':
  #     self.take_token('PRINT')
  #     self.value()
  #     self.take_token('END')
  #     print "print_stmt OK"
  #   else:
  #     self.error("Epsilon not allowed")
   
  # # assign_stmt -> ID ASSIGN value END
  # def assign_stmt(self):
  #   if self.token.type == 'ID':
  #     self.take_token('ID')
  #     self.take_token('ASSIGN')      
  #     self.value()
  #     self.take_token('END')
  #     print "assign_stmt OK"
  #   else:
  #     self.error("Epsilon not allowed")
  
  # def value(self):
  #   # value -> NUMBER
  #   if self.token.type == 'NUMBER':
  #     self.take_token('NUMBER')
  #   # value -> ID
  #   elif self.token.type == 'ID':
  #     self.take_token('ID')
  #   else:
  #     self.error("Epsilon not allowed")

  # def if_stmt(self):
  #   # if_stmt -> IF ID THEN program ENDIF END
  #   if self.token.type == 'IF':
  #     self.take_token('IF')
  #     self.take_token('ID')
  #     self.take_token('THEN')
  #     self.program()
  #     self.take_token('ENDIF')
  #     self.take_token('END')
  #     print "if_stmt OK"
  #   else:
  #     self.error("Epsilon not allowed")