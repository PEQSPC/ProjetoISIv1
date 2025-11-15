# Azure IoT Hub - Multiple Device Connections

## Overview

When using Azure IoT Hub, each device ID can only have **ONE active connection** at a time. If you try to use the same device ID for multiple publishers, you'll get `ConnectionDroppedError` because Azure disconnects the previous connection when a new one is established.

## The Solution: Multiple Device IDs

Use the `AZURE_DEVICE_CONNECTIONS` configuration to map each topic to its own unique device ID.

## Configuration Format

### Option 1: Multiple Devices (Recommended for multiple topics)

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_DEVICE_CONNECTIONS": {
    "linha_producao/estacao/1": "HostName=iothub-ipca.azure-devices.net;DeviceId=estacao1;SharedAccessKey=...",
    "linha_producao/estacao/2": "HostName=iothub-ipca.azure-devices.net;DeviceId=estacao2;SharedAccessKey=...",
    "linha_producao/estacao/3": "HostName=iothub-ipca.azure-devices.net;DeviceId=estacao3;SharedAccessKey=..."
  },
  "TOPICS": [
    {
      "TYPE": "multiple",
      "PREFIX": "linha_producao/estacao",
      "RANGE_START": 1,
      "RANGE_END": 3,
      ...
    }
  ]
}
```

### Option 2: Single Device (Backwards compatible, only for single topic)

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_CONNECTION_STRING": "HostName=iothub-ipca.azure-devices.net;DeviceId=device1;SharedAccessKey=...",
  "TOPICS": [
    {
      "TYPE": "single",
      "NAME": "factory/sensor1",
      ...
    }
  ]
}
```

## Setting Up Multiple Devices in Azure IoT Hub

### Step 1: Create Devices in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your IoT Hub
3. Go to **Devices** under "Device management"
4. Click **+ Add Device**
5. Create each device:
   - Device ID: `estacao1`
   - Authentication: Symmetric key (auto-generate)
   - Click **Save**
6. Repeat for `estacao2`, `estacao3`, etc.

### Step 2: Get Connection Strings

For each device:
1. Click on the device name
2. Copy the **Primary Connection String**
3. It will look like:
   ```
   HostName=iothub-ipca.azure-devices.net;DeviceId=estacao1;SharedAccessKey=abc123...
   ```

### Step 3: Update Configuration

Update `settings_azure.json` with your connection strings:

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_DEVICE_CONNECTIONS": {
    "linha_producao/estacao/1": "HostName=iothub-ipca.azure-devices.net;DeviceId=estacao1;SharedAccessKey=YOUR_KEY_1",
    "linha_producao/estacao/2": "HostName=iothub-ipca.azure-devices.net;DeviceId=estacao2;SharedAccessKey=YOUR_KEY_2",
    "linha_producao/estacao/3": "HostName=iothub-ipca.azure-devices.net;DeviceId=estacao3;SharedAccessKey=YOUR_KEY_3"
  },
  "TOPICS": [...]
}
```

## Using Azure CLI

You can also create devices and get connection strings using Azure CLI:

### Create Devices

```bash
# Create device
az iot hub device-identity create --hub-name iothub-ipca --device-id estacao1

# Get connection string
az iot hub device-identity connection-string show --hub-name iothub-ipca --device-id estacao1
```

### Create Multiple Devices (Bash script)

```bash
#!/bin/bash
HUB_NAME="iothub-ipca"

for i in {1..3}; do
  DEVICE_ID="estacao$i"
  echo "Creating device: $DEVICE_ID"
  az iot hub device-identity create --hub-name $HUB_NAME --device-id $DEVICE_ID

  echo "Connection string for $DEVICE_ID:"
  az iot hub device-identity connection-string show --hub-name $HUB_NAME --device-id $DEVICE_ID --output tsv
  echo ""
done
```

### Create Multiple Devices (PowerShell script)

```powershell
$HubName = "iothub-ipca"

1..3 | ForEach-Object {
    $DeviceId = "estacao$_"
    Write-Host "Creating device: $DeviceId"
    az iot hub device-identity create --hub-name $HubName --device-id $DeviceId

    Write-Host "Connection string for ${DeviceId}:"
    az iot hub device-identity connection-string show --hub-name $HubName --device-id $DeviceId --output tsv
    Write-Host ""
}
```

## Topic to Device Mapping

The system automatically maps topics to devices based on the exact topic URL:

| Topic URL | Device ID | Connection String Used |
|-----------|-----------|------------------------|
| `linha_producao/estacao/1` | `estacao1` | `AZURE_DEVICE_CONNECTIONS["linha_producao/estacao/1"]` |
| `linha_producao/estacao/2` | `estacao2` | `AZURE_DEVICE_CONNECTIONS["linha_producao/estacao/2"]` |
| `linha_producao/estacao/3` | `estacao3` | `AZURE_DEVICE_CONNECTIONS["linha_producao/estacao/3"]` |

**Important**: The topic URL must **exactly match** the key in `AZURE_DEVICE_CONNECTIONS`.

## Running the Simulator

```bash
cd mqtt-simulator-master/mqtt-simulator
python main.py -f ../config/settings_azure_multiple_devices.json -v
```

**Expected output:**
```
Using Azure IoT Hub publisher with 3 device connections
Starting: linha_producao/estacao/1 ...
Starting: linha_producao/estacao/2 ...
Starting: linha_producao/estacao/3 ...
Connected to Azure IoT Hub for topic: linha_producao/estacao/1
Connected to Azure IoT Hub for topic: linha_producao/estacao/2
Connected to Azure IoT Hub for topic: linha_producao/estacao/3
[12:30:45] Telemetry sent to Azure IoT Hub: linha_producao/estacao/1
[12:30:45] Telemetry sent to Azure IoT Hub: linha_producao/estacao/2
[12:30:45] Telemetry sent to Azure IoT Hub: linha_producao/estacao/3
```

## Monitoring

Monitor telemetry from all devices:

```bash
# All devices
az iot hub monitor-events --hub-name iothub-ipca

