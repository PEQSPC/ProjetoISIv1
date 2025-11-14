"""
Device Twin Example

This example demonstrates working with Azure IoT Hub Device Twins.

Usage:
    python example_device_twin.py

Environment Variables Required:
    AZURE_IOT_CONNECTION_STRING: Your device connection string from Azure IoT Hub
"""

import asyncio
import os
import sys
import json
from iot_client import AzureIoTClient, AzureIoTConfig


async def main():
    """Demonstrate device twin operations."""

    # Get connection string from environment variable
    connection_string = os.getenv("AZURE_IOT_CONNECTION_STRING")

    if not connection_string:
        print("ERROR: AZURE_IOT_CONNECTION_STRING environment variable not set")
        sys.exit(1)

    # Create configuration
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

        # Get current device twin
        print("\nRetrieving device twin...")
        twin = await client.get_twin()
        print(f"Current device twin:")
        print(json.dumps(twin, indent=2))

        # Update reported properties
        print("\nUpdating reported properties...")
        reported_properties = {
            "firmware_version": "1.0.0",
            "location": {
                "latitude": 38.7223,
                "longitude": -9.1393,
                "city": "Lisbon"
            },
            "status": "online",
            "last_updated": asyncio.get_event_loop().time()
        }

        await client.update_twin_reported_properties(reported_properties)
        print("Reported properties updated successfully!")

        # Get updated twin
        print("\nRetrieving updated device twin...")
        updated_twin = await client.get_twin()
        print(f"Updated reported properties:")
        print(json.dumps(updated_twin.get("reported", {}), indent=2))

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
