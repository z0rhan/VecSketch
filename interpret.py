import math
import shapely as sh

import vecsketch_lib as vlib


def is_shape(value):
    return isinstance(value, sh.Geometry)


def num_cmp(left, op, right):
    if op == "=":
        return 1 if left == right else 0
    if op == "/=":
        return 1 if left != right else 0
    if op == "<":
        return 1 if left < right else 0
    raise RuntimeError(f"unsupported comparison {op!r} for numbers")


def shape_cmp(left, op, right):
    if op == "=":
        return 1 if vlib.shape_equals(left, right) else 0
    if op == "/=":
        return 0 if vlib.shape_equals(left, right) else 1
    if op == "<":
        return 1 if vlib.shape_covered_by(left, right) else 0
    raise RuntimeError(f"unsupported comparison {op!r} for shapes")


def open_window_if_not_open():
    if vlib.Conf.root is None:
        vlib.window_open()


def load_var(semdata, name):
    if semdata.scopes:
        scope = semdata.scopes[-1]
    else:
        scope = None

    if scope is not None:
        if name in scope:
            return scope[name]

    return semdata.symbol_table[name].rvalue


def store_var(semdata, name, value):
    for scope in reversed(semdata.scopes):
        if name in scope:
            scope[name] = value
            return
    semdata.symbol_table[name].rvalue = value


def push_formals(semdata, formals, arg_values):
    semdata.scopes.append(
        {formal.child_identifier.value: value for formal, value in zip(formals, arg_values)}
    )


def pop_formals(semdata):
    semdata.scopes.pop()


def eval_coordinate_list(node, semdata):
    coords = []
    for coord in node.children_coordinates:
        x = eval_node(coord.child_x, semdata)
        y = eval_node(coord.child_y, semdata)
        coords.append((x, y))
    if len(coords) == 1:
        return vlib.create_point(coords[0][0], coords[0][1])
    return vlib.create_linestring(coords)


def eval_function_call(node, semdata):
    name = node.child_identifier.value
    sym = semdata.symbol_table[name]
    args = [eval_node(a, semdata) for a in node.children_arguments]
    push_formals(semdata, sym.formals, args)
    try:
        for vd in sym.variable_definitions or []:
            eval_node(vd, semdata)
        return eval_node(sym.rvalue, semdata)
    finally:
        pop_formals(semdata)


def eval_procedure_call(node, semdata, want_return):
    name = node.child_identifier.value
    sym = semdata.symbol_table[name]
    args = [eval_node(a, semdata) for a in node.children_arguments]
    push_formals(semdata, sym.formals, args)
    try:
        for vd in sym.variable_definitions or []:
            eval_node(vd, semdata)
        for st in sym.statements:
            eval_node(st, semdata)
        if want_return:
            return eval_node(sym.return_expression, semdata)
    finally:
        pop_formals(semdata)
    return None


def is_true(value):
    return value != 0


def run_program(tree, semdata):
    for symdata in semdata.symbol_table.values():
        if symdata.symtype == "variable":
            symdata.rvalue = 0

    semdata.scopes = []

    eval_node(tree, semdata)


