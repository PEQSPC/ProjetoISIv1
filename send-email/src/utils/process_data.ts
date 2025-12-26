

//converter RegistoEstacaoDB para RegistoEstacao
import { RegistoEstacao, RegistoEstacaoDB } from "../models/registo_estacoes.js";
import { roundUp } from "./round_numbers.js";

export function convertRegistoEstacaoDBToRegistoEstacao(registoDB: RegistoEstacaoDB): RegistoEstacao {
  return {
    Id_registo: registoDB.Id_registo,
    Id_Estacao: registoDB.Id_Estacao,
    Producao: parseFloat(registoDB.Producao),
    Stock: parseFloat(registoDB.Stock),
    Paragem: registoDB.Paragem.length > 0 ? roundUp(parseInt(registoDB.Paragem),0) : 0,
    Defeitos: registoDB.Defeitos.length > 0 ? roundUp(parseInt(registoDB.Defeitos),0) : 0,
    Timestamp: formatTimestamp(registoDB.Timestamp),
  };
}


//short Timestamp to string format DD-MM-YYYY HH:MM:SS
export function formatTimestamp(timestamp: Date): string {
  const pad = (num: number) => String(num).padStart(2, '0');
  return `${pad(timestamp.getDate())}-${pad(timestamp.getMonth() + 1)}-${timestamp.getFullYear()} ${pad(timestamp.getHours())}:${pad(timestamp.getMinutes())}:${pad(timestamp.getSeconds())}`;
}
