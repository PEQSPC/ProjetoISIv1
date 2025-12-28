# Base de Dados

O **ProjetoISIv1** utiliza **SQLite3** como sistema de gestao de base de dados para armazenar dados de monitorizacao industrial processados pelo sistema ETL.

---

## Visao Geral

### Tecnologia

**SQLite 3.40+** - Base de dados relacional embutida, serverless e self-contained

### Vantagens da Escolha

- **Simplicidade**: Nao requer servidor dedicado
- **Portabilidade**: Ficheiro unico `.db` facilmente transferivel
- **Performance**: Rapida para operacoes de leitura/escrita locais
- **Zero Configuracao**: Pronta a usar sem setup complexo
- **ACID Compliant**: Garante integridade transacional
- **Adequada para Prototipos**: Ideal para desenvolvimento e demonstracao

### Limitacoes

- Nao adequada para alta concorrencia (multiplas escritas simultaneas)
- Sem controlo de acessos granular
- Para producao enterprise, considerar migracao para SQL Server/PostgreSQL (ver [Fase 2](fase-2/roadmap-Iot-Simulator-Platform.md))

---

## Estrutura da Base de Dados

### Diagrama Entidade-Relacionamento

```mermaid
```

---

## Tabelas

### 1. estacoes

Armazena informacoes sobre as estacoes de producao monitorizadas.

```sql
CREATE TABLE estacoes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    localizacao TEXT,
    tipo_producao TEXT,
    capacidade_maxima INTEGER,
    status TEXT DEFAULT 'ativa',
    data_instalacao DATE,
    ultima_manutencao DATE
);
```

#### Campos (estacoes)

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `id` | INTEGER (PK) | Identificador unico da estacao |
| `nome` | TEXT (NOT NULL) | Nome descritivo da estacao |
| `localizacao` | TEXT | Localizacao fisica (ex: "Nave A - Setor 2") |
| `tipo_producao` | TEXT | Tipo de produto fabricado |
| `capacidade_maxima` | INTEGER | Capacidade maxima de producao (pecas/hora) |
| `status` | TEXT | Status operacional: 'ativa', 'inativa', 'manutencao' |
| `data_instalacao` | DATE | Data de instalacao da estacao |
| `ultima_manutencao` | DATE | Data da ultima manutencao |

#### Exemplo de Dados (estacoes)

```sql
INSERT INTO estacoes (id, nome, localizacao, tipo_producao, capacidade_maxima) VALUES
(1, 'Estacao de Montagem A1', 'Nave A - Setor 1', 'Montagem de Componentes', 100),
(2, 'Estacao de Soldadura B2', 'Nave B - Setor 2', 'Soldadura de Pecas', 80),
(3, 'Estacao de Inspecao C1', 'Nave C - Controlo Qualidade', 'Inspecao Visual', 120);
```

---

### 2. dados_acumulados

Regista metricas de producao acumuladas de cada estacao ao longo do tempo.

```sql
CREATE TABLE dados_acumulados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estacao_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    producao_total INTEGER DEFAULT 0,
    stock_atual INTEGER DEFAULT 0,
    tempo_paragem_segundos INTEGER DEFAULT 0,
    defeitos_total INTEGER DEFAULT 0,
    eficiencia_percentual REAL,
    observacoes TEXT,
    FOREIGN KEY (estacao_id) REFERENCES estacoes(id)
);
```

#### Campos (dados_acumulados)

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `id` | INTEGER (PK) | Identificador unico do registo |
| `estacao_id` | INTEGER (FK) | Referencia a estacao |
| `timestamp` | DATETIME | Data e hora do registo |
| `producao_total` | INTEGER | Total de pecas produzidas (acumulado) |
| `stock_atual` | INTEGER | Nivel de stock atual (pecas) |
| `tempo_paragem_segundos` | INTEGER | Tempo total de paragem em segundos |
| `defeitos_total` | INTEGER | Total de pecas defeituosas |
| `eficiencia_percentual` | REAL | Taxa de eficiencia calculada (OEE) |
| `observacoes` | TEXT | Notas adicionais |

#### Indices

```sql
CREATE INDEX idx_estacao_timestamp ON dados_acumulados(estacao_id, timestamp);
CREATE INDEX idx_timestamp ON dados_acumulados(timestamp DESC);
```

#### Exemplo de Dados (dados_acumulados)

