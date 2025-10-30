# VitaBrasil Backend API

API REST para o marketplace VitaBrasil.

## 🚀 Deploy no Railway

1. Criar novo projeto no Railway
2. Conectar ao repositório GitHub
3. Adicionar PostgreSQL
4. Configurar variável `SECRET_KEY`
5. Deploy automático!

## 📋 Endpoints

### Autenticação
- `POST /api/auth/register` - Cadastro
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Usuário atual (requer token)

### Profissionais
- `GET /api/professionals/search` - Buscar profissionais
- `GET /api/professionals/:id` - Detalhes do profissional

### Usuário
- `GET /api/users/profile` - Ver perfil (requer token)
- `PATCH /api/users/profile` - Atualizar perfil (requer token)

### Agendamentos
- `POST /api/appointments/` - Criar agendamento (requer token)
- `GET /api/appointments/` - Listar agendamentos (requer token)
- `PATCH /api/appointments/:id` - Atualizar agendamento (requer token)

## 🔧 Desenvolvimento Local

```bash
pip install -r requirements.txt
python run.py
```

## 🔐 Variáveis de Ambiente

- `DATABASE_URL` - URL do PostgreSQL (automático no Railway)
- `SECRET_KEY` - Chave secreta para JWT
- `CORS_ORIGINS` - Origens permitidas (padrão: *)

