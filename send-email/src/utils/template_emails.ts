import config from '../config/read_config';
import { EmailTemplate } from '../models/email_template';



// Email template para producao total vai entrar um numero e retornar um objeto com subject e body
export function emailTemplateProducaoTotal(number : number,estacao: number)  : EmailTemplate {
    const subject = "Produção Total Calculada";
    const html = `
  <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.5; padding: 20px;">
    <h1 style="color: #2E86C1; font-size: 24px;">
      Olá, <strong>${config.email.nome_remetente}</strong>!
    </h1>

    <div style="margin-top: 20px; padding: 15px; background-color: #F4F6F7; border-radius: 8px;">
      <p style="font-size: 16px; margin: 5px 0;">
        <strong>Produção Total:</strong> ${number}
      </p>
      <p style="font-size: 16px; margin: 5px 0;">
        <strong>Estação:</strong> ${estacao}
      </p>
    </div>

    <p style="margin-top: 20px; font-size: 14px; color: #777;">
      Esta é uma mensagem automática. Por favor, não responda.
    </p>
  </div>
`;
    return   {
        subject: subject,
        body: html
    };
};