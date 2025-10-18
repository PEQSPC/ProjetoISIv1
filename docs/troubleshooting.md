# Troubleshooting

| Problema | Causa provável | Solução |
|-----------|----------------|----------|
| Node-RED não liga | Porta ocupada | Muda a porta: `node-red -p 1881` |
| MQTT não conecta | Broker offline | Reinicia Mosquitto: `sudo systemctl restart mosquitto` |
| SQLite bloqueado | Conflito de acesso | Fecha outras conexões e tenta novamente |
| Emails não enviados | Autenticação falhou | Verifica SMTP e permissões “App Password” |
