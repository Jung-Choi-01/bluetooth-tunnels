from devices.joyhub_vibrator import create_app, create_bridge


def main():
    joyhub_vibrator_bridge = create_bridge()
    joyhub_vibrator_bridge.start()

    try:
        app = create_app(joyhub_vibrator_bridge)
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False, threaded=True)
    finally:
        joyhub_vibrator_bridge.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting via keyboard interrupt.")