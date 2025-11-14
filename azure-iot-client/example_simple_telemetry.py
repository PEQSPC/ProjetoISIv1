"""
Simple Telemetry Example

This example demonstrates basic telemetry sending to Azure IoT Hub.

Usage:
    python example_simple_telemetry.py

Environment Variables Required:
    AZURE_IOT_CONNECTION_STRING: Your device connection string from Azure IoT Hub
"""

import asyncio
import os
import sys
from datetime import datetime
from iot_client import AzureIoTClient, AzureIoTConfig


async def main():
    """Send simple telemetry to Azure IoT Hub."""

    # Get connection string from environment variable
    connection_string = os.getenv("AZURE_IOT_CONNECTION_STRING")

    if not connection_string:
        print("ERROR: AZURE_IOT_CONNECTION_STRING environment variable not set")
        print("\nTo set it:")
        print('  Linux/Mac: export AZURE_IOT_CONNECTION_STRING="your-connection-string"')
        print('  Windows:   set AZURE_IOT_CONNECTION_STRING="your-connection-string"')
        sys.exit(1)

    # Create configuration with Pydantic validation
    try:
        config = AzureIoTConfig(connection_string=connection_string)
    except Exception as e:
        print(f"ERROR: Invalid configuration: {e}")
        sys.exit(1)

    # Create client
    client = AzureIoTClient(config)

    try:
        # Connect to Azure IoT Hub
        print("Connecting to Azure IoT Hub...")
        await client.connect()
        print("Connected successfully!")

        # Send telemetry messages
        for i in range(10):
            # Create telemetry data
            telemetry_data = {
                "temperature": 20 + (i * 0.5),
                "humidity": 60 + (i * 2),
                "pressure": 1013.25 + (i * 0.1),
                "message_id": i
            }

            # Optional: Add custom properties
            properties = {
                "alert": "true" if telemetry_data["temperature"] > 23 else "false"
            }

            # Send telemetry
            print(f"\nSending telemetry #{i + 1}: {telemetry_data}")
            await client.send_telemetry(telemetry_data, properties)

            # Wait 2 seconds between messages
            await asyncio.sleep(2)

        print("\nAll telemetry sent successfully!")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    finally:
        # Disconnect
        print("\nDisconnecting...")
        await client.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
