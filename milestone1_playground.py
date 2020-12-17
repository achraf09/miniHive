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
import raopt
import raopt_ver
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



print("###########################")
rastring="\project_{name}(\select_{gender='f' and age=16}(Person));"
sqlstmt="selEct distinct * FRom Person X, Eats WHere age=16"
expected1 = radb.parse.one_statement_from_string("\select_{Person.gender = 'f'}(Person);")
expected2 = radb.parse.one_statement_from_string("\select_{gender = 'm'} (Person \cross Eats);")
expected3 = radb.parse.one_statement_from_string("\project_{name}(\select_{gender='f' and age=16} Person);")
expected4 = radb.parse.one_statement_from_string("\select_{Person.name = 'Amy'} Person \join_{Person.name = Eats.name} Eats;")
print(expected2)
testSelect = radb.ast.Select(radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,'age'),radb.ast.sym.EQ,radb.ast.RANumber('16')),radb.ast.Select(radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,'name'),radb.ast.sym.EQ,radb.ast.RAString('f')),radb.ast.RelRef('Person')))
print(testSelect)

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
visited=[]
def rule_pushdownselection_help_get_cross(ra,visited):
    if isinstance(ra.inputs[0], radb.ast.Cross):
        visited.append(ra.inputs[0])
        return
    else:
        if isinstance(ra.inputs[0], radb.ast.RelRef):
            visited.append(ra.inputs[0])
            return
    rule_pushdownselection_help_get_cross(ra.inputs[0],visited)

def rule_push_down_selections(ra, dd):
    visited=[]
    selects = [ra]
#The thing here is to first elemenate the case where no pushdown selection is possible
#For e.g. if there is no cross, there is no need for pushing down the selections
#if there is a cross then we check the selections : if the condition's right part is a constant:
                                                        # we push it down after the cross before the table where it belongs
                                                    #if the condition is a attribute on both sides then:
                                                        # we group the selections that satisfy this case
    first_cross_relation = None
    #rule_pushdownselection_help_get_cross(ra,visited)
    while selects[-1].inputs is not None:
        inputs = selects[-1].inputs[0]
        if isinstance(inputs, radb.ast.Select):
            selects.append(inputs)
        elif isinstance(inputs, radb.ast.Cross):
            rule_pushdownselection_help_get_cross(ra,visited)
            break
        else:
            return ra

def rule_selection_split_help(ra,visited):
    if isinstance(ra.inputs[0],radb.ast.Cross):
        visited.append(ra)
        return
    rule_selection_split_help(ra.inputs[0],visited)
    rule_selection_split_help(ra.inputs[1],visited)



dd = {}
dd["Person"] = {"name": "string", "age": "integer", "gender": "string"}
dd["Eats"] = {"name": "string", "pizza": "string"}
dd["Serves"] = {"pizzeria": "string", "pizza": "string", "price": "integer"}
stmt = sqlparse.parse("SELECT DISTINCT * FROM Eats Eats1, Eats Eats2 Where Eats1.pizza = Eats2.pizza and Eats2.name = 'Amy'")[0]
actual = sql2ra.translate(stmt)
ra = raopt.rule_break_up_selections(actual)
print(dd.keys())
ra1=raopt.rule_push_down_selections(ra,dd)
ra2=raopt_ver.rule_introduce_joins(expected3)
print(ra1)
print(expected4)
##############################################
ra1= raopt.rule_break_up_selections(radb.parse.one_statement_from_string("\\rename_{P: *} Person \cross Eats;"))
#print(ra1)
#print(type(actual))
#print(paren(actual.cond.inputs[0]))
#print(ra)
#print(str(expected) == str(actual))


