import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
from tree_sitter import Language, Parser, TreeCursor, Node
from tqdm.auto import tqdm
import numpy as np

def extract_files_subsample(root: Path, kth: int) -> List[Path]:
    """
    Extract every kth file from each project and return all file paths
    """
    files = []
    for project in os.listdir(root):
        project_files = sorted(os.listdir(root / project))[::kth]
        files += [root / project / filename for filename in project_files]
    return files

def read(filename: Path) -> bytes:
    return bytes(open(filename, "r").read(), "utf-8")

def traverse(cursor: TreeCursor, extracted_methods: List[str]):

    if cursor.node.type == METHOD_TYPE:
        extracted_methods.append(cursor.node)

    if cursor.goto_first_child():
        traverse(cursor, extracted_methods)
    
    if cursor.goto_next_sibling():
        traverse(cursor, extracted_methods)
    else:
        cursor.goto_parent()

Language.build_library('build/my-languages.so', ['tree-sitter-java'])
JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

METHOD_TYPE = "method_declaration"
IDENTIFIER_TYPE = "identifier"
MASK_TOKEN = b"<mask>"
        
def extract_methods_from_files(files: List[Path]) -> List[Node]:
    extracted_methods = []
    
    for filepath in tqdm(files):
        content = read(filepath)
        parsed_tree = parser.parse(content)
        cursor = parsed_tree.walk()
        try:
            traverse(cursor, extracted_methods)
        except RecursionError:
            pass
    
    return extracted_methods

split_regex = re.compile("(?<=[a-z])(?=[A-Z])|_|[0-9]|(?<=[A-Z])(?=[A-Z][a-z])|\\s+")

def split_token(token: str):
    return split_regex.split(token)

def prepare_sample(method_root: Node) -> Dict:
    name = None
    name_span = None
    for child in method_root.children:
        if child.type == IDENTIFIER_TYPE:
            name = child.text
            name_span = (
                child.start_byte - method_root.start_byte, 
                child.end_byte - method_root.start_byte
            )
            break
    
    if name is None:
        return None

    code = method_root.text
    code = code[:name_span[0]] + MASK_TOKEN + code[name_span[1]:]

    return {
        "name": " ".join(split_token(name.decode())).lower(), 
        "code": code.decode()
    }

def prepare_samples(method_roots: List[Node]) -> List[Dict[str, str]]:
    samples = [prepare_sample(method) for method in method_roots]
    samples = [sample for sample in samples if sample is not None]
    return samples