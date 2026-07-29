import json
import logging
from typing import Any, Dict, List

from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from homeassistant.const import HTTP_OK, HTTP_BAD_REQUEST, HTTP_INTERNAL_SERVER_ERROR

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

# Keywords of entities related to system service information
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

class MicroHAView(HomeAssistantView):
    """Custom API endpoint for MicroHA Gateway."""
    
    url = "/api/microha"
    name = "api:microha"
    requires_auth = False # Can be disabled for microcontrollers or replaced with a simple token
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the View."""
        self.hass = hass

    def _is_physical_device(self, entity_id: str) -> bool:
        """Check if the entity is a physical device."""
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        if domain not in PHYSICAL_DOMAINS:
            return False

        for kw in SYSTEM_KEYWORDS:
            if kw in entity_id:
                return False

        return True

    def _resolve_device_group(self, entity_id: str) -> str:
        """Determine the device group (dynamic algorithm)."""
        name_part = entity_id.split(".", 1)[1] if "." in entity_id else entity_id

        for suffix in COMMON_SUFFIXES:
            if name_part.endswith(suffix):
                name_part = name_part[:-len(suffix)]
                break

        if entity_id.startswith("weather."):
            name_part = "Weather"
            
        return name_part.replace("_", " ").title()

    async def get(self, request):
        """Handle GET requests and return grouped data."""
        _LOGGER.debug("MicroHA: Received GET request at /api/microha")
        
        # Get all states directly from Home Assistant's memory
        all_states = self.hass.states.async_all()
        
        groups: Dict[str, Dict[str, Any]] = {}
        
        for state_obj in all_states:
            entity_id = state_obj.entity_id
            
            if not self._is_physical_device(entity_id):
                continue
                
            domain = entity_id.split(".")[0]
            attributes = state_obj.attributes
            
            compact_item: Dict[str, Any] = {
                "id": entity_id,
                "name": attributes.get("friendly_name", entity_id),
                "type": domain,
                "state": state_obj.state,
                "actions": DOMAIN_ACTIONS.get(domain, []),
            }
            
            if "unit_of_measurement" in attributes:
                compact_item["unit"] = attributes["unit_of_measurement"]
            if "device_class" in attributes:
                compact_item["class"] = attributes["device_class"]
            if domain == "light" and "brightness" in attributes:
                compact_item["brightness"] = attributes["brightness"]
                
            group_name = self._resolve_device_group(entity_id)
            
            if group_name not in groups:
                groups[group_name] = {
                    "actuators": [],
                    "sensors": [],
                    "actions": [],
                }
                
            group = groups[group_name]
            
            if compact_item["actions"]:
                group["actuators"].append(compact_item)
                for action in compact_item["actions"]:
                    if action not in group["actions"]:
                        group["actions"].append(action)
            else:
                group["sensors"].append(compact_item)
                
        return self.json(groups, status_code=HTTP_OK)

    async def post(self, request):
        """Handle POST requests to control devices."""
        try:
            body = await request.json()
        except ValueError:
            return self.json({"error": "Invalid JSON"}, status_code=HTTP_BAD_REQUEST)
            
        entity_id = body.get("entity_id")
        action = body.get("action")
        
        if not entity_id or not action:
             return self.json({"error": "entity_id and action are required"}, status_code=HTTP_BAD_REQUEST)
             
        domain = entity_id.split(".")[0]
        service_data = {"entity_id": entity_id}
        
        # Add extra parameters if any (e.g. brightness)
        if "params" in body and isinstance(body["params"], dict):
            service_data.update(body["params"])
            
        try:
            _LOGGER.info(f"MicroHA: Calling service {domain}.{action} for {entity_id}")
            # Call the native Home Assistant service
            await self.hass.services.async_call(
                domain,
                action,
                service_data,
                blocking=False
            )
            return self.json({"status": "success", "message": f"Command {action} sent to {entity_id}"}, status_code=HTTP_OK)
        except Exception as e:
            _LOGGER.error(f"MicroHA Error: Service call failed: {e}")
            return self.json({"error": str(e)}, status_code=HTTP_INTERNAL_SERVER_ERROR)
