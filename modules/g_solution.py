import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects


def target_function(obj_x1, obj_x2):
    plt.arrow(x=0, y=0, dx=obj_x1 - 0.25, dy=obj_x2 - 0.25, width=.01, color='black', label='Нормаль вектор')


def function_constraints(x1, x2, constraint_parser, const_max, const_min, variables_max_1, variables_min_1,
                         variables_max_2, variables_min_2, i, num_constraints):
    x1_now = list()
    x2_now = list()
    if constraint_parser.constant == 0:
        for x_1 in np.linspace(0, constraint_parser.constant + 100):
            for x_2 in np.linspace(0, constraint_parser.constant + 100):
                if constraint_parser.variables['x1'] * x_1 + constraint_parser.variables['x2'] * x_2 == constraint_parser.constant:
                    x1.append(x_1)
                    x2.append(x_2)
                    x1_now.append(x_1)
                    x2_now.append(x_2)
    else:
        for x_1 in np.linspace(0, abs(constraint_parser.constant)):
            for x_2 in np.linspace(0, abs(constraint_parser.constant)):
                if constraint_parser.variables['x1'] * x_1 + constraint_parser.variables['x2'] * x_2 == constraint_parser.constant:
                    x1.append(x_1)
                    x2.append(x_2)
                    x1_now.append(x_1)
                    x2_now.append(x_2)
    if constraint_parser.sign == '<=':
        plt.errorbar(x1_now, x2_now, path_effects=[patheffects.withTickedStroke(spacing=7, angle=-135)],
                     label=f'Ограничение {i + 1}')
        const_min.append(constraint_parser.constant)
        variables_min_1.append(constraint_parser.variables['x1'])
        variables_min_2.append(constraint_parser.variables['x2'])
    if constraint_parser.sign == '>=':
        plt.errorbar(x1_now, x2_now, path_effects=[patheffects.withTickedStroke(spacing=7, angle=135)],
                     label=f'Ограничение {i + 1}')
        const_max.append(constraint_parser.constant)
        variables_max_1.append(constraint_parser.variables['x1'])
        variables_max_2.append(constraint_parser.variables['x2'])
    if constraint_parser.sign == '=':
        plt.plot(x1_now, x2_now, label=f'Ограничение {i + 1}')

    return x1, x2, const_max, const_min, variables_max_1, variables_min_1, variables_max_2, variables_min_2, num_constraints


def find_maximum(obj_x1, obj_x2, x1, x2, const_max, const_min, variables_max_1, variables_min_1, variables_max_2,
                 variables_min_2, num_constraints, target_parser, path_to_save='graph.png'):
    maxima = list()
    x1_otbor = list()
    x2_otbor = list()
    for l in range(int(max(const_min))):
        x1.append(l)
        x2.append(0)
    for l in range(int(max(const_min))):
        x1.append(0)
        x2.append(l)

    for i in range(num_constraints):
        const_max.append(0)
        const_min.append(0)
        variables_max_2.append(0)
        variables_max_1.append(0)
        variables_min_1.append(0)
        variables_min_2.append(0)
    for j in range(num_constraints):
        if len(x1_otbor) == 0:
            for g in range(len(x1)):
                if variables_min_1[j] * x1[g] + variables_min_2[j] * x2[g] <= const_min[j] and variables_max_1[j] * x1[g] + variables_max_2[j] * x2[g] >= const_max[j]:
                    x1_otbor.append(x1[g])
                    x2_otbor.append(x2[g])
        x1 = list()
        x2 = list()
        if len(x1) == 0:
            for g in range(len(x1_otbor)):
                if variables_min_1[j] * x1_otbor[g] + variables_min_2[j] * x2_otbor[g] <= const_min[j] and \
                        variables_max_1[j] * x1_otbor[g] + variables_max_2[j] * x2_otbor[g] >= const_max[j]:
                    x1.append(x1_otbor[g])
                    x2.append(x2_otbor[g])
        x1_otbor = list()
        x2_otbor = list()

    if target_parser.constant == 'max':
        if len(x1) == 0:
            for h in range(len(x1_otbor)):
                maxim = obj_x1 * x1_otbor[h] + obj_x2 * x2_otbor[h]
                maxima.append(maxim)
            for k in range(len(maxima)):
                if max(maxima) == maxima[k]:
                    plt.plot(x1_otbor[k], x2_otbor[k], 'o', label=f'max = {max(maxima)}')
        if len(x1_otbor) == 0:
            for h in range(len(x1)):
                maxim = obj_x1 * x1[h] + obj_x2 * x2[h]
                maxima.append(maxim)
            for k in range(len(maxima)):
                if max(maxima) == maxima[k]:
                    plt.plot(x1[k], x2[k], 'o', label=f'max = {max(maxima)}')

    if target_parser.constant == 'min':
        if len(x1) == 0:
            for h in range(len(x1_otbor)):
                maxim = obj_x1 * x1_otbor[h] + obj_x2 * x2_otbor[h]
                maxima.append(maxim)
            for k in range(len(maxima)):
                if min(maxima) == maxima[k]:
                    plt.plot(x1_otbor[k], x2_otbor[k], 'o', label=f'min = {min(maxima)}')
        if len(x1_otbor) == 0:
            for h in range(len(x1)):
                maxim = obj_x1 * x1[h] + obj_x2 * x2[h]
                maxima.append(maxim)
            for k in range(len(maxima)):
                if min(maxima) == maxima[k]:
                    plt.plot(x1[k], x2[k], 'o', label=f'min = {min(maxima)}')
    ox = list()
    oy = list()
    if max(const_min) >= max(const_max):
        for f in range(0, int(max(const_min)) + 1):
            ox.append(0)
            oy.append(f)
        for f in range(0, int(max(const_min)) + 1):
            ox.append(f)
            oy.append(0)
    else:
        for f in range(0, int(max(const_max)) + 1):
            ox.append(0)
            oy.append(f)
        for f in range(0, int(max(const_max)) + 1):
            ox.append(f)
            oy.append(0)
    plt.plot(ox, oy, color='black')
    plt.legend()
    plt.savefig(path_to_save)
    plt.figure()
