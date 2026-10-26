from minicode.tools.busca import search_code
from minicode.tools.files import create_file, list_files, read_file, write_file
from minicode.tools.git import git_diff
from minicode.tools.testes import run_tests

# liga o nome que a LLM escreve no JSON à função que executa
FERRAMENTAS = {
    "list_files": list_files,
    "read_file": read_file,
    "search_code": search_code,
    "git_diff": git_diff,
    "create_file": create_file,
    "write_file": write_file,
    "run_tests": run_tests,
}

# nomes dos argumentos de cada ferramenta (todos texto); o "finish" não tem argumentos
PARAMETROS = {
    "list_files": ["diretorio"],
    "read_file": ["path"],
    "search_code": ["padrao", "diretorio"],
    "git_diff": [],
    "create_file": ["path", "content"],
    "write_file": ["path", "content"],
    "run_tests": [],
    "finish": [],
}
