import serial
from websockets.sync.client import connect

import hashlib, base64

WS_BACKEND_URL = "wss://temperature-backend--residualentropy.repl.co"

SECRET = None
with open("secret.txt", 'r') as f:
	SECRET = f.read().strip()

def retrieve_secret():
	return SECRET

def main():
	print('Running...')
	print('Connecting to serial port...')
	with serial.Serial('/dev/ttyUSB0', 115200) as ser:
		print('Connected to serial port.')
		print(f'Using serial port {ser.name}.')
		print(f'Baud rate is {ser.baudrate}.')
		print(f'Serial port object: {repr(ser)}.')
		print('Connecting to websockets endpoint...')
		with connect(WS_BACKEND_URL) as ws:
			print('Connected to websockets.')
			print('Endpoint URL is {WS_BACKEND_URL}')
			print(f'Websockets connection object: {repr(ws)}')
			print('[ws-layer] Waiting for challenge...')
			challenge = ws.recv()
			assert challenge[0] == 'c'
			challenge = challenge[1:]
			print('[ws-layer] Computing response...')
			resp = hashlib.sha384(
				(retrieve_secret() + challenge) \
					.encode('utf-8')
			).digest()
			print('[ws-layer] Sending response...')
			ws.send('r' + base64.b64encode(resp).decode('utf-8'))
			print('[ws-layer] Connection should be ready.')
			print('[ws-layer] Proxying serial port data...')
			while True:
				line = ser.readline()
				text = line.decode('utf-8')
				print('[ws-layer] [ser-proxy] Sending...', end='')
				ws.send(f'd{text.strip()}')
				print('[ws-layer] [ser-proxy] sent!')

if __name__ == '__main__':
	main()
