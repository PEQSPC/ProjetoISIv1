from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from utils.validate_list_field import validate_list_field


class BrokerSettings(BaseModel):
    # Broker type: "mqtt" for traditional MQTT broker, "azure" for Azure IoT Hub
    broker_type: Literal["mqtt", "azure"] = Field(alias="BROKER_TYPE", default="mqtt")

    # Traditional MQTT broker settings
    url: str = Field(alias="BROKER_URL", default="localhost")
    port: int = Field(alias="BROKER_PORT", default=1883)
    protocol: int = Field(alias="PROTOCOL_VERSION", default=4)

    tls_ca_path: str | None = Field(alias="TLS_CA_PATH", default=None)
    tls_cert_path: str | None = Field(alias="TLS_CERT_PATH", default=None)
    tls_key_path: str | None = Field(alias="TLS_KEY_PATH", default=None)

    auth_username: str | None = Field(alias="AUTH_USERNAME", default=None)
    auth_password: str | None = Field(alias="AUTH_PASSWORD", default=None)

    # Azure IoT Hub settings
    azure_connection_string: str | None = Field(alias="AZURE_CONNECTION_STRING", default=None)
    azure_model_id: str | None = Field(alias="AZURE_MODEL_ID", default=None)

    def is_tls_enabled(self) -> bool:
        return (
            self.tls_ca_path is not None or
            self.tls_cert_path is not None or
            self.tls_key_path is not None
        )

    def is_auth_enabled(self) -> bool:
        return self.auth_username is not None or self.auth_password is not None

    def is_azure_enabled(self) -> bool:
        return self.broker_type == "azure" and self.azure_connection_string is not None

    @model_validator(mode="before")
    @classmethod
    def validate_topics(cls, data: Any) -> Any:
        return validate_list_field(caller="BrokerSettings", field_name="TOPICS", data=data, allow_empty=False)

    @model_validator(mode="after")
    def validate_azure_settings(self):
        if self.broker_type == "azure" and not self.azure_connection_string:
            raise ValueError(
                "AZURE_CONNECTION_STRING is required when BROKER_TYPE is 'azure'"
            )
        return self
