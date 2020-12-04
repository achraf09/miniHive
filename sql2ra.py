import sqlparse
import radb
import radb.ast
import radb.parse
from sqlparse import tokens

stmt_dict = {}


def translate(stmt):
    index = 0
    stmt = sqlparse.parse(stmt)[0]
    for token in stmt.tokens:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            index += 1
            continue
        else:
            print(token.ttype)
            if token.ttype in tokens.Keyword or 'WHERE' in str(token).upper():
                if 'where' in str(token):
                    str_1 = str(token).split("where ")
                    stmt_dict['WHERE'] = str_1[1]
                    break
                stmt_dict[str(token).upper()] = get_keyword_attribute(stmt, token, index)
                token = str(token).upper()
            index += 1
            print(token)
    print(stmt_dict)
    # Next Step is to Use this dictionary to make the relational algebra thing


def get_keyword_attribute(stmt, key, index):
    list_items = []
    for token in stmt.tokens[index + 1:]:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            continue
        else:
            if token.ttype not in tokens.Keyword:
                if 'where' in str(token):
                    continue
                list_items.append(str(token).strip())
            else:
                if token.ttype in tokens.Keyword:
                    break
    return list_items


def define_cross_product(n, tables):
    if n == 0:
        return radb.ast.RelRef(tables[0])
    if n == 1:
        return radb.ast.Cross(radb.ast.RelRef(tables[0]), radb.ast.RelRef(tables[1]))
    else:
        return radb.ast.Cross(define_cross_product(n - 1, tables), radb.ast.RelRef(tables[n]))


translate("Select distinct * from Person, Eats")
