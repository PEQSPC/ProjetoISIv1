# Send Email

## Run project

Atencao primeiro precisas criar .env file para a app-config.yml
yarn install
yarn build
yarn start

## Flow deste projeto

Le dados da base de dados
Trata os dados
Envia relatorio dos dados via email

## Estrutura das Pastas

send-email/
│
├─ src/                     # Código fonte
│   ├─ config/              # Configuração central
│   │   ├─ app-config.yaml  # Ficheiro YAML com settings
│   │   └─ index.ts         # Carrega e exporta config
│   │
│   ├─ services/            # Serviços reutilizáveis --> business logic principal (ex: enviar email)
│   │   └─ emailService.ts  # Função para enviar emails
│   │
│   ├─ utils/               # Funções utilitárias, helpers --> funções auxiliares que ajudam a services a funcionar (ex: logs, validações, formatações)
│   │   └─ logger.ts        # Ex: log de erros, info
│   │
│   ├─ types/               # Tipos TypeScript
│   │   └─ index.d.ts
│   │
│   └─ index.ts             # Ponto de entrada da aplicação
│
├─ .env                     # Variáveis de ambiente (credenciais)
├─ package.json
├─ tsconfig.json
└─ yarn.lock / package-lock.json

## Next Steps

ver readme principal do projeto
