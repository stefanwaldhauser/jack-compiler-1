import os
import sys
from pathlib import Path
from Shared import token_type_to_xml_tag


from JackTokenizer import JackTokenizer


def parse_file(path):
    tokens = []
    with open(path, 'r', encoding="utf-8") as file:
        tokenizer = JackTokenizer(file)
        while tokenizer.has_more_tokens():
            token = tokenizer.current_token
            tokenizer.advance()
            tokens.append(token)
        file.close()
    return tokens


def writeFile(path, tokens):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write("<tokens>" + '\n')
        for token in tokens:
            tag = token_type_to_xml_tag[token.token_type]
            f.write(f"<{tag}>")

            value_to_write = token.value
            if value_to_write == "<":
                value_to_write = "&lt;"
            if value_to_write == ">":
                value_to_write = "&gt;"
            if value_to_write == "&":
                value_to_write = "&amp;"

            f.write(str(value_to_write))
            f.write(f"</{tag}>\n")
        f.write("</tokens>" + '\n')


def parse_directory(path):
    path_to_tokens = []
    for file_path in path.glob('*.jack'):
        tokens = parse_file(file_path)
        path_to_tokens.append((file_path, tokens))
    return path_to_tokens


def main():
    if len(sys.argv) == 1:
        path = Path(os.getcwd())
    else:
        path = Path(sys.argv[1])

    if path.is_file():
        tokens = parse_file(path)
        output_path = path.with_stem(path.stem + "T").with_suffix(".xml")
        writeFile(output_path, tokens)

    else:
        path_to_tokens = parse_directory(path)
        for (file_path, tokens) in path_to_tokens:
            output_path = file_path.with_stem(
                file_path.stem + "T").with_suffix(".xml")
            writeFile(output_path, tokens)


if __name__ == "__main__":
    main()
