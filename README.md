# Add_Sheet_Interface_v2 (Venv Setup)

Execute o projeto em ambiente isolado (.venv), sem instalar bibliotecas globalmente.

## Estrutura
- `main.py`: entrypoint
- `layouts/`, `utils/`, `config/`, `logs/`
- `requirements.txt`: dependências (Paramiko, python-dotenv, etc.)
- `setup_venv.ps1`: cria e prepara o venv
- `run.ps1`: ativa o venv e executa o app

## Como usar (Windows PowerShell)
1) No diretório do projeto, crie o ambiente virtual e instale dependências:
   ```powershell
   .\setup_venv.ps1
   ```
2) Execute a aplicação (opcionalmente informe a pasta de dados):
   ```powershell
   .\run.ps1 -DataDir ".\data"
   ```

Notas:
- O diretório padrão de dados é `./data` (configure em `config/settings.json`).
- Para testar SSH, crie `config/.env` baseado em `config/env.example` e rode `python get_rates_info.py` após ativar o venv.