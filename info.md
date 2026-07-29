# MicroHA Gateway

An ultra-fast and lightweight integration for serving data to weak microcontrollers (ESP8266, ESP32) with dynamic entity grouping. It serves an ultra-compact JSON without tokens at the local address `http://<HA_IP>:8123/api/microha`.

## What does this integration do?
1. Fetches the states of all devices directly from Home Assistant's memory.
2. Filters out garbage and system data.
3. Keeps useful sensors, lights, switches, climate, monitoring (Uptime Kuma), and weather.
4. Uses a smart algorithm to group all related entities into a single physical device (e.g., a smart plug and its power sensors are grouped into 1 block `Wifi Plug`).
5. Allows microcontrollers to call services (toggle, turn_on) with a simple POST request.

## Getting Started
After installing the component, add the following line to your `configuration.yaml`:
```yaml
microha:
```
Then restart Home Assistant. Full documentation is available on GitHub.