def eval_node(node, semdata):
    if node is None:
        return None

    symbol_table = semdata.symbol_table
    nodetype = node.nodetype

    if nodetype == "program":
        definition_node = node.child_definitions

        for var_def_node in definition_node.children_variable_definitions:
            eval_node(var_def_node, semdata)

        for stmt in node.children_statements:
            eval_node(stmt, semdata)

        return None

    elif nodetype == "variable_definition":
        identifier = node.child_identifier.value
        rvalue = node.child_rvalue
        eval_rvalue = eval_node(rvalue, semdata)
        # if the last item is a dict we are inside a function call
        # so we register to the local scope else register to global symbol_table
        if semdata.scopes and isinstance(semdata.scopes[-1], dict):
            semdata.scopes[-1][identifier] = eval_rvalue
        else:
            node.symbol_data.rvalue = eval_rvalue
        return None

    elif nodetype == "int_literal":
        return node.value

    elif nodetype == "string":
        return node.value

    elif nodetype == "identifier":
        return load_var(semdata, node.value)

    elif nodetype == "field_access":
        target = eval_node(node.child_target, semdata)
        field = node.child_field.value
        if not is_shape(target):
            raise RuntimeError("field access requires a shape value")
        if field == "x":
            return vlib.shape_xcoord(target)
        if field == "y":
            return vlib.shape_ycoord(target)
        # Not needed, could add it in the semantics to make it possible here
        # if field == "xmin":
        #     return vlib.shape_bounds(target)[0]
        # if field == "ymin":
        #     return vlib.shape_bounds(target)[1]
        # if field == "xmax":
        #     return vlib.shape_bounds(target)[2]
        # if field == "ymax":
        #     return vlib.shape_bounds(target)[3]
        raise RuntimeError(f"unknown field {field!r}")

    elif nodetype == "coordinate_list":
        return eval_coordinate_list(node, semdata)

    elif nodetype == "unary_operation":
        op = node.value
        inner = node.child_expression
        if op == "+" and inner.nodetype == "coordinate_list":
            coords = []
            for coord in inner.children_coordinates:
                x = eval_node(coord.child_x, semdata)
                y = eval_node(coord.child_y, semdata)
                coords.append((x, y))
            return vlib.create_polygon(coords)

        val = eval_node(inner, semdata)
        if op == "-":
            if is_shape(val):
                return vlib.shape_downgrade(val)
            return -val
        if op == "+":
            if is_shape(val):
                return vlib.shape_polygonize(val)
            return math.floor(val)
        raise RuntimeError(f"unsupported unary operator {op!r}")

    elif nodetype == "binary_operation":
        operation = node.value
        if operation == "->":
            left = eval_node(node.child_left, semdata)
            coord = node.child_right
            dx = eval_node(coord.child_x, semdata)
            dy = eval_node(coord.child_y, semdata)
            if not is_shape(left):
                raise RuntimeError("-> requires a shape on the left")
            return vlib.shape_move(left, dx, dy)

        left = eval_node(node.child_left, semdata)
        right = eval_node(node.child_right, semdata)

        if is_shape(left) and is_shape(right):
            if operation == "+":
                return vlib.shape_union(left, right)
            if operation == "-":
                return vlib.shape_difference(left, right)
            if operation == "*":
                return vlib.shape_intersection(left, right)
            if operation == "/":
                raise RuntimeError("invalid / between two shapes")

        if is_shape(left) and not is_shape(right):
            if operation == "*":
                return vlib.shape_scale(left, right)
            if operation == "/":
                return vlib.shape_rotate(left, right)
            raise RuntimeError(f"invalid {operation!r} between shape and number")

        if not is_shape(left) and is_shape(right):
            if operation == "*":
                return vlib.shape_scale(right, left)
            if operation in "+-/":
                raise RuntimeError(f"invalid {operation!r} between number and shape")

        if operation == "+":
            return left + right
        if operation == "-":
            return left - right
        if operation == "*":
            return left * right
        if operation == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        raise RuntimeError(f"unsupported binary operator {operation!r}")

    elif nodetype == "comparison":
        left = eval_node(node.child_left, semdata)
        right = eval_node(node.child_right, semdata)
        operation = node.value
        if is_shape(left) or is_shape(right):
            if not (is_shape(left) and is_shape(right)):
                raise RuntimeError("shape/number mix in comparison")
            return shape_cmp(left, operation, right)
        return num_cmp(left, operation, right)

    elif nodetype == "function_call":
        return eval_function_call(node, semdata)

    elif nodetype == "assignment":
        lhs = node.child_left.value
        rhs = node.child_right
        if rhs.nodetype == "procedure_call":
            val = eval_procedure_call(rhs, semdata, want_return=True)
        else:
            val = eval_node(rhs, semdata)
        store_var(semdata, lhs, val)
        return None

    elif nodetype == "print_statement":
        items = []
        for item in node.children_print_items:
            if item.nodetype == "string":
                items.append(item.value)
            else:
                v = eval_node(item, semdata)
                if is_shape(v):
                    items.append(vlib.shape_tostring(v))
                else:
                    items.append(str(v))
        print(" ".join(items))
        return None

    elif nodetype == "if_statement":
        cond = eval_node(node.child_condition, semdata)
        if is_true(cond):
            for st in node.children_then_statements:
                eval_node(st, semdata)
        else:
            for st in node.children_else_statements:
                eval_node(st, semdata)
        return None

    elif nodetype == "while_statement":
        while is_true(eval_node(node.child_condition, semdata)):
            for st in node.children_statements:
                eval_node(st, semdata)
        return None

    elif nodetype == "procedure_call":
        eval_procedure_call(node, semdata, want_return=False)
        return None

    elif nodetype == "clear_statement":
        open_window_if_not_open()
        vlib.window_clear()
        return None

    elif nodetype == "pause_statement":
        open_window_if_not_open()
        vlib.window_pause()
        return None

    elif nodetype == "wait_statement":
        open_window_if_not_open()
        secs = eval_node(node.child_expression, semdata)
        if is_shape(secs):
            raise RuntimeError("wait cannot be called with shapes")
        if not isinstance(secs, (int, float)):
            raise RuntimeError("wait called with invalide types, use with number")

        vlib.window_wait(secs)
        return None

    elif nodetype == "draw_statement":
        open_window_if_not_open()
        shape_val = eval_node(node.child_expression, semdata)
        if not is_shape(shape_val):
            raise RuntimeError("draw can only be called on shapes")
        rgb = node.child_rgb
        if rgb is None:
            vlib.window_draw(shape_val)
        else:
            r = eval_node(rgb.child_r, semdata)
            if not isinstance(r, (int, float)):
                raise RuntimeError("RGB can only be initialized with numbers")
            g = eval_node(rgb.child_g, semdata)
            if not isinstance(g, (int, float)):
                raise RuntimeError("RGB can only be initialized with numbers")
            b = eval_node(rgb.child_b, semdata)
            if not isinstance(b, (int, float)):
                raise RuntimeError("RGB can only be initialized with numbers")
            vlib.window_draw(shape_val, r, g, b)
        return None

    return None