```sql
INSERT INTO dados_acumulados (estacao_id, producao_total, stock_atual, tempo_paragem_segundos, defeitos_total, eficiencia_percentual) VALUES
(1, 450, 120, 180, 5, 94.5),
(2, 380, 95, 240, 8, 91.2),
(3, 520, 150, 120, 2, 97.8);
```

---

### 3. produtos

Catalogo de produtos/pecas fabricadas com informacao de precos.

```sql
CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    codigo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco_unitario REAL NOT NULL,
    custo_producao REAL,
    categoria TEXT,
    unidade TEXT DEFAULT 'unidade',
    ativo BOOLEAN DEFAULT 1,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Campos (produtos)

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `id` | INTEGER (PK) | Identificador unico do produto |
| `codigo` | TEXT (UNIQUE) | Codigo do produto (SKU) |
| `nome` | TEXT (NOT NULL) | Nome do produto |
| `descricao` | TEXT | Descricao detalhada |
| `preco_unitario` | REAL | Preco de venda unitario (EUR) |
| `custo_producao` | REAL | Custo de producao unitario (EUR) |
| `categoria` | TEXT | Categoria do produto |
| `unidade` | TEXT | Unidade de medida |
| `ativo` | BOOLEAN | Se o produto esta ativo no catalogo |
| `data_criacao` | DATETIME | Data de criacao do registo |

#### Exemplo de Dados (produtos)

```sql
INSERT INTO produtos (codigo, nome, preco_unitario, custo_producao, categoria) VALUES
('PCB-001', 'Placa de Circuito Impresso Tipo A', 15.50, 8.20, 'Eletronica'),
('MTL-045', 'Suporte Metalico de Fixacao', 3.80, 1.90, 'Mecanica'),
('PLT-112', 'Tampa Plastica de Protecao', 2.10, 0.95, 'Plasticos');
```

---

### 4. relatorios

Registo de relatorios gerados automaticamente pelo sistema.

```sql
CREATE TABLE relatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_geracao DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL,
    periodo_inicio DATE,
    periodo_fim DATE,
    conteudo TEXT,
    formato TEXT DEFAULT 'HTML',
    enviado BOOLEAN DEFAULT 0,
    destinatarios TEXT,
    caminho_ficheiro TEXT
);
```

#### Campos (relatorios)

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `id` | INTEGER (PK) | Identificador unico do relatorio |
| `data_geracao` | DATETIME | Data e hora de geracao |
| `tipo` | TEXT | Tipo: 'diario', 'semanal', 'mensal', 'alerta' |
| `periodo_inicio` | DATE | Data de inicio do periodo analisado |
| `periodo_fim` | DATE | Data de fim do periodo analisado |
| `conteudo` | TEXT | Conteudo do relatorio (HTML/texto) |
| `formato` | TEXT | Formato: 'HTML', 'PDF', 'JSON' |
| `enviado` | BOOLEAN | Se foi enviado por email |
| `destinatarios` | TEXT | Emails dos destinatarios (CSV) |
| `caminho_ficheiro` | TEXT | Caminho do ficheiro gerado |

#### Exemplo de Dados (relatorios)

```sql
INSERT INTO relatorios (tipo, periodo_inicio, periodo_fim, formato, enviado) VALUES
('diario', '2025-12-25', '2025-12-25', 'HTML', 1),
('semanal', '2025-12-19', '2025-12-25', 'PDF', 0);
```

---

## Views e Consultas uteis

### View: Resumo de Producao Diaria

```sql
CREATE VIEW v_resumo_diario AS
SELECT
    e.nome AS estacao,
    DATE(d.timestamp) AS data,
    SUM(d.producao_total) AS total_producao,
    SUM(d.defeitos_total) AS total_defeitos,
    SUM(d.tempo_paragem_segundos) AS total_paragem,
    AVG(d.eficiencia_percentual) AS eficiencia_media
FROM dados_acumulados d
JOIN estacoes e ON d.estacao_id = e.id
GROUP BY e.nome, DATE(d.timestamp);
```

### View: Top Produtos por Margem

```sql
CREATE VIEW v_margem_produtos AS
SELECT
    codigo,
    nome,
    preco_unitario,
    custo_producao,
    (preco_unitario - custo_producao) AS margem,
    ROUND(((preco_unitario - custo_producao) / preco_unitario * 100), 2) AS margem_percentual
