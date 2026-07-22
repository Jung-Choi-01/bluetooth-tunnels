from flask import Flask, jsonify

from bluetooth_bridge import BluetoothBridge

DEVICE_MAC = "13:05:ac:00:fe:73"
WRITE_UUID = "0000ffa1-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ffa2-0000-1000-8000-00805f9b34fb"


def map_static_value(number):
    if number == 0:
        return 0x00

    clamped = max(0, min(99, number))
    mapped = round(0x20 + (clamped * (0xFF - 0x20) / 99))
    return max(0x20, min(0xFF, mapped))


def create_bridge():
    return BluetoothBridge(DEVICE_MAC, WRITE_UUID, NOTIFY_UUID)


def send_static_value(bridge, number):
    mapped_value = map_static_value(number)
    payload = bytes.fromhex(f"a003{mapped_value:02x}")
    bridge.send_bytes(payload)
    return mapped_value, payload


def create_app(bridge):
    app = Flask(__name__)

    @app.post("/joyhub-vibrator/static/<number>")
    def joyhub_vibrator_static(number):
        try:
            requested_number = int(number)
        except ValueError:
            return jsonify(ok=False, error="number must be an integer"), 400

        try:
            mapped_value, payload = send_static_value(bridge, requested_number)
        except Exception as exc:
            return jsonify(ok=False, error=str(exc)), 500

        return (
            jsonify(
                ok=True,
                requested=requested_number,
                clamped=max(0, min(99, requested_number)),
                mapped=payload.hex(),
                mapped_value=f"{mapped_value:02x}",
            ),
            200,
        )

    return app