"""
Azure IoT Hub Publisher

This module provides an Azure IoT Hub publisher that mimics the MQTT Publisher
interface but sends telemetry to Azure IoT Hub instead of a traditional MQTT broker.
"""

import asyncio
import json
import threading
import time
from typing import Any

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from settings_classes import BrokerSettings, ClientSettings, DataSettings


class AzurePublisher(threading.Thread):
    """
    Azure IoT Hub Publisher that sends telemetry data to Azure IoT Hub.

    This class maintains the same interface as the MQTT Publisher but uses
    Azure IoT Device SDK instead of paho-mqtt.
    """

    def __init__(
        self,
        broker_settings: BrokerSettings,
        topic_url: str,
        topic_data: list[DataSettings],
        topic_payload_root: dict[str, Any],
        client_settings: ClientSettings,
        is_verbose: bool,
    ):
        threading.Thread.__init__(self)
        # Set as daemon thread to allow clean program exit
        self.daemon = True

        self.broker_settings = broker_settings
        self.topic_url = topic_url  # Will be used as message property "topic"
        self.topic_data = topic_data
        self.topic_payload_root = topic_payload_root
        self.client_settings = client_settings
        self.is_verbose = is_verbose

        self.loop = False
        self.payload: dict[str, Any] | None = None
        self.client: IoTHubDeviceClient | None = None
        self.event_loop: asyncio.AbstractEventLoop | None = None

    def create_client(self) -> IoTHubDeviceClient:
        """Create Azure IoT Hub device client with appropriate settings."""
        if self.broker_settings.azure_model_id:
            client = IoTHubDeviceClient.create_from_connection_string(
                self.broker_settings.azure_connection_string,
                product_info=self.broker_settings.azure_model_id
            )
        else:
            client = IoTHubDeviceClient.create_from_connection_string(
                self.broker_settings.azure_connection_string
            )

        # The SDK handles reconnections automatically, but we add our own retry logic
        return client

    async def connect_async(self):
        """Async connection to Azure IoT Hub."""
        self.client = self.create_client()

        # Set up connection status handler to suppress background errors
        def on_connection_state_change():
            pass  # Silently handle connection state changes

        self.client.on_connection_state_change = on_connection_state_change

        await self.client.connect()
        print(f"Connected to Azure IoT Hub for topic: {self.topic_url}")

    async def disconnect_async(self):
        """Async disconnection from Azure IoT Hub."""
        if self.client:
            try:
                await self.client.disconnect()
                print(f"Disconnected from Azure IoT Hub for topic: {self.topic_url}")
            except Exception as e:
                # Ignore errors during disconnect (e.g., if already disconnected)
                pass

    async def send_telemetry_async(self, payload: dict[str, Any]):
        """
        Send telemetry to Azure IoT Hub asynchronously.

        Args:
            payload: Telemetry data to send

        Raises:
            RuntimeError: If client is not connected
            Exception: If message sending fails
        """
        if not self.client:
            raise RuntimeError("Client not connected")

        # Create message with JSON payload
        message = Message(json.dumps(payload))
        message.content_encoding = "utf-8"
        message.content_type = "application/json"

        # Add topic as custom property to maintain compatibility with MQTT structure
        message.custom_properties["topic"] = self.topic_url

        # Send message with timeout
        try:
            await asyncio.wait_for(
                self.client.send_message(message),
                timeout=30.0  # 30 second timeout
            )

            # Log publish event
            on_publish_log = f"[{time.strftime('%H:%M:%S')}] Telemetry sent to Azure IoT Hub: {self.topic_url}"
            if self.is_verbose:
                on_publish_log += f"\n\t[payload] {json.dumps(payload)}"
            print(on_publish_log)

        except asyncio.TimeoutError:
            raise Exception(f"Timeout sending message to Azure IoT Hub for {self.topic_url}")
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")

    async def publish_loop_async(self):
        """Main async publishing loop with reconnection handling."""
        max_retries = 3
        retry_delay = 5

        # Initial connection with retries
        for attempt in range(max_retries):
            try:
                await self.connect_async()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"Failed to connect after {max_retries} attempts: {e}")
                    return

        try:
            while self.loop:
                self.payload = self.generate_payload()
                if self.payload is None:
                    break

                try:
                    await self.send_telemetry_async(self.payload)
                except Exception as e:
                    print(f"Error sending telemetry to {self.topic_url}: {e}")
                    # Try to reconnect on send failure
                    try:
                        print(f"Attempting to reconnect for {self.topic_url}...")
                        await self.disconnect_async()
                        await asyncio.sleep(2)
                        await self.connect_async()
                        print(f"Reconnected successfully for {self.topic_url}")
                    except Exception as reconnect_error:
                        print(f"Reconnection failed for {self.topic_url}: {reconnect_error}")
                        # Continue loop to retry on next iteration

                await asyncio.sleep(self.client_settings.time_interval)

        finally:
            await self.disconnect_async()

    def run(self):
        """
        Thread run method that creates an event loop and runs the async publisher.
        """
        self.loop = True

        # Create new event loop for this thread
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        try:
            # Run the async publish loop
            self.event_loop.run_until_complete(self.publish_loop_async())
        except Exception as e:
            print(f"Error in Azure publisher: {e}")
        finally:
            # Cancel all pending tasks before closing the loop
            try:
                pending = asyncio.all_tasks(self.event_loop)
                for task in pending:
                    task.cancel()
                # Give tasks a chance to cancel
                if pending:
                    self.event_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            finally:
                try:
                    self.event_loop.close()
                except Exception:
                    pass

    def stop(self):
        """Stop the publisher."""
        self.loop = False

    def generate_payload(self) -> dict[str, Any] | None:
        """
        Generate payload from data settings.

        Returns:
            Dictionary with generated data or None if no data is active
        """
        payload: dict[str, Any] = {}
        payload.update(self.topic_payload_root)
        has_data_active = False

        for data in self.topic_data:
            if data.get_is_active():
                has_data_active = True
                payload[data.name] = data.generate_value()

        if not has_data_active:
            self.stop()
            return None

        return payload
