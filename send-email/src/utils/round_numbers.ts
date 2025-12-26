

// arredondar um numero para cima
export function roundUp(num: number, decimals: number = 0): number {
  const factor = Math.pow(10, decimals);
  return Math.ceil(num * factor) / factor;
}

// arredondar um numero para baixo
export function roundDown(num: number, decimals: number = 0): number {
  const factor = Math.pow(10, decimals);
  return Math.floor(num * factor) / factor;
}