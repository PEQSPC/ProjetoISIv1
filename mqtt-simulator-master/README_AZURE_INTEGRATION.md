# Azure IoT Hub Integration for MQTT Simulator

This document explains how to use the MQTT Simulator with Azure IoT Hub integration.

## Overview

The MQTT Simulator now supports two broker types:
- **MQTT** - Traditional MQTT broker (e.g., Mosquitto, localhost)
- **Azure** - Azure IoT Hub using the Azure IoT Device SDK

## Configuration

The broker type is controlled by the `BROKER_TYPE` field in `settings.json`.

### Option 1: MQTT Broker (localhost)

Use `settings.json` or `settings_mqtt_localhost.json`:

```json
{
  "BROKER_TYPE": "mqtt",
  "BROKER_URL": "localhost",
  "BROKER_PORT": 1883,
  "TOPICS": [...]
}
```

**Required fields for MQTT:**
- `BROKER_TYPE`: "mqtt"
- `BROKER_URL`: MQTT broker hostname
- `BROKER_PORT`: MQTT broker port (default: 1883)

### Option 2: Azure IoT Hub

Use `settings_azure.json` and update with your Azure connection string:

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=your-hub.azure-devices.net;DeviceId=your-device;SharedAccessKey=your-key",
  "TOPICS": [...]
}
```

**Required fields for Azure:**
- `BROKER_TYPE`: "azure"
- `AZURE_CONNECTION_STRING`: Your Azure IoT Hub device connection string

**Optional fields:**
- `AZURE_MODEL_ID`: IoT Plug and Play model ID (optional)

## Getting Your Azure Connection String

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your IoT Hub
3. Go to "Devices" under "Device management"
4. Select your device or create a new one
5. Copy the "Primary Connection String"

Example format:
```
HostName=my-iot-hub.azure-devices.net;DeviceId=my-device;SharedAccessKey=abc123...
```

## Usage

### Running with MQTT (localhost)

```bash
cd mqtt-simulator-master/mqtt-simulator
python main.py -f ../config/settings.json
```

or explicitly:

```bash
python main.py -f ../config/settings_mqtt_localhost.json
```

### Running with Azure IoT Hub

1. **First, update the connection string** in `config/settings_azure.json`:
   ```json
   {
     "BROKER_TYPE": "azure",
     "AZURE_CONNECTION_STRING": "HostName=YOUR-HUB.azure-devices.net;DeviceId=YOUR-DEVICE;SharedAccessKey=YOUR-KEY",
     ...
   }
   ```

2. **Run the simulator:**
   ```bash
   python main.py -f ../config/settings_azure.json
   ```

### Verbose Mode

Enable verbose output to see detailed telemetry payloads:

```bash
python main.py -f ../config/settings_azure.json -v
```

## How It Works

### MQTT Mode
- Uses `paho-mqtt` library (version 1.6.1)
- Creates `Publisher` instances
- Publishes to traditional MQTT topics
- Supports TLS and authentication

### Azure Mode
- Uses `azure-iot-device` library (version 2.14.0)
- Creates `AzurePublisher` instances
- Sends telemetry to Azure IoT Hub
- Topic names are included as message properties
- Automatic JSON encoding with UTF-8

## Topic Mapping

When using Azure IoT Hub, the MQTT topic structure is preserved:

**MQTT topic:**
```
linha_producao/estacao1
```

**Azure IoT Hub:**
- Sent as telemetry with custom property `topic=linha_producao/estacao1`
- Payload remains the same JSON structure

## Example Output

### MQTT Mode
```
Using MQTT publisher (broker: localhost:1883)
Starting: linha_producao/estacao1 ...
Starting: linha_producao/estacao2 ...
Starting: linha_producao/estacao3 ...
[12:30:45] Data published on: linha_producao/estacao1
```

### Azure Mode
```
Using Azure IoT Hub publisher (connection: HostName=my-hub.azure-devices.net;DeviceId=...)
Starting: linha_producao/estacao1 ...
Starting: linha_producao/estacao2 ...
Starting: linha_producao/estacao3 ...
Connected to Azure IoT Hub for topic: linha_producao/estacao1
[12:30:45] Telemetry sent to Azure IoT Hub: linha_producao/estacao1
```

## Monitoring Telemetry in Azure

### Using Azure Portal
1. Go to your IoT Hub in Azure Portal
2. Navigate to "Overview"
3. View "Device to cloud messages" metric

### Using Azure CLI

Monitor all telemetry:
```bash
az iot hub monitor-events --hub-name YOUR-HUB-NAME
```

Monitor specific device:
```bash
az iot hub monitor-events --hub-name YOUR-HUB-NAME --device-id YOUR-DEVICE-ID
```

### Example Telemetry Message

```json
{
  "producao": 65,
  "paragem": 12,
  "stock": 78,
  "defeitos": 2
}
```

With message properties:
```
topic: linha_producao/estacao1
contentType: application/json
contentEncoding: utf-8
```

## Dependencies

### For MQTT Mode
- `paho-mqtt==1.6.1`

### For Azure Mode
- `azure-iot-device==2.14.0`
- `paho-mqtt==1.6.1` (required by azure-iot-device)

### Common Dependencies
- `pydantic==2.12.0` (configuration validation)

**Important:** `paho-mqtt` must be version 1.6.1 (not 2.x) due to Azure IoT SDK compatibility requirements.

Install all dependencies:
```bash
pip install -r ../../requirements.txt
```

## Configuration Reference

### Complete Azure Configuration Example

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=production-hub.azure-devices.net;DeviceId=factory-sensor-01;SharedAccessKey=abc123...",
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

## Switching Between MQTT and Azure

Simply change the `BROKER_TYPE` in your settings file:

**To switch to MQTT:**
```json
{
  "BROKER_TYPE": "mqtt",
  "BROKER_URL": "localhost",
  "BROKER_PORT": 1883,
  ...
}
```

**To switch to Azure:**
```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=...",
  ...
}
```

## Troubleshooting

### Azure Connection Errors

**Error:** "AZURE_CONNECTION_STRING is required when BROKER_TYPE is 'azure'"
- **Solution:** Add a valid `AZURE_CONNECTION_STRING` to your settings file

**Error:** "Invalid connection string format"
- **Solution:** Ensure your connection string contains `HostName`, `DeviceId`, and `SharedAccessKey`

### Dependency Conflicts

**Error:** Package version conflicts with paho-mqtt
- **Solution:** Ensure `paho-mqtt==1.6.1` is installed (not 2.x)
  ```bash
  pip uninstall paho-mqtt
  pip install paho-mqtt==1.6.1
  ```

### Connection Issues

**Azure:** Check network connectivity to Azure
```bash
ping your-hub-name.azure-devices.net
```

**MQTT:** Ensure your MQTT broker is running
```bash
# For localhost Mosquitto
mosquitto -v
```

## Architecture

The integration uses a factory pattern to select the appropriate publisher:

```
settings.json → BrokerSettings.is_azure_enabled()
                       ↓
              ┌────────┴────────┐
              │                 │
       MQTT Mode          Azure Mode
              │                 │
        Publisher        AzurePublisher
              │                 │
      paho-mqtt.client   azure-iot-device
```

Both publisher types implement the same interface, making them interchangeable.

## Support

For issues or questions:
- MQTT Simulator: Check the main project README
- Azure IoT Hub: [Azure IoT Documentation](https://docs.microsoft.com/azure/iot-hub/)
- Azure SDK: [GitHub Issues](https://github.com/Azure/azure-iot-sdk-python/issues)
