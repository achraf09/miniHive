import sqlparse
import sqlparse.lexer
import sqlparse.keywords
import radb
import radb.ast
import radb.parse
from sqlparse import tokens
def sql_tokenize(string):
    """ Tokenizes a SQL statement into tokens.

    Inputs:
       string: string to tokenize.

    Outputs:
       a list of tokens.
    """
    tokens = []
    statements = sqlparse.parse(string)

    # SQLparse gives you a list of statements.
    for statement in statements:
        # Flatten the tokens in each statement and add to the tokens list.
        flat_tokens = sqlparse.sql.TokenList(statement.tokens).flatten()
        for token in flat_tokens:
            strip_token = str(token).strip()
            if len(strip_token) > 0:
                tokens.append(strip_token)

    newtokens = []
    keep = True
    for i, token in enumerate(tokens):
        if token == ".":
            newtoken = newtokens[-1] + "." + tokens[i + 1]
            newtokens = newtokens[:-1] + [newtoken]
            keep = False
        elif keep:
            newtokens.append(token)
        else:
            keep = True

    return newtokens


sql = "select distinct * from Person"
stmt = sqlparse.parse(sql)[0]
flat_tokens = sqlparse.sql.TokenList(stmt.tokens).flatten()
for token in flat_tokens:
    if token.ttype in tokens.Whitespace:
        continue
    else:
        print(token.ttype)
        token = str(token).strip()
        print(token)
        print("=====")
        #print(sqlparse.keywords.is_keyword(token))
print("#################-----")

#print(sqlparse.sql.Comparison(stmt.tokens))
for token in stmt.tokens:
    print(token)
    print(token.ttype)

print(stmt.tokens[-1])
print("--------------")

cond = radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None, 'age'), radb.ast.sym.EQ, radb.ast.RANumber('16'))
input = radb.ast.RelRef('Person')
select = radb.ast.Select(cond, input)
expected = radb.parse.one_statement_from_string("\select_{age=16}(Person);")
print(select) # Output
print(expected)
#for token in flat_tokens:
#    if token select and