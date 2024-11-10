from Shared import TOKEN_TYPE


class CompilationEngine:
    def __init__(self, tokenizer, file):
        self.tokenizer = tokenizer

        self.file = file
        self.level = 0

    def write_indent(self):
        for _ in range(self.level):
            self.file.write(" ")

    def write_new_line(self):
        self.file.write("\n")

    def write_inline_tag(self, tag, value):
        self.write_indent()
        self.file.write(f"<{tag}>{value}</{tag}>\n")

    def write_open_tag(self, tag):
        self.write_indent()
        self.file.write(f"<{tag}>\n")
        self.level = self.level + 1

    def write_close_tag(self, tag):
        self.level = self.level - 1
        self.write_indent()
        self.file.write(f"</{tag}>\n")

    def compile_keyword(self):
        if self.tokenizer.token_type() != TOKEN_TYPE.KEYWORD:
            raise ValueError("Parse Error: Expected Keyword Token")
        value = self.tokenizer.key_word()
        self.write_inline_tag("keyword", value)
        self.tokenizer.advance()

    def compile_identifier(self):
        if self.tokenizer.token_type() != TOKEN_TYPE.IDENTIFIER:
            raise ValueError("Parse Error: Expected Identifier Token")
        value = self.tokenizer.identifier()
        self.write_inline_tag("identifier", value)
        self.tokenizer.advance()

    def compile_symbol(self):
        if self.tokenizer.token_type() != TOKEN_TYPE.SYMBOL:
            raise ValueError("Parse Error: Expected Symbol Token")
        value = self.tokenizer.symbol()
        self.write_inline_tag("symbol", value)
        self.tokenizer.advance()

    # Maps to grammar rule: 'class' className '{' classVarDec * subroutineDec * '}'
    def compile_class(self):
        self.write_open_tag("class")
        self.compile_keyword()  # 'class'
        self.compile_identifier()  # 'className
        self.compile_symbol()  # '{'

        # classVarDec*
        while self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['static', 'field']:
            self.compile_class_var_dec()

        # subroutineDec*
        while self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['constructor', 'function', 'method']:
            self.compile_subroutine_dec()

        self.compile_symbol()  # '}'
        self.write_close_tag("class")

    # Maps to grammar rule: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody

    def compile_subroutine_dec(self):
        self.write_open_tag("subroutineDec")
        self.compile_keyword()  # ('constructor' | 'function' | 'method')

        # ('void' | type)
        if self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD:
            self.compile_keyword()
        else:
            self.compile_identifier()

        # subroutineName
        self.compile_identifier()

        # '('
        self.compile_symbol()

        # parameterList
        self.compile_parameter_list()

        # ')'
        self.compile_symbol()

        # subroutineBody
        self.compile_subroutine_body()

        self.write_close_tag("subroutineDec")

    # Maps to to the grammer rule 'int' | 'char' | 'boolean' | className
    def compile_type(self):
        if self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['int', 'char', 'boolean']:
            self.compile_keyword()
        else:
            self.compile_identifier()

    # Maps to grammar rule: ('static' | 'field) type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        self.write_open_tag("classVarDec")
        self.compile_keyword()  # ('static | 'field')
        # type
        self.compile_type()
        # varName
        self.compile_identifier()
        # (',' varName)*
        while self.tokenizer.token_type() == TOKEN_TYPE.SYMBOL and self.tokenizer.symbol() in [',']:
            # ','
            self.compile_symbol()
            # varName
            self.compile_identifier()
        # ";"
        self.compile_symbol()
        self.write_close_tag("classVarDec")

    # Maps to grammar rule: ( (type varName) (',' type varName)* )?
    def compile_parameter_list(self):
        self.write_open_tag("parameterList")
        if (self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['int', 'char', 'boolean']) or self.tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            # type
            self.compile_type()
            # varName
            self.compile_identifier()
            # (',' type varName)*
            while self.tokenizer.token_type() == TOKEN_TYPE.SYMBOL and self.tokenizer.symbol() in [',']:
                # ','
                self.compile_symbol()
                # type
                self.compile_type()
                # varName
                self.compile_identifier()
        self.write_close_tag("parameterList")

    # Maps to grammar rule: '{' varDec* statements '}'
    def compile_subroutine_body(self):
        self.write_open_tag("subroutineBody")
        # '{'
        self.compile_symbol()

        # varDec*
        while self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['var']:
            self.compile_var_dec()

        # statements
        self.compile_statements()

        # '}'
        self.compile_symbol()

        self.write_close_tag("subroutineBody")

    # Maps to the grammar rule: 'var' type varName (',' varName)* ';'
    def compile_var_dec(self):
        self.write_open_tag("varDec")
        self.compile_keyword()  # 'var'
        # type
        self.compile_type()
        # varName
        self.compile_identifier()
        # (',' varName)*
        while self.tokenizer.token_type() == TOKEN_TYPE.SYMBOL and self.tokenizer.symbol() in [',']:
            # ','
            self.compile_symbol()
            # varName
            self.compile_identifier()
        # ";"
        self.compile_symbol()
        self.write_close_tag("varDec")

    # Maps to the grammar rule: statement*
    def compile_statements(self):
        self.write_open_tag("statements")
        if self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD:
            if self.tokenizer.key_word() == "let":
                self.compile_let_statement()
            if self.tokenizer.key_word() == "if":
                self.compile_if_statement()
            if self.tokenizer.key_word() == "while":
                self.compile_while_statement()
            if self.tokenizer.key_word() == "do":
                self.compile_do_statement()
            if self.tokenizer.key_word() == "return":
                self.compile_return_statement()

        self.write_close_tag("statements")

    # maps to grammar rule 'let' varName ('[' expression ']')? '=' expression';'
    def compile_let_statement(self):
        self.write_open_tag("letStatement")
        # 'let'
        self.compile_keyword()
        # varName
        self.compile_identifier()

        # ('[' expression ']')?
        if self.tokenizer.token_type() == TOKEN_TYPE.SYMBOL and self.tokenizer.symbol() == '[':
            # '['
            self.compile_symbol()
            # expression
            self.compile_expression()
            # ']'
            self.compile_symbol()

        # ' ='
        self.compile_symbol()

        # expression
        self.compile_expression()

        # ';'
        self.compile_symbol()

        self.write_close_tag("letStatement")

    # maps to the grammar rule 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
    def compile_if_statement(self):
        self.write_open_tag("ifStatement")

        # 'if'
        self.compile_keyword()

        # '('
        self.compile_symbol()

        # expression
        self.compile_expression()

        # ')'
        self.compile_symbol()

        # '{'
        self.compile_symbol()

        # statements
        self.compile_statements()

        # '}'
        self.compile_symbol()

        if self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['else']:
            # else
            self.compile_keyword()
            # '{'
            self.compile_symbol()
            # statements
            self.compile_statements()
            # '}'
            self.compile_symbol()

        self.write_close_tag("ifStatement")

    # maps to the grammar rule 'while' '(' expression ')' '{' statements '}'
    def compile_while_statement(self):
        self.write_open_tag("whileStatement")
        # 'while'
        self.compile_keyword()

        # '('
        self.compile_symbol()

        # expression

        self.compile_expression()

        # ')'
        self.compile_symbol()

        # "{"
        self.compile_symbol()

        # statements
        self.compile_statements()

        # "}"
        self.compile_symbol()

        self.write_close_tag("whileStatement")

    # maps to the grammar rule: 'do' subroutineCall ';'
    def compile_do_statement(self):
        self.write_open_tag("doStatement")
        # 'do'
        self.compile_keyword()

        # subroutineCall
        self.compile_subroutine_call()

        # ';'
        self.compile_symbol()
        self.write_close_tag("doStatement")

    # maps to the grammar rule: 'return' expression? ';'
    def compile_return_statement(self):
        self.write_open_tag("returnStatement")
        # 'return'
        self.compile_keyword()

        # expression?
        if not (self.tokenizer.token_type() == TOKEN_TYPE.SYMBOL and self.tokenizer.symbol() == ';'):
            self.compile_expression()

        # ';'
        self.compile_symbol()
        self.write_close_tag("returnStatement")

    def compile_expression(self):
        pass

    def compile_subroutine_call(self):
        pass
