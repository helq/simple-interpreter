# module: tokrules.py
# author: helq
# license: wtfpl
# This module contains the type analizer and the interpreter

primitives = ['CONS', 'CAR', 'CDR', 'Not', 'ToString']

def isInfacts_list(id, facts_list):
    lenEnvs = len(facts_list)
    for i in range(lenEnvs-1,-1,-1):
        if id in facts_list[i]:
            return True
    return False

def getValueFromEnv(id, facts_list):
    lenEnvs = len(facts_list)
    for i in range(lenEnvs-1,-1,-1):
        if id in facts_list[i]:
            return facts_list[i][id]

def execute(stm, facts_list):
    if stm["type"] == "stm_value": return (stm["type_value"], stm["value"])

    if stm["type"] == "stm_op":
        op = stm["op"]
        typ1, val1 = execute(stm["value1"], facts_list)
        typ2, val2 = execute(stm["value2"], facts_list)
        if op in {'+','-','*','/','<','>'}:
            if typ1 != "number" or typ2 != "number":
                raise Exception("operation "+op+" valid only between numbers")
            if op == '+': return ('number', val1 + val2 )
            if op == '-': return ('number', val1 - val2 )
            if op == '*': return ('number', val1 * val2 )
            if op == '/': return ('number', val1 / val2 )
            if op == '<': return ('boolean', val1 < val2 )
            if op == '>': return ('boolean', val1 > val2 )
        if op in {'&','|'}:
            if typ1 != "boolean" or typ2 != "boolean":
                raise Exception("operation "+op+" valid only between booleans")
            if op == '&': return ('boolean', val1 and val2 )
            if op == '|': return ('boolean', val1 or val2 )
        if op == '.':
            if typ1 != "string" or typ2 != "string":
                raise Exception("operation . valid only between strings")
            return ('string', val1 + val2)
        if op == '=':
            if typ1 != typ2 or typ1 not in ['string', 'boolean', 'number', 'cons']:
                raise Exception("operation = valid only between equal types")
            return ('boolean', val1 == val2)

    if stm["type"] == "stm_if_then":
        typ_if, val_if = execute(stm["if"], facts_list)
        if typ_if != "boolean":
            raise Exception("`if` can only have boolean values")
        if val_if: return execute(stm["then"], facts_list)
        else:      return execute(stm["else"], facts_list)

    if stm["type"] == "stm_id":
        id = stm['id']
        if not isInfacts_list(id, facts_list):
            raise Exception("value `"+id+"' not found")
        depth_id = getValueFromEnv(id, facts_list)['depth']
        if depth_id == -1: # must have only a value
            v = getValueFromEnv(id, facts_list)
            return (v['type_value'], v['value'])
        else:
            new_facts_list = facts_list[:depth_id+1]
            return execute( getValueFromEnv(id, facts_list)['stm']
                          , new_facts_list)

    if stm["type"] == "stm_let":
        new_facts_list = facts_list[:]
        new_facts_list.append( stm["facts"] )
        return execute(stm["stm"], new_facts_list)

    if stm["type"] == "stm_func_call":
        id_func = stm['id_func']

        if id_func in primitives:
            args = stm["args"]
            return execute_primitive(id_func, args, facts_list)

        if not isInfacts_list(id_func, facts_list):
            raise Exception("function `"+id_func+"' not found")

        func_node = getValueFromEnv(id_func, facts_list)
        depth_func = func_node['depth']
        params = func_node['params']
        args = stm["args"]

        if depth_func < len(facts_list):
            new_facts_list = facts_list[:depth_func]
            new_facts = facts_list[depth_func].copy()
        elif depth_func == len(facts_list):
            new_facts_list = facts_list[:depth_func]
            new_facts = func_node['facts'].copy()
        else: # this must never happen
            raise Exception("trying to access to a fact that is not in the scope, this is a bug from the interpreter")

        if len(args) != len(params):
            raise Exception("different number of parameters calling function `"
                            +stm['id_func']+"'")

        for i in range(len(params)):
            if params[i]['type'] == 'id_func' and args[i]['type'] != 'id_func':
                raise Exception("declared a function `"+params[i]['id_func']
                               +"' as parameter in `"+id_func
                               +"', but have been passed a: "+args[i]['type'])
            if args[i]['type'] == 'id_func' and params[i]['type'] != 'id_func':
                raise Exception("declared a value `"+params[i]['id']
                               +"' as parameter in `"+id_func
                               +"', but have been passed a: id_func `"
                               +args[i]['id_func']+"'")

            if params[i]['type'] == 'id_func':
                # extracting function from facts_list
                tmp = getValueFromEnv(args[i]['id_func'], facts_list).copy()
                new_id_func = params[i]['id_func']
                # changing name of the function in the new_facts
                tmp['name'] = new_id_func
                new_facts[new_id_func] = tmp
            else: # then the argument is an statment
                new_id = params[i]['id']
                typ, val = execute(args[i], facts_list) # getting statement value

                new_val = {'type': 'val',
                           'name': new_id,
                           'type_value': typ,
                           'value': val,
                           'depth': -1}
                new_facts[new_id] = new_val

        new_facts_list.append(new_facts)
        return execute( func_node['stm'] , new_facts_list)

    # this must never happen
    return ("error: invalid type", "")

