# -*- coding: utf-8 -*-
import smbus
import time
import sys
import os
import netifaces as ni

# Define some device parameters
I2C_ADDR  = 0x38 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

dirname, filename = os.path.split(os.path.abspath(__file__))
tempfile = open(dirname + "/config")
serverIp = tempfile.read()
tempfile.close()

isServerIp = True
counter = 0

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
    
def setIp():
  global counter, isServerIp, serverIp
  localIp = 'no IP'
  
  net = ni.ifaddresses('wlan0')
  if 2 in net:
    localIp = net[2][0]['addr'] + ""
  
  if counter % 3 == 0:
    counter = 0
    cIp = ""
    if isServerIp:
      cIp = localIp 
    else: 
      cIp = serverIp
    isServerIp = not isServerIp
    lcd_string(cIp,LCD_LINE_2)

def main():
  global counter
  # Main program block

  # Initialise display
  lcd_init()
  
  lcd_string(serverIp,LCD_LINE_2)

  while True:
  	tempfile = open("/sys/bus/w1/devices/28-05167355eeff/w1_slave")
	text = tempfile.read()
	tempfile.close()
	tempdata = text.split("\n")[1].split(" ")[9]
	temp = float(tempdata[2:])
	temp = temp / 1000
	msg = "%.2f " % (temp) + chr(223) + "C"

    # Send some test
	lcd_string(msg, LCD_LINE_1)
	setIp()
	counter += 1
	  
	time.sleep(1)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)