FROM produtos
WHERE ativo = 1
ORDER BY margem DESC;
```

### Consulta: Performance de Estacoes (ultima Semana)

```sql
SELECT
    e.nome,
    COUNT(d.id) AS registos,
    SUM(d.producao_total) AS producao_total,
    SUM(d.defeitos_total) AS defeitos_total,
    ROUND(AVG(d.eficiencia_percentual), 2) AS eficiencia_media,
    SUM(d.tempo_paragem_segundos) / 3600.0 AS horas_paragem
FROM dados_acumulados d
JOIN estacoes e ON d.estacao_id = e.id
WHERE d.timestamp >= datetime('now', '-7 days')
GROUP BY e.nome
ORDER BY producao_total DESC;
```

### Consulta: Alertas de Baixa Eficiencia

```sql
SELECT
    e.nome,
    d.timestamp,
    d.eficiencia_percentual,
    d.defeitos_total,
    d.tempo_paragem_segundos
FROM dados_acumulados d
JOIN estacoes e ON d.estacao_id = e.id
WHERE d.eficiencia_percentual < 85
ORDER BY d.timestamp DESC
LIMIT 10;
```

---

## Triggers

### Trigger: Atualizar Eficiencia Automaticamente

```sql
CREATE TRIGGER calcular_eficiencia
AFTER INSERT ON dados_acumulados
BEGIN
    UPDATE dados_acumulados
    SET eficiencia_percentual =
        CASE
            WHEN NEW.producao_total > 0 THEN
                ((NEW.producao_total - NEW.defeitos_total) * 100.0 / NEW.producao_total)
            ELSE 0
        END
    WHERE id = NEW.id;
END;
```

### Trigger: Log de Auditoria

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabela TEXT,
    operacao TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    dados_anteriores TEXT,
    dados_novos TEXT
);

CREATE TRIGGER audit_producao
AFTER UPDATE ON dados_acumulados
BEGIN
    INSERT INTO audit_log (tabela, operacao, dados_anteriores, dados_novos)
    VALUES ('dados_acumulados', 'UPDATE',
            json_object('producao', OLD.producao_total),
            json_object('producao', NEW.producao_total));
END;
```

---

## Operacoes Comuns

### Inserir Novo Registo de Producao

```sql
INSERT INTO dados_acumulados (estacao_id, producao_total, stock_atual, tempo_paragem_segundos, defeitos_total)
VALUES (1, 458, 125, 190, 6);
```

### Atualizar Status de Estacao

```sql
UPDATE estacoes
SET status = 'manutencao', ultima_manutencao = CURRENT_DATE
WHERE id = 2;
```

### Consultar Producao de Hoje

```sql
SELECT * FROM dados_acumulados
WHERE DATE(timestamp) = DATE('now')
ORDER BY timestamp DESC;
```

### Eliminar Dados Antigos (Mais de 1 Ano)

```sql
DELETE FROM dados_acumulados
WHERE timestamp < datetime('now', '-1 year');
```

---

## Backup e Manutencao

### Criar Backup

```bash
# Backup completo
sqlite3 industrial_monitoring.db ".backup backup_$(date +%Y%m%d).db"

# Backup em SQL
sqlite3 industrial_monitoring.db ".dump" > backup.sql
```

### Restaurar Backup

```bash
# Restaurar de ficheiro .db
sqlite3 industrial_monitoring.db ".restore backup_20251226.db"

# Restaurar de SQL
sqlite3 new_database.db < backup.sql
```

### Otimizar Base de Dados

```sql
-- Reindexar
REINDEX;

-- Vacuum (compactar e otimizar)
VACUUM;

-- Analisar estatisticas para optimizacao de queries
ANALYZE;
```

### Verificar Integridade

```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

---

## Conexao e Acesso

### Python

```python
import sqlite3

conn = sqlite3.connect('industrial_monitoring.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM estacoes")
estacoes = cursor.fetchall()

conn.close()
```

### Node-RED

Utiliza o no `sqlite` configurado com o caminho da base de dados.

### CLI

```bash
sqlite3 industrial_monitoring.db
```

---

## Migracao Futura

Para ambientes de producao, planeia-se migrar para **SQL Server** ou **PostgreSQL** (ver [Fase 2](fase-2/roadmap-Iot-Simulator-Platform.md)).

### Vantagens da Migracao

- Melhor suporte para concorrencia
- Replicacao e alta disponibilidade
- Controlo de acessos granular
- Performance em grandes volumes
- Ferramentas empresariais de gestao

---

## Referencias

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [DB Browser for SQLite](https://sqlitebrowser.org/) - GUI para explorar a base de dados
