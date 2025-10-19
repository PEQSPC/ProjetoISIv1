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
├─ src/ # Código fonte  
│ ├─ config/ # Configuração central  
│ │ ├─ app-config.yaml # Ficheiro YAML com settings  
│ │ └─ index.ts # Carrega e exporta config  
│ │  
│ ├─ services/ # Serviços reutilizáveis → lógica de negócio principal (ex: enviar email)  
│ │ └─ emailService.ts # Função para enviar emails  
│ │  
│ ├─ utils/ # Funções utilitárias, helpers → funções auxiliares que ajudam os services a funcionar (ex: logs, validações, formatações)  
│ │ └─ logger.ts # Ex: log de erros, info  
│ │  
│ ├─ types/ # Tipos TypeScript  
│ │ └─ index.d.ts  
│ │  
│ └─ index.ts # Ponto de entrada da aplicação  
│  
├─ .env # Variáveis de ambiente (credenciais)  
├─ package.json # Dependências e scripts do projeto  
├─ tsconfig.json # Configuração do TypeScript  
└─ yarn.lock / package-lock.json # Gerenciador de pacotes lockfile

## Next Steps

ver readme principal do projeto
