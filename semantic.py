from utils import SemData, SymbolData


def push_scope(semdata, formals):
    scope_items = []

    for formal in formals:
        scope_items.append(formal.child_identifier.value)

    semdata.scopes.append(scope_items)


def pop_scope(semdata):
    semdata.scopes.pop()


def register_functions(node, semdata):
    if node.nodetype == "function_definition":
        identifier = node.child_identifier.value
        if identifier in semdata.symbol_table:
            defined_lineno = semdata.symbol_table[identifier].lineno
            return f"Redefinition of function <{identifier}>\n\
                     Hint: defined at line {defined_lineno}"

        formals = node.children_formals
        variable_definitions = node.children_variable_definitions
        rvalue = node.child_rvalue

        symbol_data = SymbolData("function", node)
        symbol_data.lineno = node.lineno
        symbol_data.formals = formals
        symbol_data.return_type = node.child_return_type
        symbol_data.variable_definitions = variable_definitions
        symbol_data.rvalue = rvalue

        semdata.symbol_table[identifier] = symbol_data
        node.symbol_data = symbol_data


def register_procedures(node, semdata):
    if node.nodetype == "procedure_definition":
        identifier = node.child_identifier.value
        if identifier in semdata.symbol_table:
            defined_lineno = semdata.symbol_table[identifier].lineno
            return f"Redefinition of procedure <{identifier}>\n\
                     Hint: defined at line {defined_lineno}"

        statement_list = node.children_statements
        formals = node.children_formals
        variable_definitions = node.children_variable_definitions

        symbol_data = SymbolData("procedure", node)
        symbol_data.lineno = node.lineno
        symbol_data.formals = formals
        symbol_data.variable_definitions = variable_definitions
        symbol_data.statements = statement_list
        symbol_data.return_expression = node.child_return_expression

        semdata.symbol_table[identifier] = symbol_data
        node.symbol_data = symbol_data


def register_variable(node, semdata):
    if node.nodetype == "variable_definition":
        identifier = node.child_identifier.value

        if identifier in semdata.symbol_table:
            return f"Redefinition of variable <{identifier}>"

        variable_type = node.child_type.value
        rvalue = node.child_rvalue
        if rvalue.nodetype == "identifier":
            rval_identifier = rvalue.value
            if rval_identifier not in semdata.symbol_table:
                return f"Undefined variable <{rval_identifier}>"

        symbol_data = SymbolData("variable", node)
        symbol_data.lineno = node.lineno
        symbol_data.type = variable_type
        symbol_data.rvalue = rvalue

        semdata.symbol_table[identifier] = symbol_data
        node.symbol_data = symbol_data

    return None


def register_variable_local(node, semdata):
    if node.nodetype == "variable_definition":
        identifier = node.child_identifier.value

        if identifier in semdata.scopes[-1]:
            return f"Redefinition of variable <{identifier}>"

        rvalue = node.child_rvalue
        if rvalue.nodetype == "identifier":
            rval_identifier = rvalue.value
            if rval_identifier not in semdata.symbol_table and rval_identifier not in semdata.scopes[-1]:
                return f"Undefined variable <{rval_identifier}>"

        semdata.scopes[-1].append(identifier)

    return None


def program(node, semdata):
    if node.nodetype == "program":
        # Empty scope
        # Needed for global variables definitions
        # Though the scope is only for storing formal args
        push_scope(semdata, [])
        variable_definitions = node.child_definitions.children_variable_definitions

        for var_def in variable_definitions:
            result = register_variable(var_def, semdata)
            if result is not None:
                return result


def program_after(node, semdata):
    if node.nodetype == "program":
        # This had to be checked here since the symbol_table is not populated yet in program()
        statement_list = node.children_statements

        for statement in statement_list:
            if statement.nodetype == "procedure_call":
                identifier = statement.child_identifier.value
                return_expression = semdata.symbol_table[identifier].return_expression
                if return_expression is not None:
                    return f"Procedure <{identifier}> has return expression\n\
                             Procedure with return expression must be assigned"


def variable_definition(node, semdata):
    if node.nodetype == "variable_definition":

        variable_type = node.child_type.value
        if variable_type not in ["number", "shape"]:
            return f"Unknown type <{variable_type}> |\n\
                     Hint: allowed types -> <number> or <shape>"

        rvalue = node.child_rvalue
        if rvalue.nodetype == "function_call":
            func_identifier = rvalue.child_identifier.value
            if func_identifier not in semdata.symbol_table:
                return f"Call to Undefined function <{func_identifier}>"
        elif rvalue.nodetype == "procedure_call":
            proc_identifier = rvalue.child_identifier.value
            if proc_identifier not in semdata.symbol_table:
                return f"Call to Undefined procedure <{proc_identifier}>"


