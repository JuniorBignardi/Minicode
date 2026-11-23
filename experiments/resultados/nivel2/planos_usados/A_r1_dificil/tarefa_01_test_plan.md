# Test Plan

1. Critério: O método `remover` deve existir na classe `RepositorioUsuarios` e deletar um usuário com base no ID.
   - entrada: repositorio_usuarios = RepositorioUsuarios()
repositorio_usuarios.adicionar(1, 'usuario1')
repositorio_usuarios.remover(1)
   - esperado: O usuário com ID 1 deve ser removido do repositório.
2. Critério: O método `excluir_usuario` deve existir na classe `ServicoUsuarios` e chamar o método `remover` do repositório.
   - entrada: repositorio_usuarios = RepositorioUsuarios()
repositorio_usuarios.adicionar(1, 'usuario1')
servico_usuarios = ServicoUsuarios(repositorio_usuarios)
servico_usuarios.excluir_usuario(1)
   - esperado: O usuário com ID 1 deve ser removido do repositório.
3. Critério: Se o usuário não existir, o método `excluir_usuario` deve levantar uma exceção `KeyError`.
   - entrada: repositorio_usuarios = RepositorioUsuarios()
repositorio_usuarios.adicionar(2, 'usuario2')
servico_usuarios = ServicoUsuarios(repositorio_usuarios)
servico_usuarios.excluir_usuario(1)
   - esperado: KeyError