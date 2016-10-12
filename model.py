#!/usr/bin/env python3

# Шаблон для домашнѣго задания
# Рѣализуйте мѣтоды с raise NotImplementedError


class Scope:

    def __init__(self, parent=None):
        self.parent = parent
        d = {}
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
        self.value = value

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
        if self.condition.evaluate(scope).value:
            return self.if_true.evaluate(scope)
        else:
            return self.if_false.evaluate(scope)


class Print:

    """Print - печатает значение выражения на отдельной строке."""

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope):
        print (self.expr.evaluate(scope).value)
        return self.expr.evaluate(scope)


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
        s = Scope(scope)
        function = self.fun_expr.evaluate(s)
        for arg, val in list(zip(function.args, self.args)):
            s[arg] = val.evaluate(scope)
        return function.evaluate(s)


class Reference:

    """Reference - получение объекта
    (функции или переменной) по его имени."""

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]


binary_ops = {'+': lambda a, b: a + b,
              '-': lambda a, b: a - b,
              '*': lambda a, b: a * b,
              '/': lambda a, b: a / b,
              '%': lambda a, b: a % b,
              '==': lambda a, b: a == b,
              '!=': lambda a, b: a != b,
              '<': lambda a, b: a < b,
              '>': lambda a, b: a > b,
              '<=': lambda a, b: a <= b,
              '>=': lambda a, b: a >= b,
              '&&': lambda a, b: a and b,
              '||': lambda a, b: a or b}


class BinaryOperation:

    """BinaryOperation - представляет бинарную операцию над двумя выражениями.
    Результатом вычисления бинарной операции является объект Number.
    Поддерживаемые операции:
    “+”, “-”, “*”, “/”, “%”, “==”, “!=”,
    “<”, “>”, “<=”, “>=”, “&&”, “||”."""

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self, scope):
        return Number(binary_ops[self.op](self.lhs.evaluate(scope).value,
                      self.rhs.evaluate(scope).value))


unary_ops = {'-': lambda a: -a,
             '!': lambda a: not a}


class UnaryOperation:

    """UnaryOperation - представляет унарную операцию над выражением.
    Результатом вычисления унарной операции является объект Number.
    Поддерживаемые операции: “-”, “!”."""

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope):
        return Number(unary_ops[self.op](self.expr.evaluate(scope).value))


def example():
    parent = Scope()
    parent["foo"] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent["bar"] = Number(10)
    scope = Scope(parent)
    assert 10 == scope["bar"].value
    scope["bar"] = Number(20)
    assert scope["bar"].value == 20
    print('It should print 2: ', end=' ')
    FunctionCall(FunctionDefinition('foo', parent['foo']),
                 [Number(5), UnaryOperation('-', Number(3))]).evaluate(scope)


def test_add_and_print():
    scope = Scope()
    add = BinaryOperation(Number(1), '+', Number(2))
    add.evaluate(scope)
    print ("It should be 3")
    p = Print(add)
    p.evaluate(scope)


def test_var_add_and_read():
    scope = Scope()
    read = Read('n')
    read.evaluate(scope)
    a = UnaryOperation('-', Number(1))
    add = BinaryOperation(a.evaluate(scope), '+', Reference('n'))
    print ("It should be n-1")
    write = Print(add)
    write.evaluate(scope)


def test_if():
    scope = Scope()
    read = Read('n')
    read.evaluate(scope)
    print ("It should be result of 2 <= n")
    le = Conditional(BinaryOperation(Number(2), '<=',
                     Reference('n')), Print(Number(1)), Print(Number(0)))
    le.evaluate(scope)


if __name__ == '__main__':
    example()
    test_add_and_print()
    test_var_add_and_read()
    test_if()
