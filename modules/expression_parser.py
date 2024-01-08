import re
from typing import Dict, Union


class ExpressionParser:
    """
    Класс для анализа и разбора линейных выражений.

    Args:
        expression (str): Входное линейное выражение в формате, например, "2*x+3.6*y2+7>=5".

    Attributes:
        left (str): Левая часть выражения.
        sign (str): Знак (">=", "<=", ">", "<", "->").
        constant (Union[float, str]): Свободный член (константа) правой части выражения.
        variables (Dict[str, float]): Словарь переменных и их коэффициентов из левой части.

    """

    def __init__(self, expression: str):
        self._expression = expression

        # Получаем знак неравенства
        self._sign = self._get_sign()

        # Делим на левую и правую часть
        self._left, self._right = self._expression.split(self._sign)

        # Получаем все переменные и их коэффициенты из левой части
        self._variables = self._get_variables()

        # Получаем правую часть
        self._constant = self._get_constant()

    def _get_sign(self) -> str:
        """
        Определение знака неравенства или стремления в выражении.

        Returns:
            str: Один из знаков (">=", "<=", ">", "<", "->").

        """

        if '->' in self._expression:
            return '->'
        pattern = r'[<>]=?'
        return re.search(pattern, self._expression).group(0)

    def _get_variables(self) -> Dict[str, float]:
        """
        Извлечение переменных и их коэффициентов из левой части выражения.

        Returns:
            Dict[str, float]: Словарь переменных и их коэффициентов.

        """
        variables = {}
        pattern = r'[a-zA-Z][a-zA-Z\d]*'
        variable_names = re.findall(pattern, self._left)
        for name in variable_names:
            coefficient_pattern = r'-?\d*\.?\d+'
            coefficient_match = re.search(fr'{coefficient_pattern}\*{re.escape(name)}', self._left)

            variables[name] = float(f'{coefficient_match.group(0)}'.split('*')[0]) if coefficient_match else 1.0
        return variables

    def _get_constant(self) -> Union[float, str]:
        """
        Извлечение свободного члена (константы) из правой части выражения.

        Returns:
            Union[float, str]: Свободный член (константа) или правая часть (если есть "->").

        """
        if self.sign == '->':
            return self._right.strip()

        pattern = r'-?\d*\.?\d+'
        return sum(map(float, re.findall(pattern, self._right)))

    @property
    def left(self) -> str:
        return self._left

    @property
    def sign(self) -> str:
        return self._sign

    @property
    def constant(self) -> Union[float, str]:
        return self._constant

    @property
    def variables(self) -> Dict[str, float]:
        return self._variables.copy()


# Пример использования:
if __name__ == "__main__":
    target_expression = input('Введите целевую функцию: ')
    target_parser = ExpressionParser(target_expression)
    print(f'\n{target_parser.constant = }\n{target_parser.sign = }\n{target_parser.variables = }\n')

    num_constraints = int(input('Введите количество ограничений: '))

    constraint_parsers = []
    for i in range(num_constraints):
        constraint = input(f'Введите ограничение {i + 1}: ')
        constraint_parser = ExpressionParser(constraint)
        constraint_parsers.append(constraint_parser)
        print(f'\n{constraint_parser.constant = }\n{constraint_parser.sign = }\n{constraint_parser.variables = }\n')
