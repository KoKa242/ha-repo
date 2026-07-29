import json
import requests

# Настройки Home Assistant
HA_URL = "http://homeassistant.local:8123"  # Укажите ваш URL/IP Home Assistant
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0YTNkMTkxODRlNGU0NGY3YTcxZGI0ZTcwZWNlYTFlYyIsImlhdCI6MTc4NTMyNTY1MywiZXhwIjoyMTAwNjg1NjUzfQ.Ec-WuE3DBWxtQlkW1JIMMlRTcjXxKAG4aF5ii_krqJ4"  # Ваш Долгосрочный токен доступа

# Заголовки для авторизации в REST API
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "content-type": "application/json",
}

# Endpoint для получения всех состояний (entities)
# Также можно использовать f"{HA_URL}/api/config" для получения конфигурации
url = f"{HA_URL}/api/states"

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    # Получаем JSON ответ
    data = response.json()

    # Преобразуем в отформатированную строку
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    # Выводим весь JSON в терминал
    print(json_str)

    # Сохраняем в файл ha_states.json
    output_filename = "ha_states.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"\n[Успешно] JSON сохранен в файл: {output_filename}")

except requests.exceptions.RequestException as e:
    print(f"[Ошибка при запросе]: {e}")
