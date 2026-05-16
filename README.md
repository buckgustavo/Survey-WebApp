# 📋 Survey WebApp

> Plataforma web para criação e gerenciamento de pesquisas/enquetes, construída com Django 5, PostgreSQL e Docker.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4479A1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## 📌 Sobre o Projeto

O **Survey WebApp** é uma aplicação fullstack que permite criar, distribuir e coletar respostas de pesquisas/enquetes. O sistema conta com autenticação de usuários, gerenciamento de surveys e uma arquitetura Django modular com separação por apps (`accounts` e `surveys`).

---

## 🚀 Funcionalidades

- ✅ Autenticação de usuários (cadastro, login, logout)
- ✅ Criação e edição de pesquisas (surveys)
- ✅ Coleta e visualização de respostas
- ✅ Interface web com templates Django
- ✅ Containerizado com Docker e Docker Compose
- ✅ Banco de dados PostgreSQL 16
- ✅ Configurações separadas por ambiente (dev/prod)
- ✅ Testes automatizados com pytest-django

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.2.1 |
| Banco de Dados | PostgreSQL 16 |
| Servidor WSGI | Gunicorn 23 |
| Assets Estáticos | WhiteNoise 6.9 |
| Containerização | Docker + Docker Compose |
| Testes | pytest-django 4.9 |
| Config | python-decouple |

---

## 📁 Estrutura do Projeto

```
Survey-WebApp/
├── apps/
│   ├── accounts/        # Autenticação e gerenciamento de usuários
│   └── surveys/         # Lógica de criação e respostas de pesquisas
├── config/
│   └── settings/        # Configurações por ambiente (dev/prod)
├── templates/           # Templates HTML Django
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## ⚙️ Como Rodar o Projeto

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados

### 1. Clone o repositório

```bash
git clone https://github.com/buckgustavo/Survey-WebApp.git
cd Survey-WebApp
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

> Edite o arquivo `.env` com suas configurações. Para desenvolvimento local, os valores padrão já funcionam.

### 3. Suba os containers

```bash
docker compose up --build
```

### 4. Execute as migrações

```bash
docker compose exec web python manage.py migrate
```

### 5. Crie um superusuário (opcional)

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Acesse a aplicação

```
http://localhost:8001
```

---

## 🧪 Rodando os Testes

```bash
docker compose exec web pytest
```

Os testes utilizam `pytest-django` com configurações definidas em `pytest.ini`.

---

## 🔐 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|---|---|---|
| `POSTGRES_DB` | Nome do banco de dados | `survey_db` |
| `POSTGRES_USER` | Usuário do PostgreSQL | `survey_user` |
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | `survey_pass` |
| `POSTGRES_HOST` | Host do banco (service Docker) | `db` |
| `POSTGRES_PORT` | Porta do PostgreSQL | `5432` |
| `SECRET_KEY` | Chave secreta Django | `sua-chave-aqui` |
| `DEBUG` | Modo debug | `True` / `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |

> ⚠️ **Nunca commite o arquivo `.env` com dados reais em produção.**

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: adiciona minha feature'`
4. Push para a branch: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">Code by<a href="https://github.com/buckgustavo">G.Buck</a></p>
