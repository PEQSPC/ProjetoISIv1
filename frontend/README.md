# IoT Simulator Manager - Frontend

Interface web para gerir simulações IoT através da API FastAPI.

## Tecnologias

- **React 19** - Framework frontend
- **TypeScript** - Type safety
- **Vite** - Build tool e dev server
- **Material-UI (MUI) v7** - Componentes UI
- **Axios** - Cliente HTTP

## Funcionalidades

- ✅ Listar simulações ativas
- ✅ Criar nova simulação via JSON
- ✅ Parar/deletar simulações
- ✅ Atualização automática a cada 5 segundos
- ✅ Validação de JSON em tempo real
- ✅ Tratamento de erros
- ✅ Loading states
- ✅ Interface responsiva

## Instalação

```bash
cd frontend
yarn install
# ou
npm install
```

## Configuração

O frontend espera a API a correr em `http://localhost:8000` por padrão.

Para alterar, crie um ficheiro `.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Desenvolvimento

```bash
yarn dev
# ou
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`

## Build para Produção

```bash
yarn build
# ou
npm run build
```

Os ficheiros serão gerados na pasta `dist/`.

Para pré-visualizar o build:

```bash
yarn preview
# ou
npm run preview
```

## Estrutura

```
frontend/
├── src/
│   ├── App.tsx          # Componente principal
│   ├── main.tsx         # Entry point
│   └── index.css        # Estilos globais
├── public/
├── package.json
└── vite.config.ts
```

## API Endpoints Utilizados

- `GET /simulations` - Lista todas as simulações
- `POST /simulations` - Cria nova simulação
- `DELETE /simulations/{simulation_id}` - Para/deleta simulação

## Formato de Configuração JSON

O JSON para criar uma simulação deve seguir este formato:

```json
{
  "BROKER_URL": "test.mosquitto.org",
  "BROKER_PORT": 1883,
  "TIME_INTERVAL": 10,
  "duration_minutes": 30,
  "TOPICS": [
    {
      "TYPE": "multiple",
      "PREFIX": "demo/sensor",
      "RANGE_START": 1,
      "RANGE_END": 3,
      "TIME_INTERVAL": 1,
      "DATA": [
        {
          "NAME": "temp",
          "TYPE": "int",
          "MIN_VALUE": 20,
          "MAX_VALUE": 30
        }
      ]
    }
  ]
}
```

Ver documentação completa da API em `/docs` do projeto principal.
