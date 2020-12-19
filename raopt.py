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
        else:
            if isinstance(ra,radb.ast.Cross):
                if isinstance(ra.inputs[0], radb.ast.Select):
                    rule_selection_split_help(ra.inputs[0].cond,visited)
                    sel = radb.ast.Cross(rule_selection_spilt_building(visited,ra.inputs[0].inputs[0]),ra.inputs[1])
                else:
                    rule_selection_split_help(ra.inputs[1].cond,visited)
                    sel = radb.ast.Cross(ra.inputs[0], rule_selection_spilt_building(visited,ra.inputs[1].inputs[0]))
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


#def rule_push_down_selections(ra, dd):
    #The thing here is to first elemenate the case where no pushdown selection is possible
    #For e.g. if there is no cross, there is no need for pushing down the selections
    #if there is a cross then we check the selections : if the condition's right part is a constant:
                                                            # we push it down after the cross before the table where it belongs
                                                        #if the condition is a attribute on both sides then:
                                                            # we group the selections that satisfy this case





