import radb
import radb.ast


def rule_break_up_selections(ra):
    visited = []
    sel = ra
    if isinstance(ra, radb.ast.Select):
        rule_selection_split_help(ra.cond, visited)
        sel = rule_selection_spilt_building(visited, ra.inputs[0])
    else:
        if isinstance(ra, radb.ast.Project):
            rule_selection_split_help(ra.inputs[0].cond, visited)
            sel = radb.ast.Project(ra.attrs, rule_selection_spilt_building(visited, ra.inputs[0].inputs[0]))
        else:
            if isinstance(ra,radb.ast.Cross): #not bother with breaking up selections if no select is in the statement
                if isinstance(ra.inputs[0], radb.ast.Select):
                    rule_selection_split_help(ra.inputs[0].cond,visited)
                    sel = radb.ast.Cross(rule_selection_spilt_building(visited,ra.inputs[0].inputs[0]),ra.inputs[1])
                elif isinstance(ra.inputs[1],radb.ast.Select):
                    rule_selection_split_help(ra.inputs[1].cond,visited)
                    sel = radb.ast.Cross(ra.inputs[0], rule_selection_spilt_building(visited,ra.inputs[1].inputs[0]))
    return sel


def rule_selection_spilt_building(ra, inputs):#build up selections on top of each other
    if len(ra) > 1:
        return radb.ast.Select(ra.pop(0), rule_selection_spilt_building(ra, inputs))
    else:
        return radb.ast.Select(ra[0], inputs)


def rule_selection_split_help(ra, visited):#Function that visits the selection tree node
    if isinstance(ra.inputs[0], radb.ast.AttrRef):
        visited.append(ra)
        return
    rule_selection_split_help(ra.inputs[0], visited)
    rule_selection_split_help(ra.inputs[1], visited)


def rule_push_down_selections(ra, dd):
    if isinstance(ra, radb.ast.Select):
        ra = pushdown_selects(ra,dd)
    else:
        stmt_inputs=[]
        if ra.inputs is not None:
            for i in range(0, len(ra.inputs)):
                stmt_inputs.append(rule_push_down_selections(ra.inputs[i],dd))
        ra.inputs = stmt_inputs

    return ra


def pushdown_selects(ra,dd):
    selects = [ra]
    cross_product = None
    return pushdown_selects_help(ra,dd,selects,cross_product)


def pushdown_selects_help(ra,dd,selects,cross_product):
    if selects[-1].inputs is None:
        return rule_selection_pushdown_build(cross_product,selects,dd)
    inputs = selects[-1].inputs[0]
    if isinstance(inputs, radb.ast.Select):
        selects.append(inputs)
    elif isinstance(inputs, radb.ast.Cross):
        cross_product = inputs
        return rule_selection_pushdown_build(cross_product,selects,dd)
    else:
        return ra
    return pushdown_selects_help(ra,dd,selects,cross_product)


def rule_selection_pushdown_build(cross_product,selects,dd):
    ra_1= cross_product
    for select in selects:
        entry = ra_1
        old_stmt = None
        old_index = None
        while entry is not None:
            if isinstance(entry, radb.ast.Cross):
                for i in range(len(entry.inputs)):
                    if isinstance(entry.inputs[i], radb.ast.Cross):
                        continue
                    else:
                        index = get_select_index(select, entry.inputs[i], dd, i)
                        if index is None:
                            # insertion point found
                            if old_stmt is None:
                                select.inputs[0] = ra_1
                                ra_1 = select
                            else:
                                select.inputs[0] = old_stmt.inputs[old_index]
                                old_stmt.inputs[i] = select
                            entry = None
                        else:
                            old_stmt = entry
                            old_index = index
                            entry = entry.inputs[index]

                        break

            elif isinstance(entry, radb.ast.Select):
                old_stmt = entry
                old_index = 0
                entry = entry.inputs[0]

            else:
                select.inputs[0] = old_stmt.inputs[old_index]
                old_stmt.inputs[old_index] = select
                break
    return ra_1


