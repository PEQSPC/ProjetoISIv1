
# ETL PROCESSOS

```markdown
# Processos ETL e Transformações

O **Node-RED** atua como o motor central de **ETL** (Extract, Transform, Load).

---

## Estratégia

1. **Extração (Extract)**  
   - Dados recolhidos de sensores MQTT.
   - Publicação periódica dos valores de produção, stock e paragem.

2. **Transformação (Transform)**  
   - Normalização dos dados.
   - Cálculo de acumulados.
   - Validação e filtragem de outliers.

3. **Carregamento (Load)**  
   - Inserção e atualização dos dados em **SQLite3**.
   - Geração de logs e relatórios.

---

## Exemplos de Transformações

| Tipo | Operação | Descrição |
|------|-----------|-----------|
| Limpeza | Eliminar valores nulos | Ignorar mensagens sem payload válido |
| Normalização | Converter tipos | Garantir que todos os valores são `float` |
| Agregação | Somar produção acumulada | `acumulado += msg.payload.producao` |
| Regex | Extrair ID do produto | `/produto-(\d+)/` |
| Filtro | Ignorar paragens < 2s | `if (msg.payload.paragem >= 2)` |

---

## Jobs Node-RED

Os fluxos Node-RED incluem:

1. **MQTT In → Function → SQLite Out**  
2. **Function → Python Exec → Email Out**

Esses fluxos são documentados visualmente no ficheiro `flows.json` e explicados no relatório final.
