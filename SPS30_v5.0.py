#!/usr/bin/env python3
# coding=utf-8
#
# Copyright © 2018 UnravelTEC
# Michael Maier <michael.maier+github@unraveltec.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# If you want to relicense this code under another license, please contact info+github@unraveltec.com.

# This module uses the services of the C pigpio library. pigpio must be running on the Pi(s) whose GPIO are to be manipulated. 
# cmd ref: http://abyz.me.uk/rpi/pigpio/python.html#i2c_write_byte_data
# aptitude install python3-pigpio 
import pigpio # controlar entradas y salidas
import time # controlar el tiempo
import struct # interpretar bytes como paquetes de datos binarios
import sys # controlar parametros y funciones especificas del sistema
# aptitude install python3-crcmod
import crcmod 
import os, signal
from subprocess import call
#integracion de libreria a la nube
import requests
import time

import pprint
############
import mysql.connector

conexion1=mysql.connector.connect(host="localhost", user="eduardo", passwd="123456", database="aire")
cursor1=conexion1.cursor()

#################

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

#LOGFILE = '/run/sensors/sps30/last'
LOGFILE = '/home/eduardo/Desktop/run/last.txt'

PIGPIO_HOST = '127.0.0.1'
I2C_SLAVE = 0x69
I2C_BUS = 1

DEBUG = False

deviceOnI2C = call("i2cdetect -y 1 0x69 0x69|grep '\--' -q", shell=True) # grep exits 0 if match found
if deviceOnI2C:
  print("I2Cdetect found SPS30")
else:
  print("SPS30 (0x69) not found on I2C bus")
  exit(1)

def exit_gracefully(a,b):
  print("exit")
  stopMeasurement()
  os.path.isfile(LOGFILE) and os.access(LOGFILE, os.W_OK) and os.remove(LOGFILE)
  pi.i2c_close(h)
  exit(0)

signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)



pi = pigpio.pi(PIGPIO_HOST)
if not pi.connected:
  eprint("no connection to pigpio daemon at " + PIGPIO_HOST + ".")
  exit(1)
else:
  if DEBUG:
    print("connection to pigpio daemon successful")


try:
  pi.i2c_close(0)
except:
  tupl = sys.exc_info()
  if tupl[1] and str(tupl[1]) != "'unknown handle'":
    eprint("Unknown error: ", tupl)

#try:
h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
#except:
#  eprint("i2c open failed")
#  exit(1)

#def i2cOpen():
#  global h
#  try:
#    h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
#  except:
#    eprint("i2c open failed")
#    exit(1)


f_crc8 = crcmod.mkCrcFun(0x131, 0xFF, False, 0x00)

def calcCRC(TwoBdataArray):
  byteData = ''.join(chr(x) for x in TwoBdataArray)
  return f_crc8(byteData.encode())

# print(hex(calcCRC([0xBE,0xEF])))

def readNBytes(n):
  try:
    (count, data) = pi.i2c_read_device(h, n)
  except:
    eprint("error: i2c_read failed")
    exit(1)

  if count == n:
    return data
  else:
    eprint("error: read bytes didnt return " + str(n) + "B")
    return False

# takes an array of bytes (integer-array)
def i2cWrite(data):
  try:
    pi.i2c_write_device(h, data)
  except Exception as e:
    pprint.pprint(e)
    eprint("error in i2c_write:", e.__doc__ + ":",  e.value)
    return -1
  return True

def readFromAddr(LowB,HighB,nBytes):
  for amount_tries in range(3):
    ret = i2cWrite([LowB, HighB])
    if ret != True:
      eprint("readFromAddr: write try unsuccessful, next")
      continue
    data = readNBytes(nBytes)
    if data:
      return data
    eprint("error in readFromAddr: " + hex(LowB) + hex(HighB) + " " + str(nBytes) + "B did return Nothing")
  eprint("readFromAddr: write tries(3) exceeded")
  return False

def readArticleCode():
  data = readFromAddr(0xD0,0x25,47)
  if data == False:
    eprint('readArticleCode failed')
    return False

  acode = ''
  crcs = ''
  for i in range(47):
    currentByte = data[i]
    if currentByte == 0:
      break;
    if (i % 3) != 2:
      acode += chr(currentByte) + '|'
    else:
      crcs += str(currentByte) + '.'
  print('Article code: "' + acode + '"')
  return True

def readSerialNr():
  data = readFromAddr(0xD0,0x33,47)
  if data == False:
    eprint('readSerialNr failed')
    return False

  snr = ''
  for i in range(47):
    if (i % 3) != 2:
      currentByte = data[i]
      if currentByte == 0:
        break;
      if i != 0:
        snr += '-'
      snr += chr(currentByte)
  print('Serial number: ' + snr)
  return True

def readCleaningInterval():
  data = readFromAddr(0x80,0x04,6)
  if data and len(data):
    interval = calcInteger(data)
    print('cleaning interval:', str(interval), 's')

def startMeasurement():
  ret = -1
  for i in range(3):
    ret = i2cWrite([0x00, 0x10, 0x03, 0x00, calcCRC([0x03,0x00])])
    if ret == True:
      return True
    eprint('startMeasurement unsuccessful, next try')
    bigReset()
  eprint('startMeasurement unsuccessful, giving up')
  return False

def stopMeasurement():
  i2cWrite([0x01, 0x04])

def reset():
  if DEBUG:
    print("reset called")
  for i in range(5):
    ret = i2cWrite([0xd3, 0x04])
    if DEBUG:
      print("reset sent")
    if ret == True:
      if DEBUG:
        print("reset ok")
      return True
    eprint('reset unsuccessful, next try in', str(0.2 * i) + 's')
    time.sleep(0.2 * i)
  eprint('reset unsuccessful')
  return False



