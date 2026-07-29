# MicroHA Gateway

**MicroHA Gateway** is an lightweight Home Assistant integration designed specifically to serve grouped data to weak microcontrollers (ESP8266, ESP32, Arduino) and interact with them.

## Why is this needed?
The standard Home Assistant REST API returns heavy JSON responses, parsing which often leads to `Out Of Memory` errors on low-power microcontrollers.

**MicroHA Gateway solves this problem:**
* Fetches the states of all devices instantly from Home Assistant's memory.
* Filters out all system "garbage" data.
* Keeps the necessary data (Uptime Kuma monitoring, weather, smart devices).
* **Dynamically groups sensors and controllable switches/relays by physical devices**, stripping redundant suffixes.
* Serves an ultra-compact JSON weighing only a few kilobytes.

## Installation via HACS

1. Open HACS in your Home Assistant.
2. Click on **Integrations**.
3. In the top right corner, click on **Custom repositories**.
4. Paste the link to this GitHub repository.
5. Select the **Integration** category and click Add.
6. Search for `MicroHA Gateway` in HACS and click **Download**.
7. Restart Home Assistant.
8. Add the following line to your `configuration.yaml`:
   ```yaml
   microha:
   ```
9. Restart Home Assistant one more time.

## Usage (API for ESP32)

The integration automatically creates 2 endpoints. Token authentication is not required.

### 1. Fetching compact data
`GET http://<HA_IP>:8123/api/microha`

**Example Response:**
```json
{
  "Wifi Plug": {
    "actuators": [
      {
        "id": "switch.wifi_plug_socket_1",
        "name": "Fan Socket",
        "type": "switch",
        "state": "on",
        "actions": ["turn_on", "turn_off", "toggle"]
      }
    ],
    "sensors": [
      {
        "id": "sensor.wifi_plug_power",
        "name": "Fan Power",
        "type": "sensor",
        "state": "12.5",
        "actions": [],
        "unit": "W",
        "class": "power"
      }
    ],
    "actions": ["turn_on", "turn_off", "toggle"]
  }
}
```

### 2. Controlling devices
Send a command (e.g., turn on a light) from the microcontroller:

`POST http://<HA_IP>:8123/api/microha`

**Request Body (JSON):**
```json
{
  "entity_id": "switch.wifi_plug_socket_1",
  "action": "toggle"
}
```
