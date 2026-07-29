import json
import sys
from standalone.gateway import MicroHAGateway

def main():
    print("Чтение файла ha_states.json...")
    try:
        with open("standalone/ha_states.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("Файл standalone/ha_states.json не найден!")
        sys.exit(1)

    # Инициализируем шлюз без параметров
    gateway = MicroHAGateway()
    
    # Подменяем метод fetch_raw_states, чтобы он отдавал данные из файла
    gateway.fetch_raw_states = lambda: raw_data

    print("Парсинг и группировка...")
    groups = gateway.get_grouped_devices()

    # Сохраняем в красивый JSON
    output_file = "parsed_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2, ensure_ascii=False)

    print(f"Готово! Сгруппировано устройств: {len(groups)}")
    print(f"Результат сохранён в файл: {output_file}")

if __name__ == "__main__":
    main()
