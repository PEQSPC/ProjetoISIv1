"""
Direct Methods Example

This example demonstrates handling direct methods from Azure IoT Hub.

Usage:
    python example_direct_methods.py

Environment Variables Required:
    AZURE_IOT_CONNECTION_STRING: Your device connection string from Azure IoT Hub

After running, invoke methods from Azure Portal or CLI:
    az iot hub invoke-device-method --device-id <device-id> --hub-name <hub-name> \\
        --method-name reboot --method-payload '{"delay": 5}'
"""

import asyncio
import os
import sys
from typing import Any, Dict
from iot_client import AzureIoTClient, AzureIoTConfig


def handle_reboot(payload: Any) -> Dict[str, Any]:
    """
    Handle reboot direct method.

    Args:
        payload: Method payload from IoT Hub

    Returns:
        Response dictionary
    """
    print(f"\n[REBOOT] Method invoked with payload: {payload}")

    delay = payload.get("delay", 0) if isinstance(payload, dict) else 0

    print(f"[REBOOT] Simulating reboot with {delay}s delay...")
    # In a real scenario, you would trigger an actual device reboot here

    return {
        "status": "success",
        "message": f"Reboot scheduled with {delay}s delay"
    }


def handle_get_status(payload: Any) -> Dict[str, Any]:
    """
    Handle get_status direct method.

    Args:
        payload: Method payload from IoT Hub

    Returns:
        Response dictionary with device status
    """
    print(f"\n[GET_STATUS] Method invoked")

    return {
        "status": "success",
        "device_status": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 34.1,
            "uptime_hours": 72.5,
            "temperature": 42.0
        }
    }


def handle_update_config(payload: Any) -> Dict[str, Any]:
    """
    Handle update_config direct method.

    Args:
        payload: Method payload containing configuration updates

    Returns:
        Response dictionary
    """
    print(f"\n[UPDATE_CONFIG] Method invoked with payload: {payload}")

    if not isinstance(payload, dict):
        return {
            "status": "error",
            "message": "Invalid payload format. Expected dictionary."
        }

    # Simulate configuration update
    print(f"[UPDATE_CONFIG] Updating configuration: {payload}")

    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "updated_fields": list(payload.keys())
    }


async def main():
    """Run direct methods example."""

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

        # Register direct method handlers
        print("\nRegistering direct method handlers...")
        client.register_method_handler("reboot", handle_reboot)
        client.register_method_handler("get_status", handle_get_status)
        client.register_method_handler("update_config", handle_update_config)

        # Set up the handlers
        await client.setup_method_handlers()
        print("Method handlers registered successfully!")

        # Keep the client running to receive method calls
        print("\nWaiting for direct method calls...")
        print("Available methods: reboot, get_status, update_config")
        print("Press Ctrl+C to exit")

        # Run indefinitely until interrupted
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

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
