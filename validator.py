# Simple example of parsing
# Bartosz Sawicki, 2014-03-13

from scanner import *
from parser import *

input_string = '''
x := 5;
y := x;
PRINT 64;
'''

# input_string = '''
# PRINT x;
#     IF quantity THEN
#         total := total;
#         tax := 0.05;
#     ENDIF;
#  '''

input_string = '''
 var query_orderby1 = from c in svcContext.ContactSet
 where !c.CreditLimit.Equals(null)
groupby c.CreditLimit descending
select new
{
 limit = c.CreditLimit,
first = c.FirstName,
last = c.LastName   
 };

'''

print input_string
scanner = Scanner(input_string)


parser = Parser(scanner)
parser.start()

# def wznowienia():
#     print("wstrzymuje dzialanie")
#     yield 1
#     print("wznawiam dzialanie")

#     print("wstrzymuje dzialanie")
#     yield 2
#     print("wznawiam dzialanie")

# for i in wznowienia():
#     print("Zwrocono wartosc: " + str(i))
  
