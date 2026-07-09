# SindCON

Sistema Inteligente de Sindicancia Condominial.

Este MVP inicia uma aplicacao Flask para centralizar registros administrativos e operacionais do condominio, formando uma base para relatorios periodicos.

## Banco de dados

O MVP utiliza uma base SQL local com SQLite, acessada pelo Flask-SQLAlchemy. As tabelas possuem campo `id` como chave primaria para facilitar gestao, filtros, edicao e exclusao de registros.

## Modulos do MVP

- Dashboard operacional
- Diario de bordo com CRUD
- Manutencoes com CRUD
- Agenda de manutencoes
- Ocorrencias com CRUD
- Compras com CRUD
- Banco de evidencias
- Relatorios por periodo com impressao

## Como executar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

O banco SQLite sera criado automaticamente em `instance/sindcon.db` no primeiro acesso, com alguns registros iniciais para demonstracao.

## Como enviar para o GitHub

1. Crie um repositorio vazio no GitHub.
2. No terminal, dentro da pasta do projeto, execute:

```powershell
git init
git add .
git commit -m "Primeira versao do SindCON"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
git push -u origin main
```

Troque `SEU-USUARIO` e `NOME-DO-REPOSITORIO` pelos dados do repositorio criado.

Para publicar novas alteracoes depois:

```powershell
git add .
git commit -m "Atualiza projeto"
git push
```

## Como publicar online no Render.com

O Render publica aplicacoes Flask como um **Web Service** conectado ao repositorio GitHub. Este projeto ja possui o arquivo `serve.py`, usado como ponto de entrada em producao.

1. Acesse `https://render.com` e entre na sua conta.
2. Clique em **New** > **Web Service**.
3. Conecte sua conta GitHub e selecione o repositorio do SindCON.
4. Configure o servico:
   - **Language**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn serve:app`
5. Clique em **Create Web Service**.
6. Aguarde o build finalizar. Ao concluir, o Render exibira uma URL no formato:

```text
https://nome-do-servico.onrender.com
```

Sempre que houver um novo `git push` para a branch configurada, o Render fara um novo deploy automaticamente.

### Observacao sobre o banco SQLite no Render

Este MVP usa SQLite em `instance/sindcon.db`. Em servicos sem disco persistente, arquivos locais podem ser perdidos em deploys ou reinicios. Para manter os dados:

- use um plano do Render com **Persistent Disk**;
- configure o disco com mount path em `/opt/render/project/src/instance`;
- ou migre o projeto para PostgreSQL antes de usar em producao.

## Proximos passos sugeridos

- Autenticacao e perfis de acesso
- Upload real de anexos e evidencias
- Exportacao PDF dos relatorios
- Workflows de aprovacao
- Notificacoes
- Cadastros administrativos
- Regras parametrizadas por condominio