def rule_merge_selections(ra):
    stmt_inputs=[]
    if ra.inputs is not None:
        if isinstance(ra, radb.ast.Select):
            return rule_merge_selections_help(ra)
        for i in range(len(ra.inputs)):
            stmt_inputs.append(rule_merge_selections(ra.inputs[i]))
    ra.inputs = stmt_inputs
    return ra


def rule_merge_selections_help(ra):
    if ra.inputs is None or not isinstance(ra.inputs[0], radb.ast.Select):
        return ra
    ra.cond = radb.ast.ValExprBinaryOp(ra.cond,radb.ast.sym.AND, ra.inputs[0].cond)
    ra.inputs[0] = ra.inputs[0].inputs[0]
    return rule_merge_selections_help(ra)


def construct_selects_func(ra_1,cross_product,selects,dd,select,entry,old_stmt,old_index):
    if entry is None:
        #selects.pop(0)
        return rule_selection_pushdown_build(cross_product,selects,dd)
    if isinstance(entry,radb.ast.Cross):
        for i in range(len(entry.inputs)):
            if isinstance(entry.inputs[i], radb.ast.Cross):
                continue
            else:
                index = get_select_index(select,entry.inputs[i],dd,i)
                if index is None:
                    if old_stmt is None:
                        select.inputs[0] = ra_1
                        ra_1 = select
                    else:
                        select.inputs[0] = old_stmt.inputs[old_index]
                        old_stmt.inputs[0] = select
                    entry = None
                else:
                    old_stmt = entry
                    old_index = index
                    entry = entry.inputs[index]
                #selects.pop(0)
        return construct_selects_func(ra_1,cross_product,selects,dd,select,entry,old_stmt,old_index)
#    return construct_selects_func(ra_1,cross_product,selects,dd,select,entry,old_stmt,old_index)


def rule_introduce_joins_help(cond,inputs):
    input = inputs[0]
    for i in range(0, len(cond)):
        for j in range(1, len(inputs) - 1):
            input = radb.ast.Join(input, cond[i], inputs[j])
            inputs[j] = inputs[j + 1]
    return input

def rule_introduce_joins(ra):
    inputs=[]
    if ra.inputs is not None:
        for i in range(0, len(ra.inputs)):
                inputs.append(rule_introduce_joins(ra.inputs[i]))
    ra.inputs=inputs
    if isinstance(ra, radb.ast.Select):
        if join_elegible(ra):
            ra = radb.ast.Join(ra.inputs[0].inputs[0], ra.cond, ra.inputs[0].inputs[1])
    return ra


def join_elegible(ra):
    if not isinstance(ra.cond, radb.ast.ValExprBinaryOp):
        return False
    stmt = ra.inputs[0]
    if not isinstance(stmt, radb.ast.Cross) and not isinstance(stmt, radb.ast.Join):
        return False

    if isinstance(ra.cond.inputs[0], radb.ast.ValExprBinaryOp):
        for cond in ra.cond.inputs:
            rel_left = get_rel_attr(cond.inputs[0], stmt)
            rel_right = get_rel_attr(cond.inputs[1], stmt)
            if rel_left == rel_right:
                return False
        return True
    else:
        rel_left = get_rel_attr(ra.cond.inputs[0], stmt)
        rel_right = get_rel_attr(ra.cond.inputs[1], stmt)
        return rel_right != rel_left

def get_rel_attr(attr, rel):
    attrRel = attr.rel

    if isinstance(rel.inputs[0], radb.ast.Rename) or isinstance(rel.inputs[0], radb.ast.RelRef):
        index = 0
    else:
        index = 1
    relname=name_rel(rel.inputs[index])
    if relname == attrRel:
        return index
    else:
        return (index + 1) % 2
