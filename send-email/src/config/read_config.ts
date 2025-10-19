import fs from "fs";
import yaml from "js-yaml";
import { AppConfig } from "../models/app_config.js";
import { CONFIG_PATH } from "../constants/paths.js";
import dotenv from "dotenv";


// Lê o ficheiro YAML
const file = fs.readFileSync(CONFIG_PATH, "utf8");
const rawConfig = yaml.load(file) as AppConfig;


// Carrega variáveis de ambiente do ficheiro .env
dotenv.config();

// Substitui variáveis de ambiente, se existirem
const config: AppConfig = {
  email: {
    host: rawConfig.email.host,
    port: rawConfig.email.port,
    secure: rawConfig.email.secure,
    service: rawConfig.email.service,
    email_to: process.env.EMAIL_TO || rawConfig.email.email_to,
    nome_remetente: process.env.NOME_REMETENTE || rawConfig.email.nome_remetente,
    auth: {
      user: process.env.EMAIL_USER || rawConfig.email.auth.user,
      pass: process.env.EMAIL_PASS || rawConfig.email.auth.pass,
    },
  },
};

export default config;