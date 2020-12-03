import sqlparse
import radb
import radb.ast
import radb.parse
from sqlparse import tokens

stmt_dict={}
def translate(stmt):

    index = 0
    stmt = sqlparse.parse(stmt)[0]
    for token in stmt.tokens:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            index += 1
            continue
        else:
            print(token.ttype)
            if token.ttype in tokens.Keyword or 'WHERE' in token.normalized:

                stmt_dict[str(token).upper()] = get_keyword_attribute(stmt, token, index)
                token = str(token).upper()
            index += 1
            print(token)
    print(stmt_dict)
def get_keyword_attribute(stmt,key,index):
    list_items=[]
    for token in stmt.tokens[index+1:]:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            continue
        else:
            if token.ttype not in tokens.Keyword :
                if 'where' in str(token):
                    continue
                list_items.append(str(token).strip())
            else:
                if token.ttype in tokens.Keyword:
                    break
    return list_items

translate("Select distinct * from Person where age = 16")
