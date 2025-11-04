# VitaBrasil Backend

Backend API para o sistema VitaBrasil - Plataforma de agendamento de consultas médicas.

## Tecnologias

- Python 3.11
- Flask
- PostgreSQL
- SQLAlchemy

## Estrutura

```
/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências Python
├── runtime.txt         # Versão do Python
└── server/            # Módulos do backend
    ├── database.py    # Configuração do banco
    ├── models.py      # Modelos SQLAlchemy
    └── routes.py      # Rotas da API
```

## Deploy

Este projeto está configurado para deploy automático no Railway.

## Variáveis de Ambiente

- `DATABASE_URL`: URL de conexão PostgreSQL (configurada automaticamente pelo Railway)
- `SECRET_KEY`: Chave secreta para JWT
- `ALGORITHM`: Algoritmo de criptografia (HS256)