def readDataReady():
  data = readFromAddr(0x02, 0x02,3)
  if data == False:
    eprint("readDataReady: command unsuccessful")
    return -1
  if data and data[1]:
    if DEBUG:
      print("✓")
    return 1
  else:
    if DEBUG:
      print('.',end='')
    return 0

def calcInteger(sixBArray):
  integer = sixBArray[4] + (sixBArray[3] << 8) + (sixBArray[1] << 16) + (sixBArray[0] << 24)
  return integer

def calcFloat(sixBArray):
  struct_float = struct.pack('>BBBB', sixBArray[0], sixBArray[1], sixBArray[3], sixBArray[4])
  float_values = struct.unpack('>f', struct_float)
  first = float_values[0]
  return first

def printPrometheus(data):
  pm10 = calcFloat(data[18:24])
  if pm10 == 0:
    eprint("pm10 == 0; ignoring values")
    return

  output_string = 'particulate_matter_ppcm3{{size="pm0.5",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[24:30]))
  output_string += 'particulate_matter_ppcm3{{size="pm1",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[30:36]))
  output_string += 'particulate_matter_ppcm3{{size="pm2.5",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[36:42]))
  output_string += 'particulate_matter_ppcm3{{size="pm4",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[42:48]))
  output_string += 'particulate_matter_ppcm3{{size="pm10",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[48:54]))
  output_string += 'particulate_matter_ugpm3{{size="pm1",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data))
  output_string += 'particulate_matter_ugpm3{{size="pm2.5",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[6:12]))
  output_string += 'particulate_matter_ugpm3{{size="pm4",sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[12:18]))
  output_string += 'particulate_matter_ugpm3{{size="pm10",sensor="SPS30"}} {0:.8f}\n'.format( pm10 )
  output_string += 'particulate_matter_typpartsize_um{{sensor="SPS30"}} {0:.8f}\n'.format( calcFloat(data[54:60]))
  # print(output_string)
  logfilehandle = open(LOGFILE, "w",1)
  logfilehandle.write(output_string)
  logfilehandle.close()

def printHuman(data):
  #print("pm0.5 count: %f" % calcFloat(data[24:30]))
  #print("pm1   count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[30:36]), calcFloat(data) ) )
  #print("pm2.5 count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[36:42]), calcFloat(data[6:12]) ) )
  #print("pm4   count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[42:48]), calcFloat(data[12:18]) ) )
  #print("pm10  count: {0:.3f} ug: {1:.3f}".format( calcFloat(data[48:54]), calcFloat(data[18:24]) ) )
  data_envio = calcFloat(data[18:24])
  return data_envio
  #print("pm_typ: %f" % calcFloat(data[54:60]))


def readPMValues():
  print("Lectura de datos")
  data = readFromAddr(0x03,0x00,59)
  printPrometheus(data)
  printHuman(data)
  return data

'''def send_data(data):
    print("enviando datos")
    #pm10 = printHuman(data)
    #####url_pm10 = "https://api.thingspeak.com/update?api_key=DRBYUZANZYRQJMAW&field1=" #url obtenida desde Thingspeak
    #concatenar URL más valor
    url_envio = url_pm10 + str(round(calcFloat(data[18:24]),2))
    #####url_pm25 = "https://api.thingspeak.com/update?api_key=DRBYUZANZYRQJMAW&field2="
    #print(url_envio)
    url_envio2 = url_pm25 + str(round(calcFloat(data[6:12]),2))
    #enviar dato
    r = requests.get(url_envio,url_envio2) 
    print(r)
'''
def initialize():
  startMeasurement() or exit(1)
  time.sleep(0.9)

def bigReset():
  global h
  if DEBUG:
    print("bigReset.")
  eprint('resetting...',end='')
  pi.i2c_close(h)
  time.sleep(0.5)
  h = pi.i2c_open(I2C_BUS, I2C_SLAVE)
  time.sleep(0.5)
  reset()
  time.sleep(0.1) # note: needed after reset

if len(sys.argv) > 1 and sys.argv[1] == "stop":
  exit_gracefully(False,False)

#call(["mkdir", "-p", "/run/sensors/sps30"])
call(["mkdir", "-p", "/home/eduardo/Desktop/run"])

readArticleCode() or exit(1)

reset()
time.sleep(0.1) # note: needed after reset

readSerialNr()
readCleaningInterval()

initialize()

while True:
  ret = readDataReady()
  if ret == -1:
    eprint('resetting...',end='')
    bigReset()
    initialize()
    continue

  if ret == 0:
    time.sleep(0.1)
    continue
  
  data = readPMValues()
  #send_data(data)
  print("PM10 :")
  data = calcFloat(data[18:24])
  pm10=data
  print(data)
  data = readPMValues()
  print("PM2.5 :")
  data = calcFloat(data[6:12])
  pm25=data
  print(data)
  time.sleep(20)
  ##############
  sql="insert into variables (PM10,PM25) values ('"+ str(pm10)+"','"+ str(pm25)+"')"
  print(sql)
  #"INSERT INTO datos (nombre,cedula,apellido,edad) "\
  #      "VALUES ('"+ str(nombre.get())+"',"\
  #      ""+ cedula.get()+",'"+ str(apellido.get())+"','"\
  #          ""+ str(edad.get())+"')")
  cursor1.execute(sql)
  
  conexion1.commit()
  #conexion1.close() 