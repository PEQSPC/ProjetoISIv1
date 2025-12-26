import config from './config/read_config.js';
import { getAllRegistosEstacoes,getRegistoEstacoesByDateRange,getRegistoEstacoesByIdEstacao } from './service/read_db.js';
import { RegistoEstacao, RegistoEstacaoDB } from '../src/models/registo_estacoes.js';
import { convertRegistoEstacaoDBToRegistoEstacao } from './utils/process_data.js';
import { calcularProducaoTotal } from './utils/calculate_data.js';
import { emailTemplateProducaoTotal } from './utils/template_emails.js';
import { enviarEmail } from './service/send_email.js';


// Variável para definir a estação a processar
let estacao = 2;

//load email configuration
console.log("Email configuration loaded:", config);


// le dados do sqlite db
console.log("Reading data from database...");
const registos : RegistoEstacaoDB[]  = getAllRegistosEstacoes(100); 

console.log("Records read from database:", registos.length);

//Trata os dados lidos para o formato correto
const registosTratados: RegistoEstacao[] = registos.map(registoDB => {
  return convertRegistoEstacaoDBToRegistoEstacao(registoDB);
});

// Filtra os registos para a estacao 3
const registoEstacao3 : RegistoEstacao[]  = registosTratados.filter(registo => registo.Id_Estacao === estacao);
console.log("Filtered and processed records count:", registoEstacao3.length);
//Mostrar os dados tratados
//console.log("Registos tratados:", registoEstacao3);


// Fazer o calculo com os dados lidos
const producaoTotal = calcularProducaoTotal(registoEstacao3);

console.log(`Producao total calculada da estacao ${estacao}:`, producaoTotal);

//Enviar email com os calculos feitos


const emailTemplate = emailTemplateProducaoTotal(producaoTotal,estacao);

(async () => {
  try {
    const [result, message] = await enviarEmail(emailTemplate);

    if(result === true){
      console.log("Email enviado com sucesso.");
      console.log("Mensagem do email:", message);
    }else{
      console.log("Erro ao enviar email:", message);
    }
  } catch (err) {
    console.error("Erro ao enviar email:", err);
  }
})();