import serial
from serial import tools
import requests
import time
import configparser


class Bridge():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.setupSerial()

    def postData(self, val):
        if len(val) < 6:
            return print("values missing")
        url = self.config.get("DJANGO", "Url") + "data/"
        #bot_url = self.config.get("TELEGRAM", "Url")
        myobj = {'id':val[0],
                 'button_state': val[1],
                 'temp_in': val[2],
                 'hum_in': val[3],
                 'temp_out': val[4],
                 'pot_val' : val[5]}
        headers = {'X-AIO-Key': self.config.get("DJANGO", "X-AIO-Key")}
        print("> Sending to " + url)

        x = requests.post(url, data=myobj, headers=headers)
        #print(x.json())

    def getData(self):
        url = self.config.get("DJANGO", "Url") + "data/alarm/"
        headers = {'X-AIO-Key': self.config.get("HTTPAIO", "X-AIO-Key")}
        print("> Sending GET to " + url)

        x = requests.get(url, headers=headers)
        res = x.json()
        val = res.get('value', None)
        print(x.json())
        return val


    def setupSerial(self):
        # open serial port
        self.ser = None

        if not self.config.getboolean("Serial", "UseDescription", fallback=False):
            self.portname = self.config.get("Serial", "PortName", fallback="COM1")
        else:
            print("list of available ports: ")
            ports = serial.tools.list_ports.comports()

            for port in ports:
                print(port.device)
                print(port.description)
                if self.config.get("Serial", "PortDescription", fallback="arduino").lower() \
                        in port.description.lower():
                    self.portname = port.device

        try:
            if self.portname is not None:
                print("connecting to " + self.portname)
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
        while (True):
            current_time = time.time()
            # look for a byte from serial
            if not self.ser is None:
                while self.ser.inWaiting() != 0:

                    # data available from the serial port
                    lastchar = self.ser.read(1)

                    # se viene inviato il carattere di inizio
                    if connect == 0 and lastchar == b'\xff':
                        print("Connesso, leggo i dati...")
                        connect = 1
                        continue

                    if connect == 1:
                        if lastchar == b'\xfe':  # EOL
                            connect = 0
                            print("\nValue received")
                            print(self.inbuffer)

                            # check if there's an ID and enough data
                            if len(self.inbuffer) < 3:  # ID + at least 1 data + footer
                                print("Packet is too short, ignored")
                            else:
                                self.useData()  # process data

                                # Get data and send appropriate command
                                dataAlarm = self.getData()
                                if dataAlarm == '1':
                                    self.ser.write(b'A')
                                elif dataAlarm == '0':
                                    self.ser.write(b'S')

                            # clear the buffer
                            self.inbuffer = []

                        else:
                            self.inbuffer.append(lastchar)

            # If no serial data, still check if 2 seconds have passed
            elif current_time - lasttime >= 2:
                print("no data")
                break

    def useData(self):
        # I have received a packet from the serial port. I can use it
        if len(self.inbuffer) < 3:  # at least header, id, size?, footer
            print("inbuffer short")
            return False

        # extract arduino ID
        arduino_id = int.from_bytes(self.inbuffer[1], byteorder='little')
        print("Arduino ID received: ", arduino_id, ", data: ", self.inbuffer[1:6])

        print("\nPrinting: {")
        #read all sent values (also Arduino ID)
        val = []
        for i in range(len(self.inbuffer)):
            val.append(int.from_bytes(self.inbuffer[i], byteorder='little'))
            print(val[i], ",")
        print("}")
        self.postData(val)


if __name__ == '__main__':
    br = Bridge()
    br.loop()
