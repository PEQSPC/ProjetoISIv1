"""
Azure IoT Hub Device Client

This module provides a wrapper for Azure IoT Hub device connectivity with
support for telemetry, device twin, and direct methods.

Dependencies:
- azure-iot-device==2.14.0
- paho-mqtt==1.6.1 (required by azure-iot-device)
- pydantic==2.12.0 (for configuration validation)
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message, MethodResponse
from pydantic import BaseModel, Field, validator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureIoTConfig(BaseModel):
    """Configuration model for Azure IoT Hub connection with Pydantic validation."""

    connection_string: str = Field(
        ...,
        description="Azure IoT Hub device connection string"
    )
    model_id: Optional[str] = Field(
        None,
        description="Optional IoT Plug and Play model ID"
    )

    @validator('connection_string')
    def validate_connection_string(cls, v):
        """Validate connection string format."""
        required_parts = ['HostName=', 'DeviceId=', 'SharedAccessKey=']
        if not all(part in v for part in required_parts):
            raise ValueError(
                "Invalid connection string format. Must contain HostName, "
                "DeviceId, and SharedAccessKey"
            )
        return v


class AzureIoTClient:
    """
    Azure IoT Hub Device Client wrapper with async support.

    Handles connection lifecycle, telemetry sending, device twin updates,
    and direct method handling.
    """

    def __init__(self, config: AzureIoTConfig):
        """
        Initialize the Azure IoT client.

        Args:
            config: AzureIoTConfig instance with connection details
        """
        self.config = config
        self.client: Optional[IoTHubDeviceClient] = None
        self._method_handlers: Dict[str, Callable] = {}
        self._is_connected = False

    async def connect(self) -> None:
        """
        Connect to Azure IoT Hub.

        Raises:
            Exception: If connection fails
        """
        try:
            if self.config.model_id:
                self.client = IoTHubDeviceClient.create_from_connection_string(
                    self.config.connection_string,
                    product_info=self.config.model_id
                )
            else:
                self.client = IoTHubDeviceClient.create_from_connection_string(
                    self.config.connection_string
                )

            await self.client.connect()
            self._is_connected = True
            logger.info("Successfully connected to Azure IoT Hub")

        except Exception as e:
            logger.error(f"Failed to connect to Azure IoT Hub: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Azure IoT Hub."""
        if self.client and self._is_connected:
            await self.client.disconnect()
            self._is_connected = False
            logger.info("Disconnected from Azure IoT Hub")

    async def send_telemetry(
        self,
        data: Dict[str, Any],
        properties: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Send telemetry data to Azure IoT Hub.

        Args:
            data: Telemetry data as dictionary
            properties: Optional message properties

        Raises:
            RuntimeError: If client is not connected
        """
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")

        try:
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()

            # Create message
            message = Message(json.dumps(data))
            message.content_encoding = "utf-8"
            message.content_type = "application/json"

            # Add custom properties if provided
            if properties:
                for key, value in properties.items():
                    message.custom_properties[key] = value

            # Send message
            await self.client.send_message(message)
            logger.info(f"Telemetry sent: {data}")

        except Exception as e:
            logger.error(f"Failed to send telemetry: {e}")
            raise

    async def receive_messages(
        self,
        message_handler: Callable[[Message], None]
    ) -> None:
        """
        Receive cloud-to-device messages.

        Args:
            message_handler: Callback function to handle received messages
        """
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")

        try:
            while True:
                message = await self.client.receive_message()
                logger.info(f"Message received: {message.data}")
                message_handler(message)

        except asyncio.CancelledError:
            logger.info("Message receiving cancelled")
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            raise

    def register_method_handler(
        self,
        method_name: str,
        handler: Callable[[Any], Dict[str, Any]]
    ) -> None:
        """
        Register a handler for a direct method.

        Args:
            method_name: Name of the direct method
            handler: Callback function that processes the method request
        """
        self._method_handlers[method_name] = handler
        logger.info(f"Registered handler for method: {method_name}")

    async def setup_method_handlers(self) -> None:
        """Set up registered direct method handlers."""
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")

        async def method_request_handler(method_request):
            """Generic method request handler."""
            method_name = method_request.name
            logger.info(f"Received method request: {method_name}")

            if method_name in self._method_handlers:
                try:
                    # Call the registered handler
                    response_payload = self._method_handlers[method_name](
                        method_request.payload
                    )
                    response_status = 200
                except Exception as e:
                    logger.error(f"Method handler error: {e}")
                    response_payload = {"error": str(e)}
                    response_status = 500
            else:
                logger.warning(f"No handler registered for method: {method_name}")
                response_payload = {"error": f"Method {method_name} not found"}
                response_status = 404

            # Send response
            method_response = MethodResponse.create_from_method_request(
                method_request,
                response_status,
                response_payload
            )
            await self.client.send_method_response(method_response)

        # Register the generic handler
        self.client.on_method_request_received = method_request_handler
        logger.info("Method handlers set up successfully")

    async def update_twin_reported_properties(
        self,
        properties: Dict[str, Any]
    ) -> None:
        """
        Update device twin reported properties.

        Args:
            properties: Dictionary of properties to update
        """
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")

        try:
            await self.client.patch_twin_reported_properties(properties)
            logger.info(f"Twin reported properties updated: {properties}")
        except Exception as e:
            logger.error(f"Failed to update twin properties: {e}")
            raise

    async def get_twin(self) -> Dict[str, Any]:
        """
        Get the current device twin.

        Returns:
            Dictionary containing the device twin
        """
        if not self._is_connected or not self.client:
            raise RuntimeError("Client is not connected. Call connect() first.")

        try:
            twin = await self.client.get_twin()
            logger.info("Retrieved device twin")
            return twin
        except Exception as e:
            logger.error(f"Failed to get device twin: {e}")
            raise

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected
