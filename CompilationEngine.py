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
        self.file.write(f"</{tag}>")

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

    # Maps to grammar rule: class -> 'class' className '{' classVarDec * subroutineDec * '}'
    def compile_class(self):
        self.write_open_tag("class")
        self.compile_keyword()  # 'class'
        self.compile_identifier()  # 'className
        self.compile_symbol()  # '{'

        # classVarDec*
        while self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD and self.tokenizer.key_word() in ['static', 'field']:
            self.compile_class_var_dec()

        self.write_close_tag("class")

    # Maps to grammar rule: ('static' | 'field') -> type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        self.write_open_tag("classVarDec")
        self.compile_keyword()  # ('static | 'field')
        # type
        if self.tokenizer.token_type() == TOKEN_TYPE.KEYWORD:
            self.compile_keyword()
        else:
            self.compile_identifier()
        # varName
        self.compile_identifier()
        # (',' varName)*
        while self.tokenizer.token_type() == TOKEN_TYPE.SYMBOL and self.tokenizer.symbol() in [',']:
            self.compile_symbol()
            self.compile_identifier()
        # ";"
        self.compile_symbol()
        self.write_close_tag("classVarDec")
