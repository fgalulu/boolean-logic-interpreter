# character types
AND, OR, NOT, TRUE, FALSE, EOF, LPAREN, RPAREN = 'AND', 'OR', 'NOT', "TRUE", 'FALSE', 'EOF', 'LPAREN', 'RPAREN'


class Token(object):
    def __init__(self, _type):
        self.type = _type
        # self.value = value

    def __str__(self):
        """ String representation for the characters"""
        return 'Token[{type}]'.format(type=self.type)

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, line):
        self.line = line
        self.pointer = -1
        self.current_char = None
        self.next()

    def next(self):
        """get next character"""
        self.pointer += 1
        if self.pointer > len(self.line) - 1:
            self.current_char = None
        else:
            self.current_char = self.line[self.pointer]

    def del_space(self):
        """ delete whitespace"""
        while self.current_char is not None and self.current_char.isspace():
            self.next()

    def get_token(self):
        tokens = []

        while self.current_char is not None:

            if self.current_char.isspace():
                self.del_space()
                continue

            elif self.current_char == 'T':
                self.next()
                tokens.append(Token(TRUE))

            elif self.current_char == 'F':
                self.next()
                tokens.append(Token(FALSE))

            elif self.current_char == '∧':
                self.next()
                tokens.append(Token(AND))

            elif self.current_char == '∨':
                self.next()
                tokens.append(Token(OR))

            elif self.current_char == '¬':
                self.next()
                tokens.append(Token(NOT))

            elif self.current_char == '(':
                tokens.append(Token(LPAREN))
                self.next()

            elif self.current_char == ')':
                tokens.append(Token(RPAREN))
                self.next()

            else:
                self.error()

        return tokens

    def error(self):
        raise Exception('Invalid syntax!')


# NODES


class BoolNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, ops, right_node):
        self.ops = ops
        self.right_node = right_node
        self.left_node = left_node

    def __repr__(self):
        return f'({self.left_node}, {self.ops}, {self.right_node})'


class NotNode:
    def __init__(self, ops, node):
        self.ops = ops
        self.node = node

    def __repr__(self):
        return f'({self.ops}, {self.node})'


#######################################
# PARSE RESULT
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


# Parser


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_token = self.tokens[self.tok_idx]
        return self.current_token

    def parse(self):
        res = self.expr()

        return res

    def factor(self):
        res = ParseResult()
        tok = self.current_token

        if tok.type in (TRUE, FALSE):
            res.register(self.advance())
            return res.success(BoolNode(tok))
        elif tok.type == LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if self.current_token.type == RPAREN:
                res.register(self.advance())
                return res.success(expr)

    def term(self):
        res = ParseResult()
        val = res.register(self.factor())

        while self.current_token.type is NOT:
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(self.factor())
            val = NotNode(op_tok, right)

        return res.success(val)

    def expr(self):
        res = ParseResult()
        left = res.register(self.term())

        while self.current_token.type in (AND, OR):
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(self.term())
            left = BinOpNode(left, op_tok, right)

        return res.success(left)


# Bool

class Bool:
    def __init__(self, value):
        self.value = value

    def to_bool(self):
        return self.value.type == TRUE

    def and_to(self, other):
        if isinstance(other, Bool):
            if Bool(self.to_bool() and other.to_bool()).value:
                return Bool(Token(TRUE))
            return Bool(Token(FALSE))

    def or_to(self, other):
        if isinstance(other, Bool):
            if Bool(self.to_bool() or other.to_bool()).value:
                return Bool(Token(TRUE))
            return Bool(Token(FALSE))

    def not_to(self):
        if self.value.type == TRUE:
            self.value = Token(FALSE)
        elif self.value.type == FALSE:
            self.value = Token(TRUE)

        return self

    def __repr__(self):
        return str(self.value)


class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_BoolNode(self, node):
        # print('bool')
        return Bool(node.tok)

    def visit_NotNode(self, node):
        unary = self.visit(node.node)
        print(unary)

        if node.ops.type == NOT:
            # print('inside not')
            unary = unary.not_to()
            print(unary)

        return unary

    def visit_BinOpNode(self, node):
        # print('bin')
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)
        # print(f"left: {left}")
        # print(f"right: {right}")

        if node.ops.type == AND:
            result = left.and_to(right)
        elif node.ops.type == OR:
            result = left.or_to(right)

        # print(f"result: {result}")
        return  result


def main():
    while True:
        try:
            text = input('λ>')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        tokens = lexer.get_token()
        # print(tokens)

        parser = Parser(tokens)
        ast = parser.parse()
        # print(ast.node)

        interpreter = Interpreter()
        result = interpreter.visit(ast.node)

        print(result)


if __name__ == '__main__':
    main()
