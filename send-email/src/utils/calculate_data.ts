

import { RegistoEstacao } from "../models/registo_estacoes.js";
import { roundUp } from "./round_numbers.js";




//calcular producao total
export function calcularProducaoTotal(registos: RegistoEstacao[]): number {
  const producaoTotal = registos.reduce((acc, registo) => acc + registo.Producao, 0);
  return roundUp(producaoTotal, 0);
}
