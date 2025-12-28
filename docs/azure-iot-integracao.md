# Integração Azure IoT Hub

Sistema de envio de telemetria para a cloud usando Azure IoT Hub, permitindo monitorização centralizada e análise de dados em escala.

---

## Visão Geral

**Objetivo**: Conectar sensores IoT simulados ao Azure IoT Hub para processamento na cloud.

**Biblioteca**: `azure-iot-device` (Python SDK oficial da Microsoft)

**Arquitetura Dual**:
```
Simulador IoT
     ├──> MQTT Local (Mosquitto) → Node-RED → Dashboard/DB Local
     └──> Azure IoT Hub → Stream Analytics → Azure SQL/Storage
```

**Casos de Uso**:
- Monitorização multi-site centralizada
- Backup de dados na cloud
- Análise com Azure Stream Analytics
- Dashboards em Azure IoT Central
- Integração com Power BI

---

## Instalação

```bash
pip install azure-iot-device
```

**Dependências**:
```txt
azure-iot-device==2.13.0
paho-mqtt==1.6.1
```

---

## Configuração Azure IoT Hub

### 1. Criar IoT Hub (Azure Portal)

1. Aceder ao [Azure Portal](https://portal.azure.com)
2. Criar recurso → Internet of Things → IoT Hub
3. Configurar:
   - **Nome**: `producao-industrial-hub`
   - **Região**: West Europe
   - **Tier**: F1 (gratuito) ou S1 (produção)
4. Criar

### 2. Registar Device

**Via Portal**:
1. IoT Hub → Devices → Add Device
2. Device ID: `estacao-1`
3. Authentication: Symmetric Key (auto-generate)
4. Copiar **Primary Connection String**

**Via Azure CLI**:
```bash
az iot hub device-identity create \
  --hub-name producao-industrial-hub \
  --device-id estacao-1
  
az iot hub device-identity connection-string show \
  --hub-name producao-industrial-hub \
  --device-id estacao-1
```

**Connection String** (guardar de forma segura):
```
HostName=producao-industrial-hub.azure-devices.net;DeviceId=estacao-1;SharedAccessKey=xxxxxxxxxxxx
```

---

## Implementação Python

### Exemplo Básico: Enviar Telemetria

```python
# azure_iot_sender.py

from azure.iot.device import IoTHubDeviceClient, Message
import json
import time
from datetime import datetime
import os

class AzureIoTSender:
    def __init__(self, connection_string):
        """
        Inicializar cliente Azure IoT
        
        Args:
            connection_string: Connection string do device no Azure IoT Hub
        """
        self.client = IoTHubDeviceClient.create_from_connection_string(
            connection_string
        )
        self.connected = False
    
    def connect(self):
        """Conectar ao Azure IoT Hub"""
        try:
            self.client.connect()
            self.connected = True
            print(f"✓ Conectado ao Azure IoT Hub")
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            self.connected = False
    
    def send_telemetry(self, data):
        """
        Enviar telemetria para Azure IoT Hub
        
        Args:
            data: Dicionário com dados do sensor
        """
        if not self.connected:
            print("✗ Não conectado ao Azure IoT Hub")
            return False
        
        try:
            # Adicionar timestamp se não existir
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            # Criar mensagem
            message = Message(json.dumps(data))
            
            # Definir propriedades da mensagem
            message.content_type = "application/json"
            message.content_encoding = "utf-8"
            
            # Adicionar propriedades customizadas
            message.custom_properties["estacao_id"] = str(data.get("estacao", "unknown"))
            message.custom_properties["tipo_alerta"] = self._check_alert(data)
            
            # Enviar
            self.client.send_message(message)
            print(f"✓ Telemetria enviada: Estação {data.get('estacao')}")
            
            return True
            
        except Exception as e:
            print(f"✗ Erro ao enviar telemetria: {e}")
            return False
    
    def _check_alert(self, data):
        """Verificar se há condições de alerta"""
        dados = data.get('dados', {})
        
        if dados.get('defeitos', 0) > 10:
            return "defeitos_alto"
        elif dados.get('paragem', 0) > 600:  # 10 min
            return "paragem_longa"
        elif dados.get('stock', 0) < 20:
            return "stock_baixo"
        
        return "normal"
    
    def disconnect(self):
        """Desconectar do Azure IoT Hub"""
        if self.connected:
            self.client.disconnect()
            self.connected = False
            print("✓ Desconectado do Azure IoT Hub")


# Exemplo de uso
if __name__ == "__main__":
    # Connection string do device (usar variável de ambiente)
    CONN_STRING = os.getenv('AZURE_IOT_CONNECTION_STRING')
    
    if not CONN_STRING:
        print("Erro: Definir AZURE_IOT_CONNECTION_STRING")
        exit(1)
    
    # Criar cliente
    azure_sender = AzureIoTSender(CONN_STRING)
    azure_sender.connect()
    
    # Enviar dados de exemplo
    dados_exemplo = {
        "estacao": 1,
        "dados": {
            "producao": 458,
            "stock": 120,
            "paragem": 180,
            "defeitos": 5
        }
    }
    
    azure_sender.send_telemetry(dados_exemplo)
    
    # Desconectar
    azure_sender.disconnect()
```

---

## Integração com Simulador MQTT Existente

### Simulador Dual: MQTT Local + Azure IoT

```python
# mqtt_publisher_azure.py

import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient, Message
import json
import time
import random
from datetime import datetime
import os

class DualPublisher:
    """Publica para MQTT local E Azure IoT Hub simultaneamente"""
    
    def __init__(self, mqtt_broker, mqtt_port, azure_conn_string, estacao_id):
        # MQTT Local
        self.mqtt_client = mqtt.Client()
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        
        # Azure IoT
        self.azure_client = IoTHubDeviceClient.create_from_connection_string(
            azure_conn_string
        )
        
        self.estacao_id = estacao_id
        self.running = False
    
    def connect(self):
        """Conectar a ambos os endpoints"""
        # Conectar MQTT local
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            print(f"✓ Conectado ao MQTT local ({self.mqtt_broker}:{self.mqtt_port})")
        except Exception as e:
            print(f"✗ Erro MQTT local: {e}")
        
        # Conectar Azure IoT
        try:
            self.azure_client.connect()
            print(f"✓ Conectado ao Azure IoT Hub")
        except Exception as e:
            print(f"✗ Erro Azure IoT: {e}")
    
    def publish_data(self, data):
        """Publicar dados para ambos os destinos"""
        timestamp = datetime.now().isoformat()
        
        payload = {
            "estacao": self.estacao_id,
            "timestamp": timestamp,
            "dados": data
        }
        
        # Publicar no MQTT local
        try:
            topic = f"linha_producao/estacao/{self.estacao_id}"
            self.mqtt_client.publish(topic, json.dumps(data), qos=2)
            print(f"→ MQTT: {topic}")
        except Exception as e:
            print(f"✗ Erro MQTT publish: {e}")
        
        # Publicar no Azure IoT Hub
        try:
            message = Message(json.dumps(payload))
            message.content_type = "application/json"
            message.content_encoding = "utf-8"
            message.custom_properties["estacao_id"] = str(self.estacao_id)
            
            self.azure_client.send_message(message)
            print(f"→ Azure: Estação {self.estacao_id}")
        except Exception as e:
            print(f"✗ Erro Azure publish: {e}")
    
    def simulate_production(self, interval=60):
        """Simular produção continuamente"""
        self.running = True
        
        print(f"\n▶ Iniciando simulação (Estação {self.estacao_id})")
        print(f"Intervalo: {interval}s | Ctrl+C para parar\n")
        
        try:
            while self.running:
                # Gerar dados sintéticos
                data = {
                    "producao": random.randint(80, 120),
                    "stock": random.randint(50, 200),
                    "paragem": random.randint(0, 300),
                    "defeitos": random.randint(0, 8)
                }
                
                # Publicar
                self.publish_data(data)
                
                # Aguardar
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n■ Simulação interrompida")
            self.running = False
    
    def disconnect(self):
        """Desconectar de ambos"""
        self.running = False
        
        try:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("✓ MQTT local desconectado")
        except:
            pass
        
        try:
            self.azure_client.disconnect()
            print("✓ Azure IoT desconectado")
        except:
            pass


# Executar
if __name__ == "__main__":
    # Configuração
    MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    AZURE_CONN = os.getenv('AZURE_IOT_CONNECTION_STRING')
    ESTACAO_ID = int(os.getenv('ESTACAO_ID', 1))
    
    if not AZURE_CONN:
        print("Erro: Definir AZURE_IOT_CONNECTION_STRING")
        exit(1)
    
    # Criar publisher dual
    publisher = DualPublisher(MQTT_BROKER, MQTT_PORT, AZURE_CONN, ESTACAO_ID)
    
    # Conectar
    publisher.connect()
    
    # Simular
    try:
        publisher.simulate_production(interval=60)
    finally:
        publisher.disconnect()
```

### Variáveis de Ambiente

```bash
# .env
export MQTT_BROKER="localhost"
export MQTT_PORT="1883"
export AZURE_IOT_CONNECTION_STRING="HostName=....azure-devices.net;DeviceId=estacao-1;SharedAccessKey=..."
export ESTACAO_ID="1"
```

---

## Device Twin (Propriedades do Device)

### Ler e Atualizar Propriedades

```python
# device_twin_manager.py

from azure.iot.device import IoTHubDeviceClient
import json

class DeviceTwinManager:
    def __init__(self, connection_string):
        self.client = IoTHubDeviceClient.create_from_connection_string(
            connection_string
        )
        self.client.connect()
    
    def get_desired_properties(self):
        """Obter configurações enviadas pela cloud"""
        twin = self.client.get_twin()
        desired = twin['desired']
        
        print("Configurações desejadas (cloud → device):")
        print(json.dumps(desired, indent=2))
        
        return desired
    
    def update_reported_properties(self, properties):
        """Reportar estado do device para a cloud"""
        self.client.patch_twin_reported_properties(properties)
        print(f"✓ Propriedades reportadas atualizadas: {properties}")
    
    def get_full_twin(self):
        """Obter twin completo"""
        twin = self.client.get_twin()
        
        print("\nDevice Twin completo:")
        print(json.dumps(twin, indent=2))
        
        return twin


# Exemplo de uso
if __name__ == "__main__":
    import os
    
    conn_string = os.getenv('AZURE_IOT_CONNECTION_STRING')
    manager = DeviceTwinManager(conn_string)
    
    # Ler configurações da cloud
    desired = manager.get_desired_properties()
    
    # Reportar estado atual do device
    reported = {
        "firmware_version": "1.2.0",
        "capacidade_maxima": 500,
        "status": "operacional",
        "ultima_manutencao": "2024-12-20",
        "temperatura_sensor": 42.5
    }
    
    manager.update_reported_properties(reported)
    
    # Ver twin completo
    manager.get_full_twin()
```

### Configurar via Azure Portal

1. IoT Hub → Devices → estacao-1 → Device Twin
2. Adicionar desired properties:

```json
{
  "desired": {
    "frequencia_envio": 60,
    "modo_producao": "alta_velocidade",
    "threshold_alerta_defeitos": 10,
    "threshold_paragem": 600
  }
}
```

3. No simulador, ler estas configs e ajustar comportamento:

```python
desired = manager.get_desired_properties()
frequencia = desired.get('frequencia_envio', 60)
threshold_defeitos = desired.get('threshold_alerta_defeitos', 10)

# Usar nas simulações
publisher.simulate_production(interval=frequencia)
```

---

## Direct Methods (Comandos Remotos)

### Executar Comandos da Cloud

```python
# direct_methods_handler.py

from azure.iot.device import IoTHubDeviceClient, MethodResponse
import json
import time

class CommandHandler:
    def __init__(self, connection_string):
        self.client = IoTHubDeviceClient.create_from_connection_string(
            connection_string
        )
        self.producao_ativa = True
        self.frequencia = 60
        
        # Registar handler de métodos
        self.client.on_method_request_received = self.method_request_handler
    
    def method_request_handler(self, method_request):
        """Handler para processar comandos da cloud"""
        print(f"\n📥 Comando recebido: {method_request.name}")
        print(f"Payload: {method_request.payload}")
        
        # Processar comando
        if method_request.name == "parar_producao":
            response = self._parar_producao()
            
        elif method_request.name == "iniciar_producao":
            response = self._iniciar_producao()
            
        elif method_request.name == "ajustar_frequencia":
            frequencia = method_request.payload.get("frequencia", 60)
            response = self._ajustar_frequencia(frequencia)
            
        elif method_request.name == "obter_status":
            response = self._obter_status()
            
        elif method_request.name == "resetar_contadores":
            response = self._resetar_contadores()
            
        else:
            response = {
                "result": f"Comando desconhecido: {method_request.name}",
                "status": 404
            }
        
        # Enviar resposta
        method_response = MethodResponse.create_from_method_request(
            method_request,
            status=response["status"],
            payload=response
        )
        
        self.client.send_method_response(method_response)
        print(f"✓ Resposta enviada: {response['result']}\n")
    
    def _parar_producao(self):
        self.producao_ativa = False
        return {
            "result": "Produção parada com sucesso",
            "status": 200,
            "producao_ativa": False
        }
    
    def _iniciar_producao(self):
        self.producao_ativa = True
        return {
            "result": "Produção iniciada com sucesso",
            "status": 200,
            "producao_ativa": True
        }
    
    def _ajustar_frequencia(self, nova_freq):
        self.frequencia = nova_freq
        return {
            "result": f"Frequência ajustada para {nova_freq} segundos",
            "status": 200,
            "frequencia": nova_freq
        }
    
    def _obter_status(self):
        return {
            "result": "Status obtido",
            "status": 200,
            "producao_ativa": self.producao_ativa,
            "frequencia": self.frequencia,
            "timestamp": time.time()
        }
    
    def _resetar_contadores(self):
        # Lógica para resetar contadores
        return {
            "result": "Contadores resetados",
            "status": 200
        }
    
    def start_listening(self):
        """Iniciar escuta de comandos"""
        self.client.connect()
        print("✓ Conectado ao Azure IoT Hub")
        print("👂 Aguardando comandos da cloud...\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n■ Parando escuta de comandos")
            self.client.disconnect()


# Executar
if __name__ == "__main__":
    import os
    
    conn_string = os.getenv('AZURE_IOT_CONNECTION_STRING')
    handler = CommandHandler(conn_string)
    handler.start_listening()
```

### Invocar Comando via Azure CLI

```bash
# Parar produção
az iot hub invoke-device-method \
  --hub-name producao-industrial-hub \
  --device-id estacao-1 \
  --method-name parar_producao

# Ajustar frequência
az iot hub invoke-device-method \
  --hub-name producao-industrial-hub \
  --device-id estacao-1 \
  --method-name ajustar_frequencia \
  --method-payload '{"frequencia": 30}'

# Obter status
az iot hub invoke-device-method \
  --hub-name producao-industrial-hub \
  --device-id estacao-1 \
  --method-name obter_status
```

---

## Monitorização de Mensagens

### Ver Telemetria em Tempo Real

```bash
# Azure CLI - Monitorizar mensagens
az iot hub monitor-events \
  --hub-name producao-industrial-hub \
  --device-id estacao-1

# Ou para todos os devices
az iot hub monitor-events \
  --hub-name producao-industrial-hub
```

### Azure IoT Explorer (GUI)

1. Instalar: [Azure IoT Explorer](https://github.com/Azure/azure-iot-explorer/releases)
2. Conectar ao IoT Hub
3. Selecionar device
4. Tab "Telemetry" → Start
5. Visualizar mensagens em tempo real

---

## Processamento na Cloud

### Azure Stream Analytics

**Input**: Azure IoT Hub  
**Output**: Azure SQL Database / Blob Storage / Power BI

**Query SQL**:
```sql
-- Calcular médias por estação (janela de 5 minutos)
SELECT
    estacao,
    System.Timestamp() AS window_end,
    AVG(dados.producao) AS producao_media,
    AVG(dados.stock) AS stock_medio,
    SUM(dados.defeitos) AS total_defeitos,
    AVG(dados.paragem) AS paragem_media
INTO
    [output-sql]
FROM
    [input-iothub]
TIMESTAMP BY timestamp
GROUP BY
    estacao,
    TumblingWindow(minute, 5)

-- Alertas de defeitos altos
SELECT
    estacao,
    dados.defeitos AS defeitos,
    timestamp
INTO
    [output-alerts]
FROM
    [input-iothub]
WHERE
    dados.defeitos > 10
```

### Armazenar em Azure SQL

**Tabela**:
```sql
CREATE TABLE TelemetriaProducao (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    EstacaoId INT,
    Timestamp DATETIME2,
    Producao INT,
    Stock INT,
    Paragem INT,
    Defeitos INT,
    ReceivedAt DATETIME2 DEFAULT GETUTCDATE()
);

CREATE INDEX idx_estacao_timestamp 
ON TelemetriaProducao(EstacaoId, Timestamp DESC);
```

---

## Segurança

### Boas Práticas

1. **Não hardcodar connection strings** - Usar variáveis de ambiente
2. **Rotação de chaves** - Regenerar Shared Access Keys periodicamente
3. **Usar X.509 Certificates** em produção (em vez de Symmetric Keys)
4. **Implementar Device Provisioning Service (DPS)** para escala

### Connection String em Variável de Ambiente

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Ler .env

CONN_STRING = os.getenv('AZURE_IOT_CONNECTION_STRING')

if not CONN_STRING:
    raise ValueError("AZURE_IOT_CONNECTION_STRING não definida")
```

**.env** (não commitar no Git):
```
AZURE_IOT_CONNECTION_STRING=HostName=...
```

**.gitignore**:
```
.env
*.pyc
```

---

## Casos de Uso

### 1. Multi-Site Monitoring

Centralizar dados de múltiplas fábricas:
```
Fábrica Lisboa → Azure IoT Hub
Fábrica Porto → Azure IoT Hub → Análise → Dashboard Power BI
Fábrica Braga → Azure IoT Hub
```

### 2. Backup na Cloud

- Dados locais (SQLite) para operação imediata
- Dados na cloud (Azure SQL) para histórico e análise

### 3. Machine Learning

- Azure Stream Analytics → Azure ML
- Prever falhas de equipamento
- Otimizar schedules de produção

### 4. Alertas Avançados

- Logic Apps triggam emails/SMS em defeitos altos
- Integração com Microsoft Teams
- Webhooks para sistemas externos

---

## Custos Azure IoT Hub

| Tier | Mensagens/dia | Preço/mês | Casos de Uso |
|------|---------------|-----------|--------------|
| **F1 (Free)** | 8.000 | €0 | Desenvolvimento/Testes |
| **S1 (Standard)** | 400.000 | ~€21 | Produção pequena |
| **S2** | 6M | ~€630 | Produção média |
| **S3** | 300M | ~€6.300 | Enterprise |

**Cálculo**:
- 3 estações × 1 msg/min × 60 min × 24h = **4.320 msgs/dia**
- Cabe no **F1 gratuito** ou **S1** com folga

---

## Troubleshooting

**Erro de autenticação**:
- Verificar connection string correta
- Confirmar device está registado no IoT Hub
- Regenerar chave se necessário

**Mensagens não chegam**:
- Verificar se device está conectado
- Monitorizar com `az iot hub monitor-events`
- Verificar quotas do tier F1 (8k msgs/dia)

**Timeout de conexão**:
- Verificar firewall/proxy
- Porta 8883 (MQTT) ou 443 (HTTPS) aberta
- Testar conectividade: `telnet producao-industrial-hub.azure-devices.net 8883`

---

## Próximos Passos

1. **Implementar retry logic** para reconexões
2. **Batch messages** para otimizar quotas
3. **Migrar para X.509 certificates** (mais seguro)
4. **Implementar Device Provisioning Service** para auto-registro
5. **Criar dashboards no Power BI** conectados ao Azure SQL

---

## Recursos

- [Azure IoT Hub Docs](https://docs.microsoft.com/azure/iot-hub/)
- [Python SDK Reference](https://github.com/Azure/azure-iot-sdk-python)
- [Azure IoT Explorer](https://github.com/Azure/azure-iot-explorer)
- [Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)

---

Esta integração adiciona capacidades enterprise ao ProjetoISIv1, permitindo escalar de um protótipo local para uma solução cloud-ready com monitorização centralizada e análise avançada.