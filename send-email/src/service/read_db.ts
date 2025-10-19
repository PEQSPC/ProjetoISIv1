import Database from "better-sqlite3";
import path from "path";
import { DB_PATH } from "../constants/paths";
import { RegistoEstacao,RegistoEstacaoDB } from "../models/registo_estacoes.js";

//Aqui so vai ter chamadas a base de dados



// Abre a base de dados SQLite
const db = new Database(DB_PATH);

export function getAllRegistosEstacoes(limit: number = 100): RegistoEstacaoDB[] {
  const stmt = db.prepare(`
    SELECT * 
    FROM registo_estacoes
    ORDER BY Timestamp DESC
    LIMIT ?
  `);

  const rows: any[] = stmt.all(limit);

  return rows.map(row => ({
    Id_registo: row.Id_registo,
    Id_Estacao: row.Id_Estacao,
    Producao: row.Producao,
    Stock: row.Stock,
    Paragem: row.Paragem,
    Defeitos: row.Defeitos,
    Timestamp: new Date(row.Timestamp),
  }));
}



export function getRegistoEstacoesByIdEstacao(idEstacao: number, limit: number = 100): RegistoEstacaoDB[] {
  const stmt = db.prepare(
    "SELECT * FROM registo_estacoes WHERE Id_Estacao = ? ORDER BY Timestamp DESC LIMIT ?"
  );

  // stmt.all() devolve um array de objetos
  const rows = stmt.all(idEstacao, limit);

  // Assumimos que o SQLite devolve os tipos corretos (strings/numbers)
  return rows.map((row: any) : RegistoEstacaoDB => ({
    Id_registo: row.Id_registo,
    Id_Estacao: row.Id_Estacao,
    Producao: row.Producao,
    Stock: row.Stock,
    Paragem: row.Paragem,
    Defeitos: row.Defeitos,
    Timestamp: new Date(row.Timestamp), // converte para Date
  }));
}



export function getRegistoEstacoesByDateRange(startDate: Date, endDate: Date, limit: number = 100): RegistoEstacaoDB[] {
  const stmt = db.prepare(
    "SELECT * FROM registo_estacoes WHERE Timestamp BETWEEN ? AND ? ORDER BY Timestamp DESC LIMIT ?"
  );

  const rows = stmt.all(startDate, endDate, limit);

  return rows.map((row: any) : RegistoEstacaoDB => ({
    Id_registo: row.Id_registo,
    Id_Estacao: row.Id_Estacao,
    Producao: row.Producao,
    Stock: row.Stock,
    Paragem: row.Paragem,
    Defeitos: row.Defeitos,
    Timestamp: new Date(row.Timestamp),
  }));
};      