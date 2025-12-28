# ☁️ Azure IoT Hub Integration

Guia de integração do MQTT Simulator com Azure IoT Hub para telemetria em cloud.

---

## 🎯 Visão Geral

O simulador suporta dois modos:

| Modo | Destino | Biblioteca |
|------|---------|-----------|
| **MQTT** | Broker tradicional (Mosquitto, HiveMQ) | `paho-mqtt` |
| **Azure** | Azure IoT Hub | `azure-iot-device` |

Seleciona o modo através do campo `BROKER_TYPE` em `settings.json`.

---

## ⚙️ Configuração

### Modo MQTT (Broker Local)

```json
{
  "BROKER_TYPE": "mqtt",
  "BROKER_URL": "localhost",
  "BROKER_PORT": 1883,
  "TOPICS": [...]
}
```

**Campos obrigatórios**:
- `BROKER_TYPE`: "mqtt"
- `BROKER_URL`: Hostname do broker
- `BROKER_PORT`: Porta (default: 1883)

### Modo Azure IoT Hub

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=your-hub.azure-devices.net;DeviceId=device1;SharedAccessKey=...",
  "TOPICS": [...]
}
```

**Campos obrigatórios**:
- `BROKER_TYPE`: "azure"
- `AZURE_CONNECTION_STRING`: Connection string do device

**Campos opcionais**:
- `AZURE_MODEL_ID`: IoT Plug and Play model ID

---

## 🔑 Obter Connection String no Azure

1. Aceder ao [Azure Portal](https://portal.azure.com)
2. Navegar para o IoT Hub
3. **Devices** (em "Device management")
4. Selecionar device ou criar novo
5. Copiar **Primary Connection String**

**Formato**:
```
HostName=my-hub.azure-devices.net;DeviceId=sensor-01;SharedAccessKey=abc123...
```

---

## 🚀 Utilização

### Executar com MQTT Local

```bash
python main.py -f ../config/settings.json
```

ou explicitamente:

```bash
python main.py -f ../config/settings_mqtt_localhost.json
```

### Executar com Azure IoT Hub

**1. Atualizar connection string** em `config/settings_azure.json`:

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=YOUR-HUB.azure-devices.net;DeviceId=YOUR-DEVICE;SharedAccessKey=YOUR-KEY",
  "TOPICS": [...]
}
```

**2. Executar simulador**:

```bash
python main.py -f ../config/settings_azure.json
```

**3. Modo verbose** (ver payloads detalhados):

```bash
python main.py -f ../config/settings_azure.json -v
```

---

## 🔄 Como Funciona

### Modo MQTT
- Usa `paho-mqtt` (v1.6.1)
- Cria instâncias `Publisher`
- Publica em tópicos MQTT tradicionais
- Suporta TLS e autenticação

### Modo Azure
- Usa `azure-iot-device` (v2.14.0)
- Cria instâncias `AzurePublisher`
- Envia telemetria para IoT Hub
- Tópicos incluídos como propriedades de mensagem
- Encoding automático JSON + UTF-8

---

## 📋 Mapeamento de Tópicos

O simulador preserva a estrutura de tópicos MQTT no Azure:

**Tópico MQTT**:
```
linha_producao/estacao1
```

**Azure IoT Hub**:
- Enviado como telemetria
- Propriedade customizada: `topic=linha_producao/estacao1`
- Payload mantém estrutura JSON original

---

## 📊 Output de Exemplo

### Modo MQTT

```
Using MQTT publisher (broker: localhost:1883)
Starting: linha_producao/estacao1 ...
Starting: linha_producao/estacao2 ...
[12:30:45] Data published on: linha_producao/estacao1
```

### Modo Azure

```
Using Azure IoT Hub publisher
Connected to Azure IoT Hub for topic: linha_producao/estacao1
[12:30:45] Telemetry sent to Azure IoT Hub: linha_producao/estacao1
```

---

