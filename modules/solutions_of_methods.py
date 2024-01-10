from typing import Dict, List
import os

import numpy as np

from modules.expression_parser import ExpressionParser
from modules.g_solution import target_function, function_constraints, find_maximum
from modules.s_solution import generate_simplex_report


def simplex(target: str, constraints: List[str], _) -> str:
    a = []
    b = []
    for constraint in constraints:
        constraint_parser = ExpressionParser(constraint)
        a.append(list(constraint_parser.variables.values()))
        b.append(constraint_parser.constant)

    a = np.array(a)
    b = np.array(b)

    target_func = ExpressionParser(target)
    c = np.array(list(target_func.variables.values()))

    report = generate_simplex_report(a, b, c, target_func.constant)
    return report


def graphic(target_expression: str, constraints: List[str], user_id: int) -> str:
    x1 = []
    x2 = []
    const_min = []
    const_max = []
    variables_max_1 = []
    variables_min_1 = []
    variables_max_2 = []
    variables_min_2 = []

    target_parser = ExpressionParser(target_expression)

    obj_x1 = target_parser.variables['x1']
    obj_x2 = target_parser.variables['x2']

    target_function(obj_x1, obj_x2)

    num_constraints = len(constraints)
    for i in range(num_constraints):
        constraint = constraints[i]
        constraint_parser = ExpressionParser(constraint)

        function_constraints(x1, x2, constraint_parser, const_max, const_min, variables_max_1, variables_min_1,
                             variables_max_2, variables_min_2, i, num_constraints)

    folder = 'img'
    if not os.path.isdir(folder):
        os.mkdir(folder)

    png = f'{folder}/{user_id}.png'


    find_maximum(obj_x1, obj_x2, x1, x2, const_max, const_min, variables_max_1, variables_min_1, variables_max_2,
                 variables_min_2, num_constraints, target_parser, path_to_save=png)

    return png
