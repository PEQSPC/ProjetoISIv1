export interface EmailConfig {
  host: string;
  port: number;
  secure: boolean;
  service: string;
  email_to: string;
  nome_remetente: string;
  auth: {
    user: string;
    pass: string;
  };
}