import asyncio
import threading

from bleak import BleakClient, BleakScanner


def default_notification_handler(sender, data):
    print(f"\n[Toy Response] {data.hex()}")


class BluetoothBridge:
    def __init__(self, device_mac, write_uuid, notify_uuid, notification_handler=None):
        self.device_mac = device_mac
        self.write_uuid = write_uuid
        self.notify_uuid = notify_uuid
        self.notification_handler = notification_handler or default_notification_handler
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.client = None
        self._send_lock = None

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        self.loop_thread.start()

    def close(self):
        if self.loop.is_closed():
            return

        try:
            future = asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
            future.result(timeout=10)
        except Exception:
            pass
        finally:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.loop_thread.join(timeout=5)
            self.loop.close()

    async def _disconnect(self):
        if self.client and self.client.is_connected:
            try:
                await self.client.stop_notify(self.notify_uuid)
            except Exception:
                pass
            await self.client.disconnect()
        self.client = None

    async def _connect(self):
        if self.client and self.client.is_connected:
            return

        if self._send_lock is None:
            self._send_lock = asyncio.Lock()

        print(f"Searching for device {self.device_mac}...")
        device = await BleakScanner.find_device_by_address(self.device_mac, timeout=10.0)
        if not device:
            raise RuntimeError("Device not found.")

        print("Connecting to device...")
        client = BleakClient(device)
        await client.connect()
        print("Connected! Initializing notification handshake...")
        await client.start_notify(self.notify_uuid, self.notification_handler)
        await asyncio.sleep(0.5)
        self.client = client

    async def _ensure_connected(self):
        if not self.client or not self.client.is_connected:
            await self._connect()

    async def _send_bytes_async(self, payload):
        if self._send_lock is None:
            self._send_lock = asyncio.Lock()

        async with self._send_lock:
            await self._ensure_connected()
            client = self.client
            if client is None:
                raise RuntimeError("Bluetooth client is not connected.")

            await client.write_gatt_char(self.write_uuid, payload, response=False)

    async def _send_hex_async(self, hex_payload):
        payload = bytes.fromhex(hex_payload)
        await self._send_bytes_async(payload)

    def send_bytes(self, payload):
        future = asyncio.run_coroutine_threadsafe(self._send_bytes_async(payload), self.loop)
        return future.result()

    def send_hex(self, hex_payload):
        future = asyncio.run_coroutine_threadsafe(self._send_hex_async(hex_payload), self.loop)
        return future.result()