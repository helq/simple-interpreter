# module: tokrules.py
# author: helq
# license: wtfpl
# This module contains the type analizer and the interpreter

primitives = ['CONS', 'CAR', 'CDR', 'Not', 'ToString']

def isInEnvironments(id, environments):
    lenEnvs = len(environments)
    for i in range(lenEnvs-1,-1,-1):
        if id in environments[i]:
            return True
    return False

def getValueFromEnv(id, environments):
    lenEnvs = len(environments)
    for i in range(lenEnvs-1,-1,-1):
        if id in environments[i]:
            return environments[i][id]

def execute(stm, environments):
    if stm["type"] == "stm_value": return (stm["type_value"], stm["value"])

    if stm["type"] == "stm_op":
        op = stm["op"]
        typ1, val1 = execute(stm["value1"], environments)
        typ2, val2 = execute(stm["value2"], environments)
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
        typ_if, val_if = execute(stm["if"], environments)
        if typ_if != "boolean":
            raise Exception("`if` can only have boolean values")
        if val_if: return execute(stm["then"], environments)
        else:      return execute(stm["else"], environments)

    if stm["type"] == "stm_id":
        id = stm['id']
        if not isInEnvironments(id, environments):
            raise Exception("value `"+id+"' not found")
        depth_id = getValueFromEnv(id, environments)['depth']
        if depth_id == -1: # must have only a value
            v = getValueFromEnv(id, environments)
            return (v['type_value'], v['value'])
        else:
            new_environments = environments[:depth_id+1]
            return execute( getValueFromEnv(id, environments)['stm']
                          , new_environments)

    if stm["type"] == "stm_let":
        new_environments = environments[:]
        new_environments.append( stm["facts"] )
        return execute(stm["stm"], new_environments)

    if stm["type"] == "stm_func_call":
        id_func = stm['id_func']

        if id_func in primitives:
            args = stm["args"]
            return execute_primitive(id_func, args, environments)

        if not isInEnvironments(id_func, environments):
            raise Exception("function `"+id_func+"' not found")

        depth_func = getValueFromEnv(id_func, environments)['depth']
        new_environments = environments[:depth_func]
        new_environment = environments[depth_func].copy()
        params = getValueFromEnv(id_func, environments)['params']
        args = stm["args"]

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
                # extracting function from environments
                tmp = getValueFromEnv(args[i]['id_func'], environments).copy()
                new_id_func = params[i]['id_func']
                # changing name of the function in the new_environment
                tmp['name'] = new_id_func
                new_environment[new_id_func] = tmp
            else: # then the argument is an statment
                new_id = params[i]['id']
                typ, val = execute(args[i], environments) # getting statement value

                new_val = {'type': 'val',
                           'name': new_id,
                           'type_value': typ,
                           'value': val,
                           'depth': -1}
                new_environment[new_id] = new_val

        new_environments.append(new_environment)
        return execute( getValueFromEnv(id_func, environments)['stm']
                      , new_environments)

    # this must never happen
    return ("error: invalid type", "")

def create_depth_in_facts(facts, depth):
    for k, fact in facts.items():
        fact['depth'] = depth
        create_depth_in_stm(fact["stm"], depth)

def create_depth_in_stm(stm, depth):
    if stm["type"] in ["stm_value", "stm_id", "stm_func_call"]:
        return
    if stm["type"] == "stm_op":
        create_depth_in_stm(stm["value1"], depth)
        create_depth_in_stm(stm["value2"], depth)
    if stm["type"] == "stm_if_then":
        create_depth_in_stm(stm["if"], depth)
        create_depth_in_stm(stm["then"], depth)
        create_depth_in_stm(stm["else"], depth)
    if stm["type"] == "stm_let":
        create_depth_in_stm(stm["stm"], depth+1)
        create_depth_in_facts(stm["facts"], depth+1)

def execute_ast(ast):
    create_depth_in_facts(ast['facts'], 0)
    create_depth_in_stm(ast['stm'], 0)
    return execute(stm=ast["stm"], environments=[ast["facts"]])

def execute_primitive(id_func, args, environments):
    if id_func == "CONS":
        if len(args) != 2:
            raise Exception("CONS has only two parameters")
        if args[0]['type'] == 'id_func' or args[1]['type'] == 'id_func':
            raise Exception("CONS do not accept functions as arguments")
        val1 = execute(args[0], environments)
        val2 = execute(args[1], environments)
        return ('cons', (val1, val2) )

    if id_func in ['CAR', 'CDR', 'Not', 'ToString']:
        if len(args) != 1:
            raise Exception(id_func+" has only one parameter")
        if args[0]['type'] == 'id_func':
            raise Exception(id_func+" do not accept functions as arguments")
        val = execute(args[0], environments)

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
