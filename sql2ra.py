import sqlparse
import radb
import radb.ast
import radb.parse
from sqlparse import tokens
import re
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
                if 'WHERE' in str(token).upper():
                    str_1 = str(token).split("where ")
                    stmt_dict['WHERE'] = str_1[1]
                    break
                stmt_dict[str(token).upper()] = get_keyword_attribute(stmt, token, index)
                token = str(token).upper()
            index += 1
            print(token)
    print(stmt_dict)
    # Next Step is to Use this dictionary to make the relational algebra thing


def get_keyword_attribute(stmt, key, index):#Function that groups each Keyword with corresponding attributes
    list_items = []
    for token in stmt.tokens[index + 1:]:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            continue
        else:
            if token.ttype not in tokens.Keyword:
                if 'WHERE' in str(token).upper():
                    continue
                list_items.append(str(token).strip())
            else:
                if token.ttype in tokens.Keyword:
                    break
    return list_items


def define_cross_product(n, tables): #construct cross products from From-Clause
    if n == 0:
        return radb.ast.RelRef(tables[0])
    if n == 1:
        return radb.ast.Cross(radb.ast.RelRef(tables[0]), radb.ast.RelRef(tables[1]))
    else:
        return radb.ast.Cross(define_cross_product(n - 1, tables), radb.ast.RelRef(tables[n]))

def get_where_conditions_as_list(str_):#return list of where conditions as a list of items
    str_ = str_.split('and')
    str_1 = []
    for st in str_:
        st.strip(' ')
        if '=' in st:
            str_1 += re.split('(\W+)=', str(st))
            # for s in str_1:
            print(str_1)
            # str_1=[]
        if '<' in st:
            str_1 = re.split('(\W+)<', str(st))
            print(str_1)
            str_1 = []
    stripped_str = []
    for st in str_1:
        if st == ' ':
            continue
        st = st.strip()
        print(st)
        stripped_str.append(st)
    return stripped_str


def extract_cond(l,cond): #create the select condition from the where statement
    if l == 1:
        if '.' in cond[0] and "'" in cond[1]:
            c = re.split('\.',cond[0])
            return radb.ast.ValExprBinaryOp(radb.ast.AttrRef(c[0],c[1]), radb.ast.sym.EQ, radb.ast.RAString(cond[1]))
        else:
            if '.' in cond[0] and "'" not in cond[1]:
                c = re.split('\.', cond[0])
                return radb.ast.ValExprBinaryOp(radb.ast.AttrRef(c[0], c[1]), radb.ast.sym.EQ, radb.ast.RANumber(cond[1]))
            else:
                if '.' not in cond[0] and "'" in cond [1]:
                    return radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,cond[0]), radb.ast.sym.EQ, radb.ast.RAString(cond[1]))
                else:
                    return radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,cond[0]),radb.ast.sym.EQ,radb.ast.RANumber(cond[1]))
    else:
        if '.' in cond[l-1] and "'" in cond[l]:
            c = re.split('\.', cond[l-1])
            return radb.ast.ValExprBinaryOp(extract_cond(l-2,cond),radb.ast.sym.AND , radb.ast.ValExprBinaryOp(radb.ast.AttrRef(c[0],c[1]), radb.ast.sym.EQ, radb.ast.RAString(cond[l])))
        else:
            if '.' in cond[l-1] and "'" not in cond[l]:
                c = re.split('\.', cond[l-1])
                return radb.ast.ValExprBinaryOp(extract_cond(l-2,cond),radb.ast.sym.AND , radb.ast.ValExprBinaryOp(radb.ast.AttrRef(c[0], c[1]), radb.ast.sym.EQ, radb.ast.RANumber(cond[l])))
            else:
                if '.' not in cond[l-1] and "'" in cond [l]:
                    return radb.ast.ValExprBinaryOp(extract_cond(l-2,cond),radb.ast.sym.AND , radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,cond[l-1]), radb.ast.sym.EQ, radb.ast.RAString(cond[l])))
                else:
                    return radb.ast.ValExprBinaryOp(extract_cond(l-2,cond),radb.ast.sym.AND , radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None,cond[l-1]),radb.ast.sym.EQ,radb.ast.RANumber(cond[l])))


translate("Select distinct * from Person, Eats where age=16 and Person.gender='f'")
