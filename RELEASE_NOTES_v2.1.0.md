# Release Notes - v2.1.0

## ✨ Novidades
- **Histórico de Revisões Vertical**: O layout da tabela de revisões no corpo da issue foi alterado para um formato chave-valor vertical, melhorando a legibilidade.
- **Controle de Atualização**: Adicionada flag `--update` ao `main.py`.
    - **Processamento de Lista**: Por padrão, **NÃO** sobrescreve issues existentes, preservando dados ricos. Use `--update` se deseja forçar a atualização via lista.
    - **Processamento de DOCX**: Continua atualizando por padrão (fonte da verdade).
- **Workflow Atualizado**: A action `process-list` agora utiliza a flag `--update` para garantir a atualização das issues.

## 🛠️ Melhorias
- Logs de erro suprimidos na verificação de acesso a projetos (evita flood de mensagens "GraphQL error").
- Títulos das issues agora aparecem nos logs de execução.
