
import serial
import serial.tools.list_ports
import requests
import time
import configparser


class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		#self.postdata(0, 2)  prova post
		self.setupSerial()

	def postdata(self, i, val):
		if i > 0:
			return
		url = self.config.get("DJANGO","Url") + "/data"
		myobj = {'value': val}
		headers = {'X-AIO-Key': self.config.get("DJANGO","X-AIO-Key") }
		print ("> Sending to " + url)

		x = requests.post(url, data=myobj, headers=headers)
		print(x.json())

	def setupSerial(self):
		# open serial port
		self.ser = None

		if not self.config.getboolean("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM1")
		else:
			print("list of available ports: ")
			ports = serial.tools.list_ports.comports()

			for port in ports:
				print (port.device)
				print (port.description)
				if self.config.get("Serial","PortDescription", fallback="arduino").lower() \
						in port.description.lower():
					self.portname = port.device

		try:
			if self.portname is not None:
				print ("connecting to " + self.portname)
				self.ser = serial.Serial(self.portname, 9600, timeout=0)
				print("CONNESSO alla porta")
		except:
			print("ECCEZIONE")
			self.ser = None

		# self.ser.open()

		# internal input buffer from serial
		self.inbuffer = []


	def loop(self):
		lasttime = time.time()
		connect = 0
		while(True):
				current_time = time.time()
				#look for a byte from serial
				if not self.ser is None:
					while self.ser.inWaiting() != 0:

						# data available from the serial port
						lastchar = self.ser.read(1)

						#se viene inviato il carattere di inizio
						if connect == 0 and lastchar == b'\xff':
							print("Connesso, leggo i dati...")
							connect = 1
							continue

						if connect == 1:
							if lastchar == b'\xfe': #EOL
								connect = 0
								print("\nValue received")
								print(self.inbuffer)
								self.useData()
								self.inbuffer = []
							else:
								self.inbuffer.append(lastchar)

				# If no serial data, still check if 2 seconds have passed
				elif current_time - lasttime >= 2:
					print("no data")
					break



	def useData(self):
		# I have received a packet from the serial port. I can use it
		if len(self.inbuffer)<2:   # at least header, size, footer
			print("inbuffer short")
			return False
		# split parts

		#numval = int.from_bytes(self.inbuffer[1], byteorder='little')
		#print(numval)

		for i in range(2):
			val = int.from_bytes(self.inbuffer[i], byteorder='little')
			print(val)
			#self.postData(i, val)

if __name__ == '__main__':
	br = Bridge()
	br.loop()

