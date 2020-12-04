import re
import sqlparse
import sqlparse.lexer
import sqlparse.keywords
import radb
import radb.ast
import radb.parse
from sqlparse import tokens
str = "age=16 and female='f'"

str_1= re.split('and', str)
res = re.findall(r'[0-9\.]+|[^0-9\.]+|[^a-z]+|[^A-Z]+', str)
print(str_1)
print(res)

import sqlparse
import sqlparse.lexer
import sqlparse.keywords
import radb
import radb.ast
import radb.parse
from sqlparse import tokens


expected = radb.parse.one_statement_from_string("Person \cross Eats;")
# print(select) # Output
print(expected)