#!/usr/bin/env python3

# Шаблон для домашнѣго задания
# Рѣализуйте мѣтоды с raise NotImplementedError


class Scope:

    def __init__(self, parent=None):
        self.parent = parent
        self.d = {}

    def __getitem__(self, name):
        if name in self.d:
            return self.d[name]
        return self.parent[name]

    def __setitem__(self, name, val):
        self.d[name] = val


class Number:

    """Number - представляет число в программе.
    Все числа в нашем языке целые."""

    def __init__(self, value):
        self.value = int(value)

    def evaluate(self, scope):
        return self


class Function:

    """Function - представляет функцию в программе.
    Функция - второй тип поддерживаемый языком.
    Функции можно передавать в другие функции,
    и возвращать из функций.
    Функция состоит из тела и списка имен аргументов.
    Тело функции это список выражений,
    т. е.  у каждого из них есть метод evaluate.
    Во время вычисления функции (метод evaluate),
    все объекты тела функции вычисляются последовательно,
    и результат вычисления последнего из них
    является результатом вычисления функции.
    Список имен аргументов - список имен
    формальных параметров функции."""

    def __init__(self, args, body):
        self.args = args
        self.body = body

    def evaluate(self, scope):
        s = None
        for operation in self.body:
            s = operation.evaluate(scope)
        return s


class FunctionDefinition:

    """FunctionDefinition - представляет определение функции,
    т. е. связывает некоторое имя с объектом Function.
    Результатом вычисления FunctionDefinition является
    обновление текущего Scope - в него
    добавляется новое значение типа Function."""

    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope):
        scope[self.name] = self.function
        return self.function


class Conditional:

    """
    Conditional - представляет ветвление в программе, т. е. if.
    """

    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

    def evaluate(self, scope):
        if self.condition.evaluate(scope).value != 0:
            s = None
            for operation in self.if_true:
                if operation != None:
                    s = operation.evaluate(scope)
            return s
        else:
            s = None
            for operation in self.if_false:
                if operation != None:
                    s = operation.evaluate(scope)
            return s


class Print:

    """Print - печатает значение выражения на отдельной строке."""

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope):
        val = self.expr.evaluate(scope)
        print(val.value)
        return val


class Read:

    """Read - читает число из стандартного потока ввода
     и обновляет текущий Scope.
     Каждое входное число располагается на отдельной строке
     (никаких пустых строк и лишних символов не будет).
     """

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        num = Number(int(input()))
        scope[self.name] = num
        return scope[self.name]


class FunctionCall:

    """
    FunctionCall - представляет вызов функции в программе.
    В результате вызова функции должен создаваться новый объект Scope,
    являющий дочерним для текущего Scope
    (т. е. текущий Scope должен стать для него родителем).
    Новый Scope станет текущим Scope-ом при вычислении тела функции.
    """

    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args

    def evaluate(self, scope):
        call_scope = Scope(scope)
        function = self.fun_expr.evaluate(call_scope)
        for arg, val in zip(function.args, self.args):
            call_scope[arg] = val.evaluate(scope)
        return function.evaluate(call_scope)


class Reference:

    """Reference - получение объекта
    (функции или переменной) по его имени."""

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]


class BinaryOperation:

    """BinaryOperation - представляет бинарную операцию над двумя выражениями.
    Результатом вычисления бинарной операции является объект Number.
    Поддерживаемые операции:
    “+”, “-”, “*”, “/”, “%”, “==”, “!=”,
    “<”, “>”, “<=”, “>=”, “&&”, “||”."""
    binary_ops = {'+': lambda a, b: a + b,
                  '-': lambda a, b: a - b,
                  '*': lambda a, b: a * b,
                  '/': lambda a, b: a // b,
                  '%': lambda a, b: a % b,
                  '==': lambda a, b: a == b,
                  '!=': lambda a, b: a != b,
                  '<': lambda a, b: a < b,
                  '>': lambda a, b: a > b,
                  '<=': lambda a, b: a <= b,
                  '>=': lambda a, b: a >= b,
                  '&&': lambda a, b: a and b,
                  '||': lambda a, b: a or b}

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self, scope):
        lhs = self.lhs.evaluate(scope).value
        rhs = self.rhs.evaluate(scope).value
        return Number(self.binary_ops[self.op](lhs, rhs))


class UnaryOperation:

    """UnaryOperation - представляет унарную операцию над выражением.
    Результатом вычисления унарной операции является объект Number.
    Поддерживаемые операции: “-”, “!”."""

    unary_ops = {'-': lambda a: -a,
                 '!': lambda a: not a}

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope):
        arg = self.expr.evaluate(scope).value
        return Number(self.unary_ops[self.op](arg))


def example():
    parent = Scope()
    parent['foo'] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent['bar'] = Number(10)
    scope = Scope(parent)
    assert 10 == scope['bar'].value
    scope['bar'] = Number(20)
    assert scope['bar'].value == 20
    print("It should print 2: ", end=' ')
    FunctionCall(FunctionDefinition('foo', parent['foo']),
                 [Number(5), UnaryOperation('-', Number(3))]).evaluate(scope)
    print()


def test_mult_and_print():
    scope = Scope()
    mult = BinaryOperation(Number(5), '*', Number(2))
    print("Проверяем сложение и Print")
    print("сейчас должно будет вывестись 10 два раза,")
    print("так как вызывается Print от Print")
    Print(Print(mult)).evaluate(scope)
    print("Мы проверили Number, '*' и странный вызов Print,")
    print("нормальный Print будет часто использоваться далее")
    print()


