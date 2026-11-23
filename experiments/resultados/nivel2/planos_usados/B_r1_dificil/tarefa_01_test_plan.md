# Test Plan

1. Critério: A classe `RepositorioUsuarios` deve ter um método `remover(id)` que remove o usuário com o id especificado.
   - entrada: r=RepositorioUsuarios(); r.adicionar('Ana', 'Admin'); r.remover(1); r.listar()
   - esperado: []
2. Critério: O método `excluir_usuario(id)` deve levantar uma exceção `KeyError` se o usuário com o id especificado não existir.
   - entrada: r=RepositorioUsuarios(); r.adicionar('Ana', 'Admin'); s=ServicoUsuarios(r); s.excluir_usuario(999)
   - esperado: KeyError
3. Critério: A classe `ServicoUsuarios` deve ter um método `excluir_usuario(id)` que utiliza o método `remover(id)` da instância de `RepositorioUsuarios`.
   - entrada: r=RepositorioUsuarios(); r.adicionar('Ana', 'Admin'); s=ServicoUsuarios(r); s.excluir_usuario(1); s.excluir_usuario(1)
   - esperado: KeyError