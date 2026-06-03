# 🦐 Dashboard de Carcinicultura

![Workflow](https://img.shields.io/github/actions/workflow/status/USERNAME/REPO_NAME/ci.yml?branch=main&style=flat-square)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/streamlit-ready-brightgreen?style=flat-square)

Projeto educacional que analisa a mortalidade de *Litopenaeus vannamei* em viveiros sob diferentes estratégias de manejo, com foco no período chuvoso (jun-ago). O dashboard interativo foi desenvolvido em Streamlit e usa dados simulados gerados por `gerar_dados.py`.

**Status:** Pronto para apresentação e publicação no GitHub.

## Demonstração rápida

1. Instale dependências:

```bash
pip install -r requirements.txt
```

2. Gere os dados (primeira execução):

```bash
python gerar_dados.py
```

3. Rode o dashboard:

```bash
streamlit run app.py
```

O Streamlit abrirá em `http://localhost:8501`.

## Estrutura do repositório

- [app.py](app.py) — aplicação Streamlit principal
- [gerar_dados.py](gerar_dados.py) — script para gerar `dados_camarao.csv`
- [dados_camarao.csv](dados_camarao.csv) — (opcional) dados gerados
- [requirements.txt](requirements.txt) — dependências
- [README.md](README.md) — este arquivo
- [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md) — instruções detalhadas

## O que eu incluí para tornar o projeto apresentável

- README polido com instruções de execução
- `.gitignore` (Padrão Python)
- `LICENSE` (MIT) — incluirá permissão para compartilhar
- `CONTRIBUTING.md` — instruções básicas para contribuir
- GitHub Actions básico (`.github/workflows/ci.yml`) que valida instalação das dependências

## Dicas antes de subir para o GitHub

- Remova arquivos sensíveis (nenhum sensível neste projeto).
- Verifique o `.gitignore` para ambientes virtuais e caches.
- Atualize o nome de usuário/repositório no badge de workflow (substitua `USERNAME/REPO_NAME`).

## Licença

Este projeto está licenciado sob a MIT License — consulte o arquivo `LICENSE`.

## Autor

Desenvolvido como projeto acadêmico. Substitua o nome do autor em `LICENSE` se desejar.