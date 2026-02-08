# Arduino 101 Bluetooth Low Energy
# Requires: pip install bleak

import argparse
import asyncio
from bleak import BleakClient, BleakScanner

LED_CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
DEVICE_NAME = "Arduino101-LED"


async def find_device(address: str | None) -> str:
	if address:
		return address

	devices = await BleakScanner.discover(timeout=5.0)
	for device in devices:
		if device.name == DEVICE_NAME:
			return device.address

	raise RuntimeError(f"Could not find BLE device named '{DEVICE_NAME}'.")


async def connect_client(address: str | None) -> BleakClient:
	target = await find_device(address)
	client = BleakClient(target)
	await client.connect()
	if not client.is_connected:
		raise RuntimeError("Failed to connect to device.")
	return client


async def send_command(client: BleakClient, command: int, response: bool) -> None:
	value = bytes([command])
	await client.write_gatt_char(LED_CHAR_UUID, value, response=response)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Send Arduino 101 BLE commands")
	parser.add_argument(
		"state",
		nargs="?",
		choices=["on", "off", "toggle", "w", "a", "s", "d"],
		help="Command to send (LED or movement)",
	)
	parser.add_argument(
		"--address",
		help="BLE MAC address (optional). If omitted, scans for device name.",
	)
	parser.add_argument(
		"--no-response",
		action="store_true",
		help="Use write without response (faster, less reliable).",
	)
	return parser.parse_args()


def prompt_state() -> str:
	while True:
		raw = input("Enter command (on/off/toggle/w/a/s/d): ").strip().lower()
		if raw in {"on", "off", "toggle", "w", "a", "s", "d", "q"}:
			return raw
		print("Please enter 'on', 'off', 'toggle', 'w', 'a', 's', 'd', or 'q'.")


async def handle_state(state: str, client: BleakClient, response: bool) -> None:
	if state == "toggle":
		await send_command(client, 1, response)
		await asyncio.sleep(0.2)
		await send_command(client, 0, response)
		return

	if state == "on":
		await send_command(client, 1, response)
		return
	if state == "off":
		await send_command(client, 0, response)
		return

	await send_command(client, ord(state), response)


async def main() -> None:
	args = parse_args()
	response = not args.no_response
	client = await connect_client(args.address)
	try:
		if args.state:
			await handle_state(args.state, client, response)
			return

		while True:
			state = prompt_state()
			if state == "q":
				return
			await handle_state(state, client, response)
	finally:
		if client.is_connected:
			await client.disconnect()


if __name__ == "__main__":
	asyncio.run(main())