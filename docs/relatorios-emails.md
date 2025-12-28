# Relatórios e Emails Automáticos

Sistema de geração e envio automático de relatórios de produção por email.

---

## Visão Geral

**Objetivo**: Enviar relatórios diários/semanais com KPIs de produção sem intervenção manual.

**Tecnologia**: Python scripts + SQLite + SMTP

**Trigger**: Agendado via cron ou executado por Node-RED

---

## Tipos de Relatórios

### 1. Relatório Diário

Resumo das últimas 24h de produção.

**Conteúdo**:
- Total produzido por estação
- Tempo de paragens
- Taxa de defeitos
- Eficiência (OEE)

**Destinatários**: Supervisores de produção

**Frequência**: Todos os dias às 7h00

### 2. Relatório Semanal

Análise agregada da semana anterior.

**Conteúdo**:
- Tendências de produção
- Comparação entre estações
- Top 5 problemas
- Recomendações

**Destinatários**: Gestão

**Frequência**: Segundas-feiras às 9h00

### 3. Alertas em Tempo Real

Notificações imediatas de anomalias.

**Triggers**:
- Paragem > 10 minutos
- Defeitos > 5% da produção
- Eficiência < 80%
- Stock crítico (< 20 unidades)

**Método**: Email ou SMS (futuro)

---

## Estrutura do Relatório