# def rule_introduce_joins(ra):
#     inputs =[]
#     rule_introduce_joins_help(ra,inputs)
#     ra.inputs = inputs
#     if isinstance(ra,radb.ast.Select):
#         print(ra.inputs[0].inputs[0])
#         print(ra.inputs[0].inputs[1])
# def split_stmt(ra,inputs):
#     if ra is not None:
#         inputs.append(ra)
#         if isinstance(ra, radb.ast.Select):
#             split_stmt(ra.cond, inputs)
#         for item in ra.inputs:
#             split_stmt(item,inputs)
#
# def rule_introduce_joins(ra):
#     inputs = []
#     inputs.append(ra)
#     split_stmt(ra,inputs)
#     inputs = clean_list(inputs)
#     rels = [x for x in inputs if isinstance(x, radb.ast.RelRef) or isinstance(x, radb.ast.Rename)]
#     valExpr = [x for x in inputs if isinstance(x, radb.ast.ValExprBinaryOp)]
#     cross = [x for x in inputs if isinstance(x, radb.ast.Cross)]
#     tables = []
#     join = None
#     projects = [p for p in inputs if isinstance(p,radb.ast.Project)]
#     for item in cross:
#         for rel in item.inputs:
#             tables.append(rel)
#     if len(cross) < 1:
#         return ra
#     elif len(cross) > 1 :
#         join = rule_introduce_joins_help(valExpr[::-1], rels)
#     else:
#         if len(tables) == 2:
#             return radb.ast.Join(tables[0],valExpr[0], tables[1])
#     if len(projects) > 0:
#         projects[0].inputs[0] = join
#         return projects[0]
#     return join
#
# def clean_list(l):
#     res = []
#     visited = set()
#     for v in l:
#         if v not in visited:
#             res.append(v)
#             visited.add(v)
#     return res
def get_select_index(select,rel,dd,index):
    rel = get_attr_relation(rel)
    rels = get_attr_relation_cross(rel)
    left = attribute_exists(rels,select.cond.inputs[0], dd)
    right = left
    if len(select.cond.inputs) > 1 and isinstance(select.cond.inputs[1], radb.ast.AttrRef):
        if len(get_rels_for_attr(select.cond.inputs[1],dd)) >0:
            right = attribute_exists(rels,select.cond.inputs[1], dd)
    if left and right:
        return index
    elif not right and not left:
        return (index + 1) % 2
    else:
        return None

def get_attr_relation_cross(rel):
    if isinstance(rel,radb.ast.Cross):
        rels =[]
        rels.extend(get_attr_relation_cross(rel.inputs[0]))
        rels.extend(get_attr_relation_cross(rel.inputs[1]))
        return rels
    else:
        return [rel]

def get_rels_for_attr(attr, dd):
    if attr.rel is None:
        rels = []
        for rel in dd:
            if attr.name in dd.get(rel):
                rels.append(rel)
        return rels
    else:
        return {attr.rel}

def attribute_exists(rels,attrs, dd):
    rel_cand = get_rels_for_attr(attrs, dd)
    for rel in rels:
        if str(rel) in rel_cand:
            return True
    return False

# def rule_pushdownselection_help_get_cross(ra,visited):
#     if isinstance(ra.inputs[0], radb.ast.Cross):
#         visited.append(ra.inputs[0])
#         return
#     else:
#         if isinstance(ra.inputs[0], radb.ast.RelRef):
#             visited.append(ra.inputs[0])
#             print(isinstance(visited[0],radb.ast.RelRef))
#             return
#     rule_pushdownselection_help_get_cross(ra.inputs[0],visited)
#     return visited


def get_attr_relation(rel):
    if not isinstance(rel, radb.ast.Select):
        if isinstance(rel,radb.ast.Rename):
            rel = rel.relname
        return rel
    rel = rel.inputs[0]
    return get_attr_relation(rel)




def name_rel(rel):
    if isinstance(rel,radb.ast.RelRef):
        return rel.rel
    elif isinstance(rel, radb.ast.Rename):
        return rel.relname
    else:
        return name_rel(rel.inputs[0])