def test_var_minus_and_read():
    scope = Scope()
    print("Введите a")
    Read('a').evaluate(scope)
    print("Должно получиться -a-1")
    Print(BinaryOperation(
                 UnaryOperation('-',Number(1)),
                 '-',
                 Reference('a')
                         )
          ).evaluate(scope)
    print("Мы проверили Read, Reference,")
    print("унарный '-', а также нормальный Print")
    print("и бинарный '-'")
    print()


def test_if():
    scope = Scope()
    print("Введите s")
    Read('s').evaluate(scope)
    print("Если s>=2, то выводится 1, иначе 0")
    Conditional(BinaryOperation(
                   Number(2),
                   '<=',
                   Reference('s')
                                ), [Print(Number(1))],
                                   [Print(Number(0))]
                ).evaluate(scope)
    print()


def test_logical_ops():
    scope = Scope()
    assert 1 == BinaryOperation(Number(1),
                                '<',
                                Number(2)
                                ).evaluate(scope).value
    assert 0 == BinaryOperation(Number(1),
                                '>=',
                                Number(2)
                                ).evaluate(scope).value
    assert 1 == BinaryOperation(Number(2),
                                '<=',
                                Number(2)
                                ).evaluate(scope).value
    assert 0 == BinaryOperation(Number(1),
                                '>',
                                Number(2)
                                ).evaluate(scope).value
    assert 1 == BinaryOperation(Number(4),
                                '<',
                                Number(6)
                                ).evaluate(scope).value
    assert 1 == BinaryOperation(Number(5),
                                '!=',
                                Number(2)
                                ).evaluate(scope).value
    assert 0 == BinaryOperation(Number(1),
                                '==',
                                Number(2)
                                ).evaluate(scope).value
    assert 0 == BinaryOperation(Number(8),
                                '&&',
                                Number(0)
                                ).evaluate(scope).value
    assert 0 != BinaryOperation(Number(-5),
                                '||',
                                Number(0)
                                ).evaluate(scope).value
    assert 1 == UnaryOperation('!',
                               Number(0)
                               ).evaluate(scope).value
    assert 0 == UnaryOperation('!',
                               Number(-5)
                               ).evaluate(scope).value
    print("Мы только что проверили все логические операции при помощи assert")
    print("Если программа не упала, то они правильно работают")
    print()


def test_scope():
    scope = Scope()
    print("Введите число, которое будет называться n")
    Read('n').evaluate(scope)
    print("А теперь введите ненулевое k")
    Read('k').evaluate(scope)
    print("Сейчас снова потребуется ввести n,")
    print("для проверки лучше, если оно на несколько порядков отличается")
    print("от первого n или другого с ним знака")
    FunctionCall(FunctionDefinition('foo',
                                    Function([], [
                                        Read('n'),
                                        Print(BinaryOperation(
                                                 Reference('n'),
                                                 '/',
                                                 Reference('k')
                                                              )
                                              )
                                                  ]
                                             )
                                    ), [],
                 ).evaluate(scope)
    print("Должно было получиться частное второго n и k")
    print("А теперь выведем первое n,")
    print("чтобы проверить, что с ним всё в порядке")
    Print(Reference('n')).evaluate(scope)
    print("Вывод: scope отлично работает,")
    print("значение переменных сначала ищутся в call_scope,")
    print("а потом в родительском scope")
    print("Ещё мы проверили '/' и вызов функции без аргументов")
    print()


def test_empty_func_and_conditional():
    scope = Scope()
    print("Посмотрим, что возвращает пустая функция")
    print("и пустые ветки conditional")
    res = FunctionCall(FunctionDefinition('foo',
                                           Function(['x'], [])
                                          ),
                        [Number(5)]
                       ).evaluate(scope)
    print(res)
    res=Conditional(BinaryOperation(
                       Number(2),
                       '<=',
                       Number(6)
                                   ),
                    [],
                    []
                    ).evaluate(scope)
    print(res)
    res=Conditional(BinaryOperation(
                       Number(2),
                       '<=',
                       Number(0)
                                    ),
                    [],
                    []
                   ).evaluate(scope)
    print(res)
    res=Conditional(BinaryOperation(
                       Number(2),
                       '<=',
                       Number(6)
                                   ),
                    [None],
                    [None]
                    ).evaluate(scope)
    print(res)
    res=Conditional(BinaryOperation(
                       Number(2),
                       '<=',
                       Number(0)
                                    ),
                    [None],
                    [None]
                   ).evaluate(scope)
    print(res)
    print("Они возвращает то, что должны")
    print()


def test_func_in_func():
    scope = Scope()
    print ("Введите по очереди два числа")
    FunctionDefinition('foo',
                       Function([], [
                           FunctionDefinition('bar', Function([], [
                               Read('a'),
                               Read('b'),
                               BinaryOperation(
                                  Reference('a'),
                                  '%',
                                  Reference('b'))
                           ]))
                       ])
                       ).evaluate(scope)
    Print(FunctionCall(FunctionCall(Reference('foo'), []), [])).evaluate(scope)
    print("Функция foo вернула функцию bar,")
    print("которая считала два числа и посчитала остаток первого")
    print("по модулю второго")
    print()


if __name__ == '__main__':
    example()
    print("В примере проверился вызов функции от аргументов")
    print("а также операция '+'")
    test_mult_and_print()
    test_var_minus_and_read()
    test_logical_ops()
    test_scope()
    print("Проверим Conditional")
    test_if()
    print("Одна ветка Conditional точно проверена")
    print("Теперь повторите всё снова, чтобы проверялась вторая")
    test_if()
    test_empty_func_and_conditional()
    test_func_in_func()
    print("Это всё. Спасибо за внимание!")
