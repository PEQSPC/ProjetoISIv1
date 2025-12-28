# Integração com API de Preços

Sistema de enriquecimento de dados de produção com preços de peças através de API externa.

---

## Objetivo

Calcular o **valor monetário da produção** em tempo real, combinando:
- Dados de produção (quantas peças foram produzidas)
- Preços unitários obtidos via API externa

**Resultado**: Métricas financeiras automáticas (receita estimada, margem, custo de defeitos).

---

## Arquitetura

```
MQTT Sensor → Node-RED → Extrai Código Produto (regex)
                              ↓
                        HTTP Request → API Externa
                              ↓
                    Recebe Preço Unitário
                              ↓
                  Calcula: Preço × Produção
                              ↓
                      Armazena em SQLite
```

---

## API Externa

### Endpoint Utilizado

Assumindo uma API REST que retorna preços de produtos:

```
GET https://api.empresa.com/produtos/{codigo}/preco
```

**Resposta**:
```json
{
  "codigo": "PCB-001",
  "nome": "Placa de Circuito Tipo A",
  "preco_unitario": 15.50,
  "moeda": "EUR",
  "ultima_atualizacao": "2024-12-28T10:00:00Z"
}
```

### Alternativa: API Pública Mockada

Para testes, pode-se usar:
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/)
- [Mocky.io](https://www.mocky.io/)
- API própria com Express/FastAPI

---

## Implementação no Node-RED

### Flow Completo

```
[MQTT In] → [Extrair Código] → [HTTP Request] → [Calcular Valor] → [SQLite]
                                                                    ↓
                                                              [Debug Output]
```

### 1. Extrair Código do Produto

**Node**: `function` - "Extrair Código Produto"

```javascript
// Entrada: msg.payload = {codigo_produto: "PCB-001", dados: {...}}
// Saída: msg.codigo_produto = "PCB-001"

if (msg.payload.codigo_produto) {
    msg.codigo_produto = msg.payload.codigo_produto;
    
    // Guardar dados originais para uso posterior
    flow.set('ultimo_payload', msg.payload);
    
    return msg;
} else {
    node.warn("Código de produto não encontrado");
    return null;
}
```

**Configuração**:
- Nome: "Extrair Código Produto"
- Outputs: 1

### 2. Consultar API de Preços

**Node**: `http request` - "Buscar Preço API"

**Configuração**:
- Method: GET
- URL: `https://api.empresa.com/produtos/{{codigo_produto}}/preco`
- Return: parsed JSON object
- Headers:
  - `Authorization`: `Bearer {{env.API_TOKEN}}`
  - `Content-Type`: `application/json`

**Alternativa com Template URL**:

Se a API requerer formato diferente:
```javascript
// Node function antes do HTTP request
msg.url = `https://api.empresa.com/produtos/${msg.codigo_produto}/preco`;
return msg;
```

### 3. Calcular Valor da Produção

**Node**: `function` - "Calcular Valor Total"

```javascript
// msg.payload agora tem dados da API (preco_unitario)
// Recuperar dados originais do flow context

let dados_producao = flow.get('ultimo_payload');
let preco_unitario = msg.payload.preco_unitario;

if (!preco_unitario || !dados_producao) {
    node.warn("Dados incompletos para cálculo");
    return null;
}

// Calcular valores
let producao = dados_producao.dados.producao;
let defeitos = dados_producao.dados.defeitos;

let valor_producao = producao * preco_unitario;
let valor_perdido_defeitos = defeitos * preco_unitario;
let valor_liquido = valor_producao - valor_perdido_defeitos;

// Montar payload para BD
msg.payload = {
    estacao: dados_producao.estacao,
    codigo_produto: dados_producao.codigo_produto,
    timestamp: dados_producao.timestamp,
    producao: producao,
    preco_unitario: preco_unitario,
    valor_producao: valor_producao.toFixed(2),
    defeitos: defeitos,
    valor_perdido: valor_perdido_defeitos.toFixed(2),
    valor_liquido: valor_liquido.toFixed(2)
};

// Query SQL para inserção
msg.topic = `
INSERT INTO producao_valores 
(estacao_id, codigo_produto, timestamp, producao, preco_unitario, 
 valor_producao, defeitos, valor_perdido, valor_liquido)
VALUES 
('${msg.payload.estacao}', '${msg.payload.codigo_produto}', 
 '${msg.payload.timestamp}', ${msg.payload.producao}, 
 ${msg.payload.preco_unitario}, ${msg.payload.valor_producao}, 
 ${msg.payload.defeitos}, ${msg.payload.valor_perdido}, 
 ${msg.payload.valor_liquido})
`;

return msg;
```

### 4. Armazenar em Base de Dados

**Node**: `sqlite` - "Gravar Valores Produção"

**Configuração**:
- Database: `/path/to/industrial_monitoring.db`
- SQL Query: `msg.topic` (definido na função anterior)

---

## Regex para Produtos Diversos

Se a API retorna múltiplos produtos e você precisa filtrar:

**Cenário**: API retorna lista de 100 produtos, você quer apenas IDs específicos.

**Node**: `function` - "Filtrar Produtos Relevantes"

```javascript
// msg.payload = [{id: 1, preco: 10}, {id: 2, preco: 20}, ...]
// Produtos que interessam: IDs 5, 12, 23

let produtos_interesse = [5, 12, 23];
let regex_ids = new RegExp(`^(${produtos_interesse.join('|')})$`);

let produtos_filtrados = msg.payload.filter(produto => {
    return regex_ids.test(produto.id.toString());
});

if (produtos_filtrados.length === 0) {
    node.warn("Nenhum produto relevante encontrado");
    return null;
}

// Guardar no contexto para uso posterior
flow.set('produtos_precos', produtos_filtrados);

msg.payload = produtos_filtrados;
return msg;
```

---

## Tabela de Base de Dados

### Schema SQL

```sql
CREATE TABLE producao_valores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estacao_id INTEGER,
    codigo_produto TEXT,
    timestamp DATETIME,
    producao INTEGER,
    preco_unitario REAL,
    valor_producao REAL,
    defeitos INTEGER,
    valor_perdido REAL,
    valor_liquido REAL,
    FOREIGN KEY (estacao_id) REFERENCES estacoes(id)
);