# Specific device
az iot hub monitor-events --hub-name iothub-ipca --device-id estacao1
```

## Industrial Factory Example

For the industrial factory simulation with multiple production areas:

```json
{
  "BROKER_TYPE": "azure",
  "AZURE_DEVICE_CONNECTIONS": {
    "factory/rawmaterial/intake": "HostName=...;DeviceId=rawmaterial;SharedAccessKey=...",
    "factory/production/line/1": "HostName=...;DeviceId=production-line1;SharedAccessKey=...",
    "factory/production/line/2": "HostName=...;DeviceId=production-line2;SharedAccessKey=...",
    "factory/production/line/3": "HostName=...;DeviceId=production-line3;SharedAccessKey=...",
    "factory/assembly/station/1": "HostName=...;DeviceId=assembly-st1;SharedAccessKey=...",
    "factory/assembly/station/2": "HostName=...;DeviceId=assembly-st2;SharedAccessKey=...",
    "factory/assembly/station/3": "HostName=...;DeviceId=assembly-st3;SharedAccessKey=...",
    "factory/assembly/station/4": "HostName=...;DeviceId=assembly-st4;SharedAccessKey=...",
    "factory/assembly/station/5": "HostName=...;DeviceId=assembly-st5;SharedAccessKey=...",
    "factory/quality/inspection/1": "HostName=...;DeviceId=quality-insp1;SharedAccessKey=...",
    "factory/quality/inspection/2": "HostName=...;DeviceId=quality-insp2;SharedAccessKey=...",
    "factory/packaging/line1": "HostName=...;DeviceId=packaging;SharedAccessKey=...",
    "factory/warehouse/storage": "HostName=...;DeviceId=warehouse;SharedAccessKey=...",
    "factory/energy/monitoring": "HostName=...;DeviceId=energy;SharedAccessKey=...",
    "factory/hvac/system": "HostName=...;DeviceId=hvac;SharedAccessKey=...",
    "factory/maintenance/alerts": "HostName=...;DeviceId=maintenance;SharedAccessKey=..."
  },
  "TOPICS": [...]
}
```

## Troubleshooting

### Error: "No Azure connection string found for topic"

**Problem**: The topic URL doesn't match any key in `AZURE_DEVICE_CONNECTIONS`.

**Solution**: Ensure the topic URL exactly matches:
- Check for trailing slashes
- Verify the PREFIX and RANGE generate the correct topic names
- Use `-v` verbose mode to see exact topic URLs being used

### Error: "ConnectionDroppedError: Unexpected disconnection"

**Problem**: Multiple publishers trying to use the same device ID.

**Solution**:
1. Verify each topic has its own unique device ID
2. Check you're not running multiple instances of the simulator
3. Ensure no other applications are using the same device IDs

### Error: "Either AZURE_CONNECTION_STRING or AZURE_DEVICE_CONNECTIONS is required"

**Problem**: No Azure connection configuration provided.

**Solution**: Add either:
- `AZURE_DEVICE_CONNECTIONS` (for multiple devices), or
- `AZURE_CONNECTION_STRING` (for single device)

## Best Practices

1. **Use descriptive device IDs**: `production-line1`, not `device1`
2. **Organize by function**: Group related devices logically
3. **Document mappings**: Keep a reference of which device ID maps to which physical sensor/line
4. **Security**: Never commit connection strings to Git - use environment variables or Azure Key Vault in production
5. **Testing**: Test with a single device first, then scale up

## Cost Considerations

- **Azure IoT Hub Free Tier**: 8,000 messages/day, up to 500 devices
- **Standard Tier**: Charged per message, unlimited devices
- Consider your message frequency × number of devices to estimate costs
- Example: 3 devices × 100 messages/day = 300 messages/day (within free tier)

## See Also

- [README_AZURE_INTEGRATION.md](../README_AZURE_INTEGRATION.md) - Main Azure integration guide
- [README_INDUSTRIAL_FACTORY.md](README_INDUSTRIAL_FACTORY.md) - Industrial factory simulation
- [Azure IoT Hub Pricing](https://azure.microsoft.com/pricing/details/iot-hub/)
- [Azure IoT Hub Documentation](https://docs.microsoft.com/azure/iot-hub/)
