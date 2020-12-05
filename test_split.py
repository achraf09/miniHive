import re
import sqlparse
import sqlparse.lexer
import sqlparse.keywords
import radb
import radb.ast
import radb.parse
from sqlparse import tokens
str_ = "age=16 and Person.name='f'"
str_ = str_.split('and')
str_1=[]
for st in str_:
    st.strip(' ')
    if '=' in st:
        str_1 += re.split('=', str(st))
        # for s in str_1:
        print(str_1)
        #str_1=[]
    if '<' in st:
        str_1 = re.split('(\W+)<', str(st))
        print(str_1)
        str_1=[]
stripped_str=[]
for st in str_1:
    if st==' ':
        continue
    st = st.strip()
    print(st)
    stripped_str.append(st)
print(stripped_str)


cond = radb.ast.ValExprBinaryOp((radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None, 'age'), radb.ast.sym.EQ, radb.ast.RANumber('16'))), radb.ast.sym.OR,radb.ast.ValExprBinaryOp(radb.ast.AttrRef(None, 'age'), radb.ast.sym.EQ, radb.ast.RANumber('16')))
print(cond)


def extract_cond(l,cond):
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


conds = extract_cond(len(stripped_str)-1,stripped_str)
print(conds)