import json
import config
from consul_service_utils.consul_service import add_key_value

with open(config.MESSAGES_QUEUE_CONFIG_PATH) as f:
    ms_config = json.load(f)

ms_config_value = json.dumps(ms_config)
add_key_value(config.MESSAGES_QUEUE_CONFIG_KEY, ms_config_value)


with open(config.HAZELCAST_CONFIG_PATH) as f:
    hz_config = json.load(f)

hz_config_value = json.dumps(hz_config)
add_key_value(config.HAZELCAST_CONFIG_KEY, hz_config_value)
