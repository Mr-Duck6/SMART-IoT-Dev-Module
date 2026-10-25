# Архітектура

```text
Python simulator (3 rooms)
        | MQTT / JSON / QoS 1
        v
Mosquitto broker :1883
        | MQTT binding
        v
openHAB :8080 -> Items / Rules / UI
```

## Topics
- `warehouse/<room>/telemetry` - датчики; JSON, QoS 1, retained.
- `warehouse/<room>/status` - статус симулятора; JSON, QoS 1, retained.

## Rules in this demo
- Попередження, якщо температура кімнати 1 перевищує 5 °C.
- Критичне попередження, якщо температура кімнати 1 перевищує 8 °C.
- Запис у лог при відкритті дверей будь-якої кімнати.

