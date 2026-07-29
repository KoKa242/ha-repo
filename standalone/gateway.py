import json
import logging
import requests
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger(__name__)

# Domains of physical devices
PHYSICAL_DOMAINS = {
    "light",
    "switch",
    "sensor",
    "binary_sensor",
    "media_player",
    "climate",
    "cover",
    "fan",
    "lock",
    "vacuum",
    "remote",
    "weather",
}

# Keywords of entities related to system service information (excluded from the gateway)
SYSTEM_KEYWORDS = [
    "update.",
    "conversation.",
    "sun.",
    "event.",
    "zone.",
    "tts.",
    "stt.",
    "sensor.sun_",
    "sensor.traffic_",
    "sensor.backup_",
    "iphone_",
    "ipad_",
    "macbook_",
    "apple_watch_",
]

# Map of supported actions for each domain
DOMAIN_ACTIONS: Dict[str, List[str]] = {
    "light": ["turn_on", "turn_off", "toggle"],
    "switch": ["turn_on", "turn_off", "toggle"],
    "media_player": ["media_play", "media_pause", "media_play_pause", "volume_set", "volume_mute"],
    "climate": ["set_temperature", "set_hvac_mode", "set_fan_mode", "turn_on", "turn_off"],
    "cover": ["open_cover", "close_cover", "stop_cover", "set_cover_position"],
    "fan": ["turn_on", "turn_off", "set_percentage"],
    "lock": ["lock", "unlock", "open"],
    "vacuum": ["start", "pause", "return_to_base"],
    "remote": ["turn_on", "turn_off"],
    "sensor": [],
    "binary_sensor": [],
    "weather": [],
}

# Common suffixes for dynamic grouping algorithm
COMMON_SUFFIXES = [
    "_current", "_power", "_voltage", "_total_energy",
    "_battery_level", "_battery_state", "_battery",
    "_watch_battery_level", "_watch_battery_state",
    "_kiosk_mode", "_geocoded_location", "_child_lock",
    "_socket_1", "_switch_1", "_status", "_monitor_type",
    "_monitored_url", "_monitored_hostname", "_monitored_port",
    "_certificate_expiry", "_response_time", "_app_version",
    "_last_update_trigger", "_location_permission", "_kiosk_brightness",
    "_kiosk_volume", "_audio_output", "_ssid", "_bssid",
    "_connection_type", "_storage"
]

class MicroHAGateway:
    """MicroHA Gateway to transform heavy Home Assistant JSON

    into a lightweight format for low-power controllers (ESP32/ESP8266) and send commands.
    """

    def __init__(self, ha_url: str = "", token: str = ""):
        self.ha_url = ha_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def is_physical_device(self, entity_id: str) -> bool:
        """Check if the entity is a physical device."""
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        if domain not in PHYSICAL_DOMAINS:
            return False

        # Exclude system data
        for kw in SYSTEM_KEYWORDS:
            if kw in entity_id:
                return False

        return True

    def fetch_raw_states(self) -> List[Dict[str, Any]]:
        """Fetch data directly from HA API."""
        if self.ha_url and self.token:
            try:
                response = requests.get(f"{self.ha_url}/api/states", headers=self.headers, timeout=5)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                _LOGGER.warning(f"Network error when requesting HA API ({e}).")
        else:
            _LOGGER.error("HA URL or token is not configured!")

        return []

    def get_compact_devices(self) -> List[Dict[str, Any]]:
        """Fetch and transform all physical devices into an ultra-compact format."""
        raw_states = self.fetch_raw_states()
        compact_list = []

        for item in raw_states:
            entity_id = item.get("entity_id", "")
            if not self.is_physical_device(entity_id):
                continue

            domain = entity_id.split(".")[0]
            attributes = item.get("attributes", {})

            # Base properties of the compact entity
            compact_item: Dict[str, Any] = {
                "id": entity_id,
                "name": attributes.get("friendly_name", entity_id),
                "type": domain,
                "state": item.get("state"),
                "actions": DOMAIN_ACTIONS.get(domain, []),
            }

            # Additional numeric values for sensors or sockets
            if "unit_of_measurement" in attributes:
                compact_item["unit"] = attributes["unit_of_measurement"]
            if "device_class" in attributes:
                compact_item["class"] = attributes["device_class"]

            # Extract useful attributes for climate or lights, if any
            if domain == "light" and "brightness" in attributes:
                compact_item["brightness"] = attributes["brightness"]

            compact_list.append(compact_item)

        return compact_list

    def control_device(
        self, entity_id: str, action: str, params: Optional[Dict[str, Any]] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """Send a control command to the Home Assistant API.

        :param entity_id: Entity ID (e.g., 'switch.t34_smart_plug_switch_1')
        :param action: Action (e.g., 'turn_on', 'turn_off', 'toggle')
        :param params: Additional parameters (e.g., {'brightness': 128})
        :param dry_run: If True, only generates and returns the payload without calling the API
        """
        domain = entity_id.split(".")[0]
        url = f"{self.ha_url}/api/services/{domain}/{action}"

        payload = {"entity_id": entity_id}
        if params:
            payload.update(params)

        if dry_run or not (self.ha_url and self.token):
            _LOGGER.info(f"Gateway Dry-Run: POST {url} | Body: {json.dumps(payload)}")
            return {"status": "dry_run", "url": url, "payload": payload}

        try:
            res = requests.post(url, headers=self.headers, json=payload, timeout=5)
            res.raise_for_status()
            return {"status": "success", "code": res.status_code, "response": res.json()}
        except Exception as e:
            _LOGGER.error(f"Control error for {entity_id} ({action}): {e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    def _resolve_device_group(entity_id: str) -> str:
        """Determine to which physical device the entity_id belongs (dynamic algorithm)."""
        # Remove the domain: "sensor.wifi_plug_power" → "wifi_plug_power"
        name_part = entity_id.split(".", 1)[1] if "." in entity_id else entity_id

        # Dynamically cut off known suffixes to find the base device name
        for suffix in COMMON_SUFFIXES:
            if name_part.endswith(suffix):
                name_part = name_part[:-len(suffix)]
                break

        # Special case for weather
        if entity_id.startswith("weather."):
            name_part = "Weather"
            
        # Make the name pretty (e.g., "wifi_plug" -> "Wifi Plug")
        return name_part.replace("_", " ").title()

    def get_grouped_devices(self) -> Dict[str, Dict[str, Any]]:
        """Return devices grouped by physical device."""
        compact_devices = self.get_compact_devices()
        groups: Dict[str, Dict[str, Any]] = {}

        for dev in compact_devices:
            group_name = self._resolve_device_group(dev["id"])

            if group_name not in groups:
                groups[group_name] = {
                    "actuators": [],
                    "sensors": [],
                    "actions": [],
                }

            group = groups[group_name]

            if dev["actions"]:
                # Controllable entity
                group["actuators"].append(dev)
                # Collect unique actions
                for action in dev["actions"]:
                    if action not in group["actions"]:
                        group["actions"].append(action)
            else:
                # Sensor
                group["sensors"].append(dev)

        return groups
