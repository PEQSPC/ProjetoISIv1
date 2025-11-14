import json
from pathlib import Path
from typing import Any

from publisher import Publisher
from azure_publisher import AzurePublisher
from settings_classes import BrokerSettings, ClientSettings, DataSettings, DataSettingsFactory, TopicSettingsFactory


def read_publishers(settings_file: Path, is_verbose: bool) -> list[Publisher]:
    def load_topic_data(topic_data_object: list[dict[str, Any]]) -> list[DataSettings]:
        topic_data: list[DataSettings] = []
        for data_object in topic_data_object:
            data_settings = DataSettingsFactory.create(data_object)
            topic_data.append(data_settings)
        return topic_data

    publishers: list[Publisher] = []
    default_client_settings = ClientSettings(CLEAN_SESSION=True, RETAIN=False, QOS=2, TIME_INTERVAL=10)
    with open(settings_file, encoding="utf-8") as json_file:
        json_object = json.load(json_file)
    broker_settings = BrokerSettings.model_validate(json_object)
    broker_client_settings = ClientSettings.model_validate(json_object).resolve_with_default(
        default=default_client_settings
    )

    # Determine which publisher class to use based on broker type
    PublisherClass = AzurePublisher if broker_settings.is_azure_enabled() else Publisher

    if broker_settings.is_azure_enabled():
        print(f"Using Azure IoT Hub publisher (connection: {broker_settings.azure_connection_string[:50]}...)")
    else:
        print(f"Using MQTT publisher (broker: {broker_settings.url}:{broker_settings.port})")

    # read each configured topic
    for topic_object in json_object.get("TOPICS"):
        client_settings = ClientSettings.model_validate(topic_object).resolve_with_default(
            default=broker_client_settings
        )
        topic_settings = TopicSettingsFactory.create(topic_object)
        topic_data_object = topic_object.get("DATA")
        for topic_url in topic_settings.topic_urls():
            # each topic_url should have different data_settings instances
            topic_data = load_topic_data(topic_data_object)
            publishers.append(
                PublisherClass(
                    broker_settings,
                    topic_url,
                    topic_data,
                    topic_settings.payload_root,
                    client_settings,
                    is_verbose,
                )
            )
    return publishers
