
//dtos
export interface RegistoEstacaoDB {
  Id_registo: number;
  Id_Estacao: number;
  Producao: string;
  Stock: string;
  Paragem: string;
  Defeitos: string;
  Timestamp: Date;

}

export interface RegistoEstacao {
  Id_registo: number;
  Id_Estacao: number;
  Producao: number;
  Stock: number;
  Paragem: number;
  Defeitos: number;
  Timestamp: string;
}
