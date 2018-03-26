# Simple example of parsing
# Bartosz Sawicki, 2014-03-13

from scanner import *
from parser import *

input_string = '''var query_orderby1 = from c in svcContext.ContactSet
where c.CreditLimit.Equals(null)
orderby c.CreditLimit descending
select new
{
  limit = c.CreditLimit,
  first = c.FirstName,
  last = c.LastName
};'''

print input_string
scanner = Scanner(input_string)


parser = Parser(scanner)
parser.start()