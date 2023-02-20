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


class Interpreter(object):
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

    # def boolean(self):
    #     """Assign boolean value of true or false for T and F"""
    #     if self.current_char == 'T':
    #         value = True
    #         # self.next()
    #     elif self.current_char == 'F':
    #         value = False
    #         self.eat()
    #     else:
    #         value = ''
    #         self.next()
    #     return value

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

    # def eat(self, token_type):
    #     if self.current_token.type == token_type:
    #         self.current_token = self.get_token()
    #     else:
    #         self.error()
    #
    # def value(self):
    #     token = self.current_token
    #     print(f'in value {token.type}')
    #     if token.type == TRUE:
    #         self.next()
    #         return True
    #     elif token.type == FALSE:
    #         self.next()
    #         print('here here')
    #         return False
    #     return token.value

    # def expr(self):

        # self.current_token = self.get_token()
        # break_p = True
        #
        # # result = self.value()
        # # print(result)
        # # while self.current_token.type in (AND, OR, NOT):
        # #     token = self.current_token
        # #
        # #     if token.type == NOT:
        # #         print(f'in not {result}')
        # #         self.eat(NOT)
        # #         result = not result
        # #         print(f'after not {result}')
        # while break_p:
        #     result = self.boolean()
        #     print(f'in while {result}')
        #     while self.current_token.type in (AND, OR, NOT):
        #         token = self.current_token
        #
        #         if token.type == NOT:
        #             print(f'in not {result}')
        #             self.eat(NOT)
        #             result = not result
        #             print(f'after not {result}')
        #             self.next()
        #
        #         elif token.type == AND:
        #             self.eat(AND)
        #             result = result and self.current_token.value
        #         #
        #         # elif token.type == OR:
        #         #     self.eat(OR)
        #         #     result = result or self.current_token.value
        #         break
        #
        #     if self.current_token.type == EOF:
        #         break_p = False
        #
        # if result:
        #     return 'T'
        # else:
        #     return 'F'

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
        self.right_node = node

    def __repr__(self):
        return f'({self.ops}, {self.right_node})'

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
        tok = self.current_token

        if tok.type in (TRUE, FALSE):
            self.advance()
            return BoolNode(tok)
        elif tok.type is NOT:
            next_node = self.advance()
            self.advance()
            return NotNode(tok, next_node)

    def term(self):
        res = self.factor()

        while self.current_token.type is NOT:
            op_tok = self.current_token
            self.advance()
            right = self.factor()
            res = NotNode(op_tok, right)

        return res

    def expr(self):
        left = self.term()

        while self.current_token.type in (AND, OR, NOT):
            op_tok = self.current_token
            self.advance()
            right = self.term()
            left = BinOpNode(left, op_tok, right)

        return left


def main():
    while True:
        try:
            text = input('λ>')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        tokens = interpreter.get_token()
        print(tokens)

        parser = Parser(tokens)
        ast = parser.parse()
        print(ast)


if __name__ == '__main__':
    main()