def function_definition(node, semdata):
    if node.nodetype == "function_definition":
        identifier = node.child_identifier.value

        formals = node.children_formals
        is_duplicate, duplicate_formal = is_duplicate_formal(formals)
        if is_duplicate:
            return f"Redefinition of formal arg <{duplicate_formal}>"

        is_type_okay, not_ok_type = is_formal_type_okay(formals)
        if not is_type_okay:
            return f"Unknown type <{not_ok_type}> |\n\
                     Hint: allowed types -> <number> or <shape>"

        push_scope(semdata, formals)

        return_type = node.child_return_type.value
        if return_type not in ["number", "shape"]:
            return f"Unknown type <{return_type}> |\n\
                     Hint: allowed types -> <number> or <shape>"

        rvalue = node.child_rvalue
        if check_direct_recursion(rvalue, identifier):
            return f"Direct recursion dectected for function <{identifier}>"

        variable_definitions = node.children_variable_definitions
        if variable_definitions is not None:
            for var_def in variable_definitions:
                result = register_variable_local(var_def, semdata)
                if result is not None:
                    return result


def check_direct_recursion(node, function_name):
    if node is None:
        return False
    if node.nodetype == "function_call":
        if node.child_identifier.value == function_name:
            return True
        return any(check_direct_recursion(arg, function_name) for arg in node.children_arguments)
    if node.nodetype == "binary_operation":
        return check_direct_recursion(node.child_left, function_name) or\
               check_direct_recursion(node.child_right, function_name)
    if node.nodetype == "unary_operation":
        return check_direct_recursion(node.child_expression, function_name)
    if node.nodetype == "comparison":
        return check_direct_recursion(node.child_left, function_name) or\
               check_direct_recursion(node.child_right, function_name)

    return False


def is_duplicate_formal(formals):
    seen = set()
    for formal in formals:
        identifier = formal.child_identifier.value
        if identifier in seen:
            return True, identifier
        else:
            seen.add(identifier)

    return False, None


def is_formal_type_okay(formals):
    for formal in formals:
        formal_type = formal.child_type.value
        if formal_type not in ["number", "shape"]:
            return False, formal_type

    return True, None


def function_definition_after(node, semdata):
    if node.nodetype == "function_definition":
        pop_scope(semdata)


def procedure_definition(node, semdata):
    if node.nodetype == "procedure_definition":
        identifier = node.child_identifier.value

        statement_list = node.children_statements
        for statement in statement_list:
            if statement.nodetype == "procedure_call":
                identifier = statement.child_identifier
                return_expression = statement.child_return_expression
                if return_expression is not None:
                    return f"Procedure <{identifier}> has return expression\n\
                             Procedure with return expression must be assigned"

        formals = node.children_formals
        is_duplicate, duplicate_formal = is_duplicate_formal(formals)
        if is_duplicate:
            return f"Redefinition of formal arg <{duplicate_formal}>"

        is_type_okay, not_ok_type = is_formal_type_okay(formals)
        if not is_type_okay:
            return f"Unknown type <{not_ok_type}> |\n\
                     Hint: allowed types -> <number> or <shape>"

        push_scope(semdata, formals)

        variable_definitions = node.children_variable_definitions
        if variable_definitions is not None:
            for var_def in variable_definitions:
                register_variable_local(var_def, semdata)


def procedure_definition_after(node, semdata):
    if node.nodetype == "procedure_definition":
        pop_scope(semdata)


def assignment(node, semdata):
    if node.nodetype == "assignment":
        lvalue = node.child_left.value
        if lvalue not in semdata.symbol_table and lvalue not in semdata.scopes[-1]:
            return f"Assignment to Undefined variable <{lvalue}>"
        # Check for variable scope
        if lvalue not in semdata.scopes[-1] and lvalue not in semdata.symbol_table:
            return f"Variable <{lvalue}> not in scope"

        rvalue = node.child_right
        if rvalue.nodetype == "procedure_call":
            identifier = rvalue.child_identifier.value
            if identifier not in semdata.symbol_table:
                return f"Call to Undefined procedure <{identifier}>"

            return_expression = semdata.symbol_table[identifier].return_expression
            if return_expression is None:
                return f"Procedure <{identifier}> has no return expression\n\
                         Procedure without return expression cannot be used as rvalue"

        elif rvalue.nodetype == "identifier":
            identifier = rvalue.value
            # This is when expression : atom : IDENT
            if identifier not in semdata.symbol_table and identifier not in semdata.scopes[-1]:
                return f"Call to Undefined variable <{identifier}>"

            if identifier not in semdata.scopes[-1] and identifier not in semdata.symbol_table:
                return f"Variable <{identifier}> not in scope"

        symbol_data = SymbolData("assignment", node)
        symbol_data.lvalue = lvalue
        symbol_data.rvalue = rvalue

        node.symbol_data = symbol_data