CREATE INDEX idx_producao_valores_timestamp 
ON producao_valores(timestamp DESC);
```

### Consultas Úteis

**Valor total produzido hoje**:
```sql
SELECT SUM(valor_liquido) as receita_diaria
FROM producao_valores
WHERE DATE(timestamp) = DATE('now');
```

**Top 3 produtos por receita (última semana)**:
```sql
SELECT 
    codigo_produto,
    SUM(valor_producao) as receita_total,
    SUM(valor_perdido) as perdas_defeitos
FROM producao_valores
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY codigo_produto
ORDER BY receita_total DESC
LIMIT 3;
```

**Custo de defeitos por estação**:
```sql
SELECT 
    e.nome,
    SUM(pv.valor_perdido) as custo_defeitos
FROM producao_valores pv
JOIN estacoes e ON pv.estacao_id = e.id
WHERE DATE(pv.timestamp) = DATE('now')
GROUP BY e.nome;
```

---

## Gestão de Erros

### Tratamento de Falhas na API

**Node**: `catch` - "Erro API"

Adicionar node catch que captura erros do HTTP request:

```javascript
// Node function conectado ao catch
if (msg.error) {
    node.error(`API falhou: ${msg.error.message}`);
    
    // Usar preço padrão/último conhecido
    let ultimo_preco = flow.get(`preco_${msg.codigo_produto}`) || 0;
    
    msg.payload = {
        preco_unitario: ultimo_preco,
        fonte: "cache",
        aviso: "API indisponível - usando último preço conhecido"
    };
    
    return msg;
}
```

### Cache de Preços

Evitar chamadas repetidas para o mesmo produto:

```javascript
// No início do flow de preços
let codigo = msg.codigo_produto;
let cache_preco = flow.get(`preco_cache_${codigo}`);
let cache_timestamp = flow.get(`preco_cache_ts_${codigo}`);