## 🔍 Monitorizar Telemetria no Azure

### Azure Portal

1. Ir para IoT Hub no portal
2. **Overview** → Ver métrica "Device to cloud messages"

### Azure CLI

**Monitorizar tudo**:
```bash
az iot hub monitor-events --hub-name YOUR-HUB-NAME
```

**Device específico**:
```bash
az iot hub monitor-events \
  --hub-name YOUR-HUB-NAME \
  --device-id YOUR-DEVICE-ID
```

### Exemplo de Mensagem Recebida

**Payload**:
```json
{
  "producao": 65,
  "paragem": 12,
  "stock": 78,
  "defeitos": 2
}
```

**Propriedades**:
```
topic: linha_producao/estacao1
contentType: application/json
contentEncoding: utf-8
```

---

## 📦 Dependências

### Modo MQTT
```
paho-mqtt==1.6.1
pydantic==2.12.0
```

### Modo Azure (adicional)
```
azure-iot-device==2.14.0
paho-mqtt==1.6.1  # requerido pelo Azure SDK
```

**Importante**: `paho-mqtt` **deve ser 1.6.1** (não 2.x) por compatibilidade com Azure IoT SDK.

**Instalar**:
```bash
pip install -r requirements.txt
```

---

## 🔀 Alternar Entre Modos

Basta mudar `BROKER_TYPE` no settings:

**Para MQTT**:
```json
{
  "BROKER_TYPE": "mqtt",
  "BROKER_URL": "localhost",
  "BROKER_PORT": 1883
}
```

**Para Azure**:
```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=..."
}
```

---

## 🏗️ Arquitetura

```
settings.json → BrokerSettings.is_azure_enabled()
                       |
        ┌──────────────┴──────────────┐
        |                             |
   MQTT Mode                    Azure Mode
        |                             |
   Publisher                   AzurePublisher
        |                             |
  paho-mqtt.client            azure-iot-device
```

Ambos implementam a mesma interface → intercambiáveis.

---

## 🛠️ Troubleshooting

### Erro: "AZURE_CONNECTION_STRING is required"

**Solução**: Adicionar connection string válido no settings.json

### Erro: "Invalid connection string format"

**Solução**: Verificar formato (deve conter `HostName`, `DeviceId`, `SharedAccessKey`)

### Erro: Conflito de versões paho-mqtt

**Solução**: 
```bash
pip uninstall paho-mqtt
pip install paho-mqtt==1.6.1
```

### Azure não conecta

**Testar conectividade**:
```bash
ping your-hub-name.azure-devices.net
```

### MQTT broker offline

**Verificar Mosquitto**:
```bash
mosquitto -v
```

---

## 📚 Configuração Completa Azure

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=production-hub.azure-devices.net;DeviceId=factory-01;SharedAccessKey=...",
  "AZURE_MODEL_ID": "dtmi:com:example:ProductionLine;1",
  "TOPICS": [
    {
      "TYPE": "multiple",
      "PREFIX": "factory/line",
      "RANGE_START": 1,
      "RANGE_END": 5,
      "TIME_INTERVAL": 5,
      "DATA": [
        {
          "NAME": "temperature",
          "TYPE": "float",
          "MIN_VALUE": 20.0,
          "MAX_VALUE": 80.0,
          "MAX_STEP": 2.0
        },
        {
          "NAME": "pressure",
          "TYPE": "float",
          "MIN_VALUE": 1000.0,
          "MAX_VALUE": 1100.0,
          "MAX_STEP": 5.0
        }
      ]
    }
  ]
}
```

---

## 🆘 Suporte

**MQTT Simulator**: Ver README principal  
**Azure IoT Hub**: [Documentação Oficial](https://docs.microsoft.com/azure/iot-hub/)  
**Azure SDK Issues**: [GitHub](https://github.com/Azure/azure-iot-sdk-python/issues)

---

**Integração Azure simplificada para testes IoT em cloud** ☁️