def add_depth_to_facts(facts, depth):
    for k, fact in facts.items():
        fact['depth'] = depth
        fact['facts'] = facts
        add_depth_to_facts_in_stm(fact["stm"], depth)

def add_depth_to_facts_in_stm(stm, depth):
    if stm["type"] in ["stm_value", "stm_id", "stm_func_call"]:
        return
    if stm["type"] == "stm_op":
        add_depth_to_facts_in_stm(stm["value1"], depth)
        add_depth_to_facts_in_stm(stm["value2"], depth)
    if stm["type"] == "stm_if_then":
        add_depth_to_facts_in_stm(stm["if"], depth)
        add_depth_to_facts_in_stm(stm["then"], depth)
        add_depth_to_facts_in_stm(stm["else"], depth)
    if stm["type"] == "stm_let":
        add_depth_to_facts_in_stm(stm["stm"], depth+1)
        add_depth_to_facts(stm["facts"], depth+1)

def execute_ast(ast):
    add_depth_to_facts(ast['facts'], 0)
    add_depth_to_facts_in_stm(ast['stm'], 0)
    return execute(stm=ast["stm"], facts_list=[ast["facts"]])

def execute_primitive(id_func, args, facts_list):
    if id_func == "CONS":
        if len(args) != 2:
            raise Exception("CONS has only two parameters")
        if args[0]['type'] == 'id_func' or args[1]['type'] == 'id_func':
            raise Exception("CONS do not accept functions as arguments")
        val1 = execute(args[0], facts_list)
        val2 = execute(args[1], facts_list)
        return ('cons', (val1, val2) )

    if id_func in ['CAR', 'CDR', 'Not', 'ToString']:
        if len(args) != 1:
            raise Exception(id_func+" has only one parameter")
        if args[0]['type'] == 'id_func':
            raise Exception(id_func+" do not accept functions as arguments")
        val = execute(args[0], facts_list)

        if id_func == 'CAR':
            if val[0] != 'cons': raise Exception("value for CAR function must be of type `cons'")
            return val[1][0]
        if id_func == 'CDR':
            if val[0] != 'cons': raise Exception("value for CDR function must be of type `cons'")
            return val[1][1]
        if id_func == 'Not':
            if val[0] != 'boolean': raise Exception("value for Not function must be of type `boolean'")
            return (val[0], not val[1])
        if id_func == 'ToString':
            if val[0] == 'cons':
                return ( 'string', repr(cons_to_tuples(val)) )
            return ('string', repr(val[1]))

    if id_func in primitives: # this must never happen
        raise Exception("yet we do not support this primitive, :S")

def cons_to_tuples(cons):
    l = cons[1][0]
    r = cons[1][1]
    if l[0] == 'cons' and l[1] != 'nil': newl = cons_to_tuples(l)
    else:              newl = l[1]
    if r[0] == 'cons' and r[1] != 'nil': newr = cons_to_tuples(r)
    else:              newr = r[1]
    return (newl, newr)