def check_field_access(node, semdata):
    if node.nodetype == "field_access":
        target_name = node.child_target.value
        if target_name not in semdata.symbol_table and target_name not in semdata.scopes[-1]:
            return f"Undefined variable <{target_name}>"
        if target_name not in semdata.scopes[-1] and target_name not in semdata.symbol_table:
            return f"Variable <{target_name}> not in scope"

        field_name = node.child_field.value
        if field_name not in ["x", "y"]:
            return f"Undefined field <{field_name}>"


def if_statement_check(node, semdata):
    if node.nodetype == "if_statement":
        condition = node.child_condition
        # Can be binary_operation if expression is just simple_expr
        if condition.nodetype != "comparison":
            return "Invalid condition expression: Must be a comparison\n\
                    Hint: supported comparisons [=, /=, <]"

        then_statement_list = node.children_then_statements
        for statement in then_statement_list:
            if statement.nodetype == "procedure_call":
                identifier = statement.child_identifier
                return_expression = statement.child_return_expression
                if return_expression is not None:
                    return f"Procedure <{identifier}> has return expression\n\
                             Procedure with return expression must be assigned"

        else_statement_list = node.children_else_statements
        for statement in else_statement_list:
            if statement.nodetype == "procedure_call":
                identifier = statement.child_identifier
                return_expression = statement.child_return_expression
                if return_expression is not None:
                    return f"Procedure <{identifier}> has return expression\n\
                             Procedure with return expression must be assigned"

        # Technically, this should not happen, better to put this in test
        if condition.value not in ["=", "/=", "<"]:
            comparison = condition.value
            return f"Invalid comparison {comparison}"


def while_statement_check(node, semdata):
    if node.nodetype == "while_statement":
        condition = node.child_condition
        if condition.nodetype != "comparison":
            return "Invalid condition expression: Must be a comparison\n\
                    Hint: supported comparisons [=, /=, <]"

        statement_list = node.children_statements
        for statement in statement_list:
            if statement.nodetype == "procedure_call":
                identifier = statement.child_identifier
                return_expression = statement.child_return_expression
                if return_expression is not None:
                    return f"Procedure <{identifier}> has return expression\n\
                             Procedure with return expression must be assigned"


def print_statement_check(node, semdata):
    if node.nodetype == "print_statement":
        print_items = node.children_print_items
        for print_item in print_items:
            if print_item.nodetype != "identifier":
                continue

            identifier = print_item.value
            if identifier not in semdata.scopes[-1] and identifier not in semdata.symbol_table:
                return f"Variable <{identifier}> not in scope"


def function_call_check(node, semdata):
    if node.nodetype == "function_call":
        identifier = node.child_identifier.value
        if identifier not in semdata.symbol_table:
            return f"Call to Undefined function <{identifier}>"

        num_of_arguments = len(node.children_arguments)
        required_num_of_args = len(semdata.symbol_table[identifier].formals)
        if num_of_arguments != required_num_of_args:
            return f"\nRequired number of arguments: <{required_num_of_args}>\n\
                     Found <{num_of_arguments}> arguments instead"


def procedure_call_check(node, semdata):
    if node.nodetype == "procedure_call":
        identifier = node.child_identifier.value
        if identifier not in semdata.symbol_table:
            return f"Call to Undefined procedure <{identifier}>"

        arguments = node.children_arguments
        formal_args = semdata.symbol_table[identifier].formals
        num_of_arguments = len(arguments)
        required_num_of_args = len(formal_args)
        if num_of_arguments != required_num_of_args:
            return f"\nRequired number of arguments: <{required_num_of_args}>\n\
                     Found <{num_of_arguments}> arguments instead"


# Entrypoints for semantic checks
def populate_symbol_table(node, semdata):
    for func in (
        register_functions,
        register_procedures
    ):
        err = func(node, semdata)
        if err is not None:
            return err

    return None


def semantic_before(node, semdata):
    for func in (
        program,
        variable_definition,
        function_definition,
        procedure_definition,
        assignment,
        check_field_access,
        print_statement_check,
        if_statement_check,
        while_statement_check,
        function_call_check,
        procedure_call_check,
    ):
        err = func(node, semdata)
        if err is not None:
            return err

    return None


def semantic_after(node, semdata):
    for func in (
        program_after,
        function_definition_after,
        procedure_definition_after
    ):
        err = func(node, semdata)
        if err is not None:
            return err

    return None


def init_semdata():
    semdata = SemData()
    semdata.symbol_table = {}
    semdata.scopes = []
    semdata.call_stack = []

    return semdata
