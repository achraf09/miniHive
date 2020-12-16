import sqlparse
import sqlparse.lexer
import sqlparse.keywords
import radb
import radb.ast
import radb.parse
from sqlparse import tokens
import sys
import re
import sql2ra
sys.setrecursionlimit(1500)
# def sql_tokenize(string):
#     """ Tokenizes a SQL statement into tokens.
#
#     Inputs:
#        string: string to tokenize.
#
#     Outputs:
#        a list of tokens.
#     """
#     tokens = []
#     statements = sqlparse.parse(string)
#
#     # SQLparse gives you a list of statements.
#     for statement in statements:
#         # Flatten the tokens in each statement and add to the tokens list.
#         flat_tokens = sqlparse.sql.TokenList(statement.tokens).flatten()
#         for token in flat_tokens:
#             strip_token = str(token).strip()
#             if len(strip_token) > 0:
#                 tokens.append(strip_token)
#
#     newtokens = []
#     keep = True
#     for i, token in enumerate(tokens):
#         if token == ".":
#             newtoken = newtokens[-1] + "." + tokens[i + 1]
#             newtokens = newtokens[:-1] + [newtoken]
#             keep = False
#         elif keep:
#             newtokens.append(token)
#         else:
#             keep = True
#
#     return newtokens

stmt_dict={}
sql = "Select distinct name From Person, Eats Where age=16"
stmt = sqlparse.parse(sql)[0]
flat_tokens = sqlparse.sql.TokenList(stmt.tokens).flatten()
for token in flat_tokens:
    if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
        continue
    else:
        type_token = token.ttype
        token = str(token).strip()
        token_string = token
        print(f"{type_token}, {token_string}")
        print("=====")
        #print(sqlparse.keywords.is_keyword(token))
print("#################-----")

#print(sqlparse.sql.Comparison(stmt.tokens))
for token in stmt.tokens:
    if token.ttype in tokens.Whitespace:
        continue
    else:
        print(token)
        print(token.ttype)
test = [token.split('from')[0] for token in flat_tokens]
print(test)
#print(stmt.tokens[-1])
print("--------------")
print(stmt.tokens[0])
#
# cond = radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None, 'age'), radb.ast.sym.EQ, radb.ast.RANumber('16'))
# input = radb.ast.RelRef('Person')
# select = radb.ast.Select(cond, input)
# expected = radb.parse.one_statement_from_string("Person;")
# print(select) # Output
# print(expected)
#for token in flat_tokens:
#    if token select and
def defin_cross_product(n,tables):
    if n == 0:
        return radb.ast.RelRef(tables[0])
    if n == 1:
        return radb.ast.Cross(radb.ast.RelRef(tables[0]), radb.ast.RelRef(tables[1]))
    else:
        return radb.ast.Cross(defin_cross_product(n-1,tables), radb.ast.RelRef(tables[n]))

# stmt_dict = {'SELECT': ['*'], 'FROM': ['Person', 'Eats', 'Pizza','Serves','Pizzeria'], 'WHERE':['age = 16']}
# if stmt_dict.get('SELECT')[0] == '*':
#     if 'WHERE' not in stmt_dict.keys():
#         tables = stmt_dict.get('FROM');
#         if len(tables) == 1:
#             input_ = radb.ast.RelRef(tables[0])
#         else:
#             input_ = defin_cross_product(len(tables)-1,tables)
#     else:
#         where_stmt = str(stmt_dict.get('WHERE'))

print("###########################")
rastring="\project_{name}(\select_{gender='f' and age=16}(Person));"
sqlstmt="selEct distinct * FRom Person X, Eats WHere age=16"
expected1 = radb.parse.one_statement_from_string("\select_{Person.gender = 'f'}(Person);")
expected2 = radb.parse.one_statement_from_string("\select_{Person.gender = 'f' and age=16}(Person);")
expected3 = radb.parse.one_statement_from_string("\select_{Person.gender='f' and Person.age=16}(Person) \cross Eats;")
expected4 = radb.parse.one_statement_from_string("\select_{Person.gender = 'f'} (\select_{Person.age = 16} Person) \cross Eats;")
print(expected2)
testSelect = radb.ast.Select(radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,'age'),radb.ast.sym.EQ,radb.ast.RANumber('16')),radb.ast.Select(radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,'name'),radb.ast.sym.EQ,radb.ast.RAString('f')),radb.ast.RelRef('Person')))
print(testSelect)
#ren = radb.ast.Rename('A', None, radb.ast.RelRef('Person'))

#print(ren)
#st= "Person A"
#str_1 = re.split(' ', str(st))
#print(str_1)
stmt = sqlparse.parse("Select * From Eats  Where E.pizza = 'mushroom' and E.price = 10")[0]
actual = sql2ra.translate(stmt)
#ra = radb.ast.Select(actual.cond.inputs[0],radb.ast.Select(actual.cond.inputs[1],actual.inputs[0]))
#print(type(actual.cond.inputs[0]) == radb.ast.ValExprBinaryOp)
#print(len(actual.inputs))
def rule_selection_split(ra):
     visited=[]
     if isinstance(ra, radb.ast.Select):
         rule_selection_split_help(ra.cond,visited)
         sel = rule_selection_spilt_building(visited,ra.inputs[0])
     else:
         if isinstance(ra,radb.ast.Project):
             rule_selection_split_help(ra.inputs[0].cond,visited)
             sel = radb.ast.Project(ra.attrs,rule_selection_spilt_building(visited,ra.inputs[0].inputs[0]))
     return sel


def rule_selection_spilt_building(ra,inputs):
    if len(ra) > 1:
        return radb.ast.Select(ra.pop(0),rule_selection_spilt_building(ra,inputs))
    else:
        return radb.ast.Select(ra[0],inputs)
#    if n==0:
#        return radb.ast.Select(ra[n],inputs[0])
#    else:
#        l=radb.ast.Select(ra[n-1],inputs[0])
#        return radb.ast.Select(rule_selection_spilt_building(ra,n-2,inputs),radb.ast.Select(ra[n-1],inputs[0]))


def rule_selection_split_help(ra,visited):
    if isinstance(ra.inputs[0],radb.ast.AttrRef):
        visited.append(ra)
        return
    rule_selection_split_help(ra.inputs[0],visited)
    rule_selection_split_help(ra.inputs[1],visited)
# # while ra.cond.inputs[0] != radb.ast.AttrRef:
# #     if
# print(isinstance(actual.cond.inputs[0].inputs[1],radb.ast.ValExprBinaryOp))
# print(actual.cond.inputs[0].inputs[0].inputs[0])
# print(actual.to_json())
#visited=[]
print(actual)
##############################################
ra1= rule_selection_split(actual)
print(ra1)
#print(type(actual))
#print(paren(actual.cond.inputs[0]))
#print(ra)
#print(str(expected) == str(actual))


