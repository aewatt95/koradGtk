import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from threading import Thread
import koradctl
import time


class DataHandler(Thread, Gtk.Widget):
    DATA_ENTRIES = ["time", "voltage", "current", "power", "voltageSetpoint", "currentSetpoint"]

    def __init__(self, powerSupply: koradctl.PowerSupply) -> None:
        Thread.__init__(self)
        Gtk.Widget.__init__(self)
        self.refreshIntervall = 0.5
        self.powerSupply = powerSupply
        self.stopCondition = False
        self.data = {}
        for entry in DataHandler.DATA_ENTRIES:
            self.data[entry] = []

    def setRefreshIntervall(self, value: float):
        self.refreshIntervall = value

    def stop(self):
        self.stopCondition = True

    def getData(self):
        try:
            tmpData = self.powerSupply.get_output_readings()
            tmpVoltageSetpoint = self.powerSupply.get_voltage_setpoint().value
            tmpCurrentSetpoint = self.powerSupply.get_current_setpoint().value
            self.data[DataHandler.DATA_ENTRIES[0]].append(time.time() - self.startTime)
            self.data[DataHandler.DATA_ENTRIES[1]].append(tmpData[0].value)
            self.data[DataHandler.DATA_ENTRIES[2]].append(tmpData[1].value)
            self.data[DataHandler.DATA_ENTRIES[3]].append(tmpData[2].value)
            self.data[DataHandler.DATA_ENTRIES[4]].append(tmpVoltageSetpoint)
            self.data[DataHandler.DATA_ENTRIES[5]].append(tmpCurrentSetpoint)
        except Exception as e:
            print("Failed to get data point")

    def getDataAsDict(self):
        dataDict = []
        for counter in range(0, len(self.data["time"])):
                row = {}
                for key in self.data.keys():
                    row[key] = self.data[key][counter]
                dataDict.append(row)
        return dataDict

    def run(self) -> None:
        self.startTime = time.time()
        while not self.stopCondition:
            self.refreshTimeout = time.time()
            self.getData()
            self.emit('event', Gdk.Event())
            time.sleep(max(0, self.refreshIntervall - (time.time() - self.refreshTimeout)))