// Cache válido por 1 hora
if (cache_preco && cache_timestamp) {
    let agora = Date.now();
    let diff_minutos = (agora - cache_timestamp) / 1000 / 60;
    
    if (diff_minutos < 60) {
        node.warn(`Usando preço em cache para ${codigo}`);
        msg.payload = {preco_unitario: cache_preco};
        return msg;
    }
}

// Se não há cache válido, prosseguir para HTTP request
return msg;
```

**Após receber resposta da API**:
```javascript
// Guardar em cache
flow.set(`preco_cache_${msg.codigo_produto}`, msg.payload.preco_unitario);
flow.set(`preco_cache_ts_${msg.codigo_produto}`, Date.now());
```

---

## Rate Limiting

Se a API tem limite de requests:

```javascript
// Antes do HTTP request
let ultima_chamada = flow.get('api_ultima_chamada') || 0;
let agora = Date.now();
let delay_minimo = 1000; // 1 segundo entre chamadas

if (agora - ultima_chamada < delay_minimo) {
    let esperar = delay_minimo - (agora - ultima_chamada);
    node.warn(`Rate limit: aguardar ${esperar}ms`);
    
    // Agendar retry
    setTimeout(() => {
        node.send(msg);
    }, esperar);
    
    return null;
}

flow.set('api_ultima_chamada', agora);
return msg;
```

---

## Variáveis de Ambiente

Configurar credenciais da API:

**Ficheiro**: `settings.js` (Node-RED)

```javascript
functionGlobalContext: {
    API_BASE_URL: process.env.API_BASE_URL || 'https://api.empresa.com',
    API_TOKEN: process.env.API_TOKEN || '',
}
```

**Uso no flow**:
```javascript
let api_url = global.get('API_BASE_URL');
let token = global.get('API_TOKEN');

msg.url = `${api_url}/produtos/${msg.codigo_produto}/preco`;
msg.headers = {
    'Authorization': `Bearer ${token}`
};

return msg;
```

---

## Exemplo de Flow JSON

```json
[
    {
        "id": "api_flow_start",
        "type": "mqtt in",
        "topic": "linha_producao/estacao/+",
        "broker": "mqtt_broker",
        "wires": [["extrair_codigo"]]
    },
    {
        "id": "extrair_codigo",
        "type": "function",
        "name": "Extrair Código",
        "func": "msg.codigo_produto = msg.payload.codigo_produto;\nflow.set('ultimo_payload', msg.payload);\nreturn msg;",
        "wires": [["http_get_preco"]]
    },
    {
        "id": "http_get_preco",
        "type": "http request",
        "method": "GET",
        "url": "https://api.empresa.com/produtos/{{codigo_produto}}/preco",
        "wires": [["calcular_valor"]]
    },
    {
        "id": "calcular_valor",
        "type": "function",
        "name": "Calcular Valor",
        "func": "// código da função anterior",
        "wires": [["sqlite_insert"]]
    },
    {
        "id": "sqlite_insert",
        "type": "sqlite",
        "db": "industrial_monitoring.db",
        "wires": [[]]
    }
]
```

---

## Métricas Disponíveis

Após implementação completa, terás acesso a:

1. **Valor de Produção por Estação** (€/dia)
2. **Custo de Defeitos** (€ perdidos)
3. **ROI de Manutenções** (comparar antes/depois)
4. **Produtos Mais Lucrativos**
5. **Tendências de Margem**

Estas métricas podem ser visualizadas no dashboard ou incluídas nos relatórios automáticos.

---

## Troubleshooting

**API retorna erro 401**:
- Verificar token de autenticação
- Confirmar validade do token
- Verificar headers da request

**Valores sempre zero**:
- Verificar se API está retornando dados
- Debug do node HTTP request
- Confirmar parsing JSON correto

**Performance lenta**:
- Implementar cache de preços
- Reduzir frequência de chamadas
- Considerar batch requests se API suportar

---

## Melhorias Futuras

- Webhook quando preços mudam (em vez de polling)
- Batch requests para múltiplos produtos
- Fallback para múltiplas APIs (redundância)
- Machine learning para prever preços

---

Esta integração transforma dados operacionais em métricas financeiras, permitindo decisões de negócio baseadas em dados em tempo real.