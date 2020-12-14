import radb
import radb.ast


def rule_break_up_selections(ra):
    visited = []
    if isinstance(ra, radb.ast.Select):
        rule_selection_split_help(ra.cond, visited)
        sel = rule_selection_spilt_building(visited, ra.inputs[0])
    else:
        if isinstance(ra, radb.ast.Project):
            rule_selection_split_help(ra.inputs[0].cond, visited)
            sel = radb.ast.Project(ra.attrs, rule_selection_spilt_building(visited, ra.inputs[0].inputs[0]))
    return sel


def rule_selection_spilt_building(ra, inputs):
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
