### author: Roberto Vezzani

import serial
import serial.tools.list_ports
import requests
import time
import configparser


class Bridge():

	def __init__(self):
		self.setupSerial()

	def setupSerial(self):
		# open serial port
		self.ser = serial.Serial()
		print("list of available ports: ")
		ports = serial.tools.list_ports.comports()
		for port in ports:
			print (port.description)
			if 'arduino' in port.description.lower():
				self.portname = port.device

		if self.portname is not None:
			try:
				print("\ntry connecting to " + self.portname)
				self.ser.port = self.portname
				self.ser.baudrate = 9600
				self.ser.timeout = 0

				print(self.portname + " connected!")
			except:
				print("unable to connect to " + self.portname)
				self.ser.__del__()

		try:
			self.ser.open()
		except:
			print("Access denied!")
		# internal input buffer from serial
		self.inbuffer = []


	def loop(self):
		lasttime = time.time()
		while(True):
				current_time = time.time()
				#look for a byte from serial
				if not self.ser is None:
					while self.ser.in_waiting > 0:
						# data available from the serial port
						lastchar = self.ser.read(1)
						if lastchar == b'\xfe': #EOL
							print("last char")
							# Only process data if 2 seconds have passed
							if current_time - lasttime >= 2:
								print("\nValue received")
								self.useData()

								# Get data and send appropriate command

								# Update lasttime
								lasttime = current_time

							self.inbuffer = []
						else:
							# append
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
		if self.inbuffer[0] != b'\xff':
			print(int.from_bytes(self.inbuffer[0], byteorder='little'))
			print("uncorrect first char")
			return False

		#numval = int.from_bytes(self.inbuffer[1], byteorder='little')
		#print(numval)

		for i in range(2):
			val = int.from_bytes(self.inbuffer[i], byteorder='little')
			print(val)
			#self.postData(i, val)

if __name__ == '__main__':
	br = Bridge()
	br.loop()

