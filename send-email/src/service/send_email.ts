
import nodemailer from "nodemailer";
import config from "../config/read_config";
import { EmailTemplate } from "../models/email_template";

// Configurar o transporte
const transporter = nodemailer.createTransport({
  service: config.email.service,
  auth: {
    user: config.email.auth.user,
    pass: config.email.auth.pass,
  },
});

// Função para enviar email
export async function enviarEmail(templateHtml: EmailTemplate) : Promise<[boolean,string]> {

  const mailOptions = {
    from: config.email.auth.user,
    to: config.email.email_to,
    subject: templateHtml.subject,
    html: templateHtml.body,
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    return [true, info.response];
  } catch (error: string | any) {
    console.error("Erro ao enviar email:", error);
    return [false, error.message];
  }
}