### Template HTML

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .kpi { display: inline-block; padding: 20px; margin: 10px; background: #f0f0f0; border-radius: 8px; }
        .kpi-value { font-size: 32px; font-weight: bold; color: #1976d2; }
        .kpi-label { font-size: 14px; color: #666; }
        .alert { background: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #1976d2; color: white; }
    </style>
</head>
<body>
    <h1>Relatório de Produção - {data}</h1>
    
    <div class="kpis">
        <div class="kpi">
            <div class="kpi-value">{producao_total}</div>
            <div class="kpi-label">Peças Produzidas</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">{oee}%</div>
            <div class="kpi-label">OEE</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">{defeitos}%</div>
            <div class="kpi-label">Taxa de Defeitos</div>
        </div>
    </div>

    {alertas_html}

    <h2>Produção por Estação</h2>
    <table>
        <tr>
            <th>Estação</th>
            <th>Produção</th>
            <th>Paragens (min)</th>
            <th>Defeitos</th>
            <th>Eficiência</th>
        </tr>
        {tabela_estacoes}
    </table>
</body>
</html>
```

---

## Implementação Python

### Script Principal: `report_generator.py`

```python
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

class ReportGenerator:
    def __init__(self, db_path='industrial_monitoring.db'):
        self.db_path = db_path
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
    
    def get_daily_data(self):
        """Busca dados das últimas 24h"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            e.nome,
            SUM(d.producao_total) as total_producao,
            SUM(d.tempo_paragem_segundos)/60 as paragens_min,
            SUM(d.defeitos_total) as total_defeitos,
            AVG(d.eficiencia_percentual) as eficiencia
        FROM dados_acumulados d
        JOIN estacoes e ON d.estacao_id = e.id
        WHERE d.timestamp >= datetime('now', '-1 day')
        GROUP BY e.nome
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def calculate_kpis(self, data):
        """Calcula KPIs agregados"""
        total_producao = sum(row[1] for row in data)
        total_defeitos = sum(row[3] for row in data)
        avg_eficiencia = sum(row[4] for row in data) / len(data) if data else 0
        taxa_defeitos = (total_defeitos / total_producao * 100) if total_producao > 0 else 0
        
        return {
            'producao_total': total_producao,
            'oee': round(avg_eficiencia, 1),
            'defeitos': round(taxa_defeitos, 2)
        }
    
    def generate_html_report(self, data, kpis):
        """Gera relatório HTML"""
        # Template HTML (simplificado para exemplo)
        template = """
        <html>
        <body>
            <h1>Relatório Diário - {data}</h1>
            <p>Produção Total: {producao_total} peças</p>
            <p>OEE: {oee}%</p>
            <p>Taxa Defeitos: {defeitos}%</p>
            
            <h2>Detalhes por Estação</h2>
            <table border="1">
                <tr><th>Estação</th><th>Produção</th><th>Paragens</th><th>Defeitos</th></tr>
                {rows}
            </table>
        </body>
        </html>
        """
        
        rows = ""
        for row in data:
            rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]:.0f}min</td><td>{row[3]}</td></tr>"
        
        return template.format(
            data=datetime.now().strftime('%Y-%m-%d'),
            producao_total=kpis['producao_total'],
            oee=kpis['oee'],
            defeitos=kpis['defeitos'],
            rows=rows
        )
    
    def send_email(self, html_content, recipients):
        """Envia email com relatório"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Relatório de Produção - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = self.email_from
        msg['To'] = ', '.join(recipients)
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
    
    def run_daily_report(self):
        """Executa relatório diário completo"""
        data = self.get_daily_data()
        kpis = self.calculate_kpis(data)
        html = self.generate_html_report(data, kpis)
        
        recipients = os.getenv('REPORT_RECIPIENTS', '').split(',')
        self.send_email(html, recipients)
        
        print(f"Relatório enviado para {len(recipients)} destinatários")

# Uso
if __name__ == '__main__':
    generator = ReportGenerator()
    generator.run_daily_report()
```

---

## Configuração SMTP

### Gmail (Recomendado)

1. Criar App Password: [Google Account Security](https://myaccount.google.com/security)
2. Configurar variáveis de ambiente:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_FROM="producao@empresa.com"
export EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"  # App Password
export REPORT_RECIPIENTS="supervisor@empresa.com,gestor@empresa.com"
```

### Outlook

```bash
export SMTP_SERVER="smtp-mail.outlook.com"
export SMTP_PORT="587"
```

### Gmail Empresarial (Google Workspace)

Mesmo que Gmail pessoal, mas usar email empresarial.

---

## Agendamento Automático

### Cron (Linux/Mac)

Editar crontab:
```bash
crontab -e
```

Adicionar:
```cron
# Relatório diário às 7h
0 7 * * * cd /path/to/project && python report_generator.py

# Relatório semanal às segundas 9h
0 9 * * 1 cd /path/to/project && python weekly_report.py
```

### Windows Task Scheduler

1. Abrir Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 7:00 AM
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\path\to\report_generator.py`

### Node-RED (Recomendado)

Usar node `inject` com cron:

```json
{
    "id": "schedule_daily_report",
    "type": "inject",
    "cron": "0 7 * * *",
    "name": "Trigger Daily Report",
    "wires": [["exec_python_report"]]
}
```

---

## Alertas em Tempo Real

### Integração Node-RED

Flow para detectar anomalias:

```javascript
// Node: function "Detect Anomalies"
if (msg.payload.dados.paragem > 600) { // 10 min
    msg.alert = {
        tipo: "PARAGEM_LONGA",
        estacao: msg.payload.estacao,
        duracao: msg.payload.dados.paragem,
        severidade: "alta"
    };
    return msg;
}

if (msg.payload.dados.defeitos / msg.payload.dados.producao > 0.05) {
    msg.alert = {
        tipo: "DEFEITOS_ELEVADOS",
        estacao: msg.payload.estacao,
        taxa: (msg.payload.dados.defeitos / msg.payload.dados.producao * 100).toFixed(2),
        severidade: "média"
    };
    return msg;
}

return null; // Sem alerta
```

Conectar a node `exec` que executa:
```bash
python send_alert_email.py --tipo "${alert.tipo}" --estacao "${alert.estacao}"
```

---

## Exemplo de Email Recebido

```
Assunto: Relatório de Produção - 2024-12-28

Relatório Diário de Produção
-----------------------------

KPIs Gerais:
✓ Produção Total: 1,358 peças
✓ OEE: 94.5%
⚠ Taxa de Defeitos: 1.2%

Produção por Estação:
┌─────────────┬──────────┬──────────┬──────────┬────────────┐
│ Estação     │ Produção │ Paragens │ Defeitos │ Eficiência │
├─────────────┼──────────┼──────────┼──────────┼────────────┤
│ Estação A1  │ 458      │ 3 min    │ 5        │ 95.2%      │
│ Estação B2  │ 420      │ 8 min    │ 8        │ 92.1%      │
│ Estação C1  │ 480      │ 2 min    │ 3        │ 96.8%      │
└─────────────┴──────────┴──────────┴──────────┴────────────┘

Alertas:
⚠ Estação B2: Tempo de paragem acima do normal
```

---

## Melhorias Futuras

- Gráficos embutidos (matplotlib → imagem inline)
- Comparação com dia/semana anterior
- Previsões baseadas em tendências
- Anexar PDF do relatório
- Integração Telegram/Slack para alertas
- Dashboard web para histórico de relatórios

---

## Troubleshooting

**Emails não enviados**:
- Verificar App Password do Gmail
- Testar SMTP manualmente: `telnet smtp.gmail.com 587`
- Verificar firewall/antivírus

**Dados vazios no relatório**:
- Confirmar que há dados nas últimas 24h no SQLite
- Verificar query SQL no script

**Cron não executa**:
- Verificar logs: `grep CRON /var/log/syslog`
- Testar script manualmente primeiro
- Usar caminhos absolutos no cron

---

## Referências

- [Python smtplib](https://docs.python.org/3/library/smtplib.html)
- [Gmail SMTP](https://support.google.com/mail/answer/7126229)
- [Cron Syntax](https://crontab.guru/)