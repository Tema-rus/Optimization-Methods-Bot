from tabulate import tabulate
import numpy as np
from io import StringIO


def generate_simplex_report(coefficients, constants, target_coefficients, target='max'):
    output = StringIO()

    def custom_print(*args, **kwargs):
        print(*args, **kwargs, file=output)

    def is_valid_target(target):
        return target.strip().lower() in ('min', 'max')

    def get_table(target, coeffs, consts, t_coeffs):
        if target == 'min':
            t_coeffs *= -1

        count_vars = len(t_coeffs)
        count_lines = len(coeffs)

        basis = np.arange(count_vars, count_vars + count_lines)

        constraint_matrix = coeffs
        if count_vars + count_lines != len(coeffs[0]):
            identity_matrix = np.identity(count_lines)
            constraint_matrix = np.hstack((coeffs, identity_matrix))

        header_row = np.hstack([None, 0, t_coeffs, [0] * count_lines])
        table_body = np.hstack((np.transpose([basis]), np.transpose([consts]), constraint_matrix))
        table = np.vstack((header_row, table_body)).astype(float)

        return table, count_vars, count_lines

    def print_table(table, all_vars):
        headers = ['Базис', 'Константа'] + all_vars
        formatted_table = [
            [f'{int(col) if col == int(col) else col:.2f}' if not np.isnan(col) else '' for col in row]
            for row in table
        ]
        tabulated_table = tabulate(formatted_table, headers=headers, tablefmt='pipe', stralign='center')
        custom_print(tabulated_table, end='\n\n')

    def simplex_method(coefficients, constants, target_coefficients, target='max'):
        if is_valid_target(target):
            target = target.strip().lower()

        if target == 'min':
            target_coefficients *= -1

        table, count_vars, count_lines = get_table(target, coefficients, constants, target_coefficients)
        all_variables = [f'x{i}' for i in range(count_vars)] + [f's{i}' for i in range(count_vars, count_lines + count_vars)]

        i = 0
        while True:
            i += 1
            custom_print(f'№{i}:')
            print_table(table, all_variables)

            optimal_values = table[0, 2:]
            if (target == 'max' and np.all(optimal_values <= 0)) or (target == 'min' and np.all(optimal_values >= 0)):
                break

            col = np.argmax(optimal_values) + 2 if target == 'max' else np.argmin(optimal_values) + 2
            ratios = table[1:, 1] / table[1:, col]
            ratios[~np.isfinite(ratios)] = np.inf
            row = np.argmin(ratios) + 1
            pivot = table[row, col]

            custom_print(f'Разрешающий столбец: {col}, Разрешающая строка: {row}, Разрешающий элемент: {pivot:.2f}\n')

            table[row, 1:] /= pivot

            for j in range(len(table)):
                if j != row:
                    mult = table[j, col] / table[row, col]
                    table[j, 1:] -= mult * table[row, 1:]

            table[row, 0] = col - 2

        custom_print('Ответ:')
        x = np.zeros(len(target_coefficients), dtype=float)
        for key in range(1, len(table)):
            if table[key, 0] < len(target_coefficients):
                x[int(table[key, 0])] = table[key, 1]
        opt_value = -1 * table[0, 1]
        custom_print(f'Оптимальное значение: {opt_value}')
        custom_print(f'Коэффициенты: {", ".join([f"{el:.2f}" for el in x])}')
        return opt_value

    simplex_method(coefficients, constants, target_coefficients, target='max')

    return output.getvalue()


def main():
    a = np.array([[4, 7, 9],
                  [1, 4, 5],
                  [9, 0, 3]])
    b = np.array([4, 7, 2])
    c = np.array([3, 3, 3])

    report = generate_simplex_report(a, b, c, target='max')
    return report


if __name__ == '__main__':
    main()
