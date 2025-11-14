# Azure IoT Hub Client

This module provides a Python client for connecting devices to Azure IoT Hub using the `azure-iot-device` SDK.

## Features

- Async/await support for all operations
- Send telemetry data to IoT Hub
- Receive cloud-to-device messages
- Device Twin support (read and update reported properties)
- Direct Methods handling
- Pydantic-based configuration validation
- Comprehensive error handling and logging

## Dependencies

The module requires the following packages (all included in `requirements.txt`):

- `azure-iot-device==2.14.0` - Azure IoT Device SDK
- `paho-mqtt==1.6.1` - MQTT client (required by azure-iot-device)
- `pydantic==2.12.0` - Configuration validation

### Important: paho-mqtt Version Compatibility

**Note:** `paho-mqtt` has been downgraded from 2.1.0 to 1.6.1 because `azure-iot-device` 2.14.0 requires `paho-mqtt>=1.6.1,<2.0.0`. This is a known compatibility issue with the Azure IoT SDK.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Getting Your Connection String

1. Go to Azure Portal (portal.azure.com)
2. Navigate to your IoT Hub
3. Go to "Devices" under "Device management"
4. Select your device or create a new one
5. Copy the "Primary Connection String"

### Setting the Connection String

Set the `AZURE_IOT_CONNECTION_STRING` environment variable:

**Linux/macOS:**
```bash
export AZURE_IOT_CONNECTION_STRING="HostName=your-hub.azure-devices.net;DeviceId=your-device;SharedAccessKey=your-key"
```

**Windows (Command Prompt):**
```cmd
set AZURE_IOT_CONNECTION_STRING="HostName=your-hub.azure-devices.net;DeviceId=your-device;SharedAccessKey=your-key"
```

**Windows (PowerShell):**
```powershell
$env:AZURE_IOT_CONNECTION_STRING="HostName=your-hub.azure-devices.net;DeviceId=your-device;SharedAccessKey=your-key"
```

## Usage Examples

### 1. Simple Telemetry

Send sensor data to Azure IoT Hub:

```bash
python example_simple_telemetry.py
```

This example sends 10 telemetry messages with temperature, humidity, and pressure data.

### 2. Device Twin

Work with device twin reported properties:

```bash
python example_device_twin.py
```

This example:
- Retrieves the current device twin
- Updates reported properties (firmware version, location, status)
- Displays the updated twin

### 3. Direct Methods

Handle direct method calls from Azure IoT Hub:

```bash
python example_direct_methods.py
```

This example registers handlers for:
- `reboot` - Simulates a device reboot
- `get_status` - Returns device status information
- `update_config` - Updates device configuration

**Invoking methods from Azure CLI:**

```bash
# Reboot method
az iot hub invoke-device-method \
  --device-id <your-device-id> \
  --hub-name <your-hub-name> \
  --method-name reboot \
  --method-payload '{"delay": 5}'

# Get status
az iot hub invoke-device-method \
  --device-id <your-device-id> \
  --hub-name <your-hub-name> \
  --method-name get_status

# Update config
az iot hub invoke-device-method \
  --device-id <your-device-id> \
  --hub-name <your-hub-name> \
  --method-name update_config \
  --method-payload '{"telemetry_interval": 30, "log_level": "debug"}'
```

## Custom Implementation

### Basic Usage

```python
import asyncio
from iot_client import AzureIoTClient, AzureIoTConfig

async def main():
    # Create configuration
    config = AzureIoTConfig(
        connection_string="your-connection-string"
    )

    # Create client
    client = AzureIoTClient(config)

    # Connect
    await client.connect()

    # Send telemetry
    await client.send_telemetry({
        "temperature": 25.5,
        "humidity": 60
    })

    # Disconnect
    await client.disconnect()

asyncio.run(main())
```

### Advanced: With Device Twin and Methods

```python
import asyncio
from iot_client import AzureIoTClient, AzureIoTConfig

def handle_custom_method(payload):
    """Handle custom direct method."""
    print(f"Custom method called with: {payload}")
    return {"status": "success", "result": "processed"}

async def main():
    config = AzureIoTConfig(
        connection_string="your-connection-string"
    )

    client = AzureIoTClient(config)
    await client.connect()

    # Register method handler
    client.register_method_handler("custom_method", handle_custom_method)
    await client.setup_method_handlers()

    # Update device twin
    await client.update_twin_reported_properties({
        "firmware": "2.0.0",
        "location": "datacenter-1"
    })

    # Send telemetry
    await client.send_telemetry({"metric": 100})

    # Keep running for methods
    await asyncio.sleep(3600)

    await client.disconnect()

asyncio.run(main())
```

## Error Handling

The client includes comprehensive error handling:

```python
from iot_client import AzureIoTClient, AzureIoTConfig
from pydantic import ValidationError

try:
    # Invalid connection string will raise ValidationError
    config = AzureIoTConfig(connection_string="invalid")
except ValidationError as e:
    print(f"Configuration error: {e}")

try:
    client = AzureIoTClient(config)
    await client.connect()
except Exception as e:
    print(f"Connection error: {e}")
```

## Monitoring Telemetry

You can monitor telemetry in Azure Portal or using Azure CLI:

```bash
# Monitor device-to-cloud messages
az iot hub monitor-events \
  --hub-name <your-hub-name> \
  --device-id <your-device-id>

# Monitor all devices
az iot hub monitor-events \
  --hub-name <your-hub-name>
```

## Troubleshooting

### Connection Issues

1. **Invalid connection string**: Verify your connection string contains `HostName`, `DeviceId`, and `SharedAccessKey`
2. **Network issues**: Check firewall and network connectivity to Azure
3. **Certificate errors**: Ensure system time is correct

### Dependency Conflicts

If you encounter issues with `paho-mqtt`:

```bash
# Ensure correct version is installed
pip uninstall paho-mqtt
pip install paho-mqtt==1.6.1

# Verify installation
pip list | grep paho-mqtt
```

### Logging

Enable verbose logging for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Additional Resources

- [Azure IoT Hub Documentation](https://docs.microsoft.com/azure/iot-hub/)
- [Azure IoT Device SDK for Python](https://github.com/Azure/azure-iot-sdk-python)
- [IoT Hub MQTT Support](https://docs.microsoft.com/azure/iot-hub/iot-hub-mqtt-support)
- [Device Twins](https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-device-twins)
- [Direct Methods](https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-direct-methods)

## License

See the main project LICENSE file.
