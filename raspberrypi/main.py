import serial
import requests as req
import hashlib, base64, time, json

BACKEND_URL = "https://oa-backend.residualentropy.repl.co"

SECRET = None
with open("secret.txt", 'r') as f:
	SECRET = f.read().strip()

def main():
	print('Running...')
	print('Connecting to serial port...')
	with serial.Serial('/dev/ttyUSB0', 115200) as ser:
		print('Connected to serial port.')
		print(f'Using serial port {ser.name}.')
		print(f'Baud rate is {ser.baudrate}.')
		print(f'Serial port object: {repr(ser)}.')
		print('[api] Backend endpoint URL is {BACKEND_URL}')
		print('[api.auth] Asking for challenge...')
		challenge_hresp = req.get(f'{BACKEND_URL}/auth/get_challenge')
		challenge = challenge_hresp.json()['challenge']
		print('[api.auth] Computing response...')
		resp = hashlib.sha384(
			(challenge + SECRET) \
				.encode('utf-8')
		).digest()
		resp = base64.urlsafe_b64encode(resp).decode('utf-8')
		print('[api.auth] Sending response and asking for token...')
		tok_hresp = req.get(f'{BACKEND_URL}/auth/get_token?challenge={challenge}&response={resp}')
		tok_json = tok_hresp.json()
		if not tok_json["ok"]:
			raise RuntimeError("Authentication failed. Please try again.")
		tok = tok_json["token"]
		print('[api.auth] Should have valid token.')
		print('[api <- ser-proxy] Proxying serial port data...')
		while True:
			line = ser.readline()
			text = line.decode('utf-8')
			print('[api <- ser-proxy] Sending...', end='')
			text = text.strip().replace('\'', '"')
			obj = None
			try:
				obj = json.loads(text)
			except:
				print("!! Unable to parse JSON, ignoring.")
				print("!! --- BEGIN SAMPLE ---")
				print(text)
				print("!! --- END   SAMPLE ---")
				continue
			data = {
				"temps": {
					"unixts": int(time.time()),
					"readings": obj,
				},
				"token": tok,
			}
			print({"temps": data["temps"], "token": "REDACTED"})
			hresp = req.post(f'{BACKEND_URL}/api/w/temps', json=data)
			print(hresp.text)
			if not hresp.json()["w-ok"]:
				raise RuntimeError("Writing failed. Please try again.")
			print('[api <- ser-proxy] sent!')

if __name__ == '__main__':
	main()
