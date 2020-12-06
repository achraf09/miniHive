import sqlparse
import radb
import radb.ast
import radb.parse
from sqlparse import tokens
import re



def translate(stmt):
    index = 0
    stmt_dict = {}
    for token in stmt.tokens:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            index += 1
            continue
        else:
            if token.ttype in tokens.Keyword or 'WHERE' in str(token).upper():
                if 'WHERE' in str(token).upper():
                    str_1 = str(token).split("where ")
                    stmt_dict['WHERE'] = str_1[1]
                    break
                stmt_dict[str(token).upper()] = get_keyword_attribute(stmt, token, index)
                token = str(token).upper()
            index += 1
    tables = stmt_dict.get('FROM');
    cross = define_cross_product(len(tables) - 1, tables)
    # Next Step is to Use this dictionary to make the relational algebra thing
    if stmt_dict.get('SELECT')[0] == '*':
        if 'WHERE' not in stmt_dict.keys():
            result = cross
        else:
            stripped_str= get_where_conditions_as_list(stmt_dict.get('WHERE'))
            cond = extract_cond(len(stripped_str) - 1, stripped_str)
            result = define_select_with_cross(cond, cross)
    else:
        list_projections = extract_projection(stmt_dict.get('SELECT'))
        if 'WHERE' not in stmt_dict.keys():
            result = define_projection_with_cross(list_projections,cross)
        else:
            stripped_str = get_where_conditions_as_list(stmt_dict.get('WHERE'))
            cond = extract_cond(len(stripped_str) - 1, stripped_str)
            select = define_select_with_cross(cond, cross)
            result = define_projection_with_cross(list_projections,select)
    return result




def get_keyword_attribute(stmt, key, index):#Function that groups each Keyword with corresponding attributes
    list_items = []
    for token in stmt.tokens[index + 1:]:
        if token.ttype in tokens.Whitespace or 'DISTINCT' == token.normalized:
            continue
        else:
            if token.ttype not in tokens.Keyword:
                if 'WHERE' in str(token).upper():
                    continue
                st = str(token).split(', ')
                list_items.extend(st)
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
            str_1 += re.split('=', str(st))
            # str_1=[]
        # if '<' in st:
        #     str_1 = re.split('(\W+)<', str(st))
        #     str_1 = []
    stripped_str = []
    for st in str_1:
        if st == ' ':
            continue
        st = st.strip()
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


def extract_projection(proj_list):###Get the projection names and prepare them for the function that gathers them with the crosses
    list_projection=[]
    if isinstance(proj_list, str):
        if '.' in proj_list:
            p = re.split('\.',proj_list)
            list_projection.extend(radb.ast.AttrRef(p[0],p[1]))
        else:
            list_projection.extend(radb.ast.AttrRef(None, proj_list))
    else:
        for item in proj_list:
            if '.' in item:
                p = re.split('\.', item)
                list_projection.append(radb.ast.AttrRef(p[0], p[1]))
            else:
                list_projection.append(radb.ast.AttrRef(None, item))

    return list_projection


def define_projection_with_cross(list_projection, cross):###Function that gathers projection with crosses
    return radb.ast.Project(list_projection, cross)


def define_select_with_cross(list_cond, cross):
    return radb.ast.Select(list_cond,cross)

