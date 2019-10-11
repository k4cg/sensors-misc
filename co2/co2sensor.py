#!/usr/bin/python3
#	
#	k4cg co2sensor
#	Copyright (C) 2019  Christian Carlowitz <chca@cmesh.de>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from time import sleep, time, localtime
from json import loads, dumps
from CO2Meter import CO2Meter
import paho.mqtt.client as mqtt

class Mqtt:
    def __init__(self, host, port, timeout, user, pw):
        self.connected = False
        self.cli = mqtt.Client()
        self.cli.on_connect = lambda cli,udata,flags,rc: self.on_connect()
        self.cli.username_pw_set(username=user, password=pw)
        self.cli.connect(host, port, timeout)

    def poll(self):
        self.cli.loop(timeout=0.1)

    def on_connect(self):
        self.connected = True

cfg = loads(open("co2auth.txt").read())
m = Mqtt("mqtt.intern.k4cg.org", 1883, 60, user=cfg["username"], pw=cfg["password"])
sensor = CO2Meter("/dev/hidraw0")

while not m.connected:
    m.poll()

d = sensor.get_data()
while len(d) < 2:
    sleep(0.1)
    d = sensor.get_data()

if ("co2" in d) and ("temperature" in d):
    co2 = d["co2"]
    temp = round(d["temperature"],1)
    tstr = "%d-%02d-%02dT%02d:%02d:%02d.000000" % localtime()[0:6]
    co2jdat = {"co2": co2, "_timestamp": int(time()), "_datestr": tstr}
    tempjdat =  {"co2temp": temp, "_timestamp": int(time()), "_datestr": tstr}
    m.cli.publish("sensors/co2sensor/default/co2", dumps(co2jdat))
    m.cli.publish("sensors/co2sensor/default/temp", dumps(tempjdat))

