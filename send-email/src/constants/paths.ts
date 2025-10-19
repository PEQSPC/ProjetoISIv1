import path from "path";

// Caminho absoluto da raiz do projeto
const ROOT = path.resolve(__dirname, "../..");
const PROJECT_ROOT = path.resolve(__dirname, "../../..");

export const CONFIG_PATH = path.join(ROOT, "src/config/app-config.yaml");
export const DB_PATH = path.join(PROJECT_ROOT, "flows-node-red/data/sql-db-estacao.db");