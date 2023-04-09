import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from DataHandler import DataHandler
from PlotHandler import PlotHandler

import koradctl
import serial.tools.list_ports
import time
import os
import csv

class Handler:
    def __init__(self, builder: Gtk.Builder) -> None:
        self.powerSupply = None
        self.builder = builder
        self.builder.connect_signals(self)
        self.deviceComboBox : Gtk.ComboBoxText = self.builder.get_object("device_combo_box")
        self.graph : Gtk.Box = self.builder.get_object("graph")
        self.voltageSetpoint :Gtk.Adjustment = self.builder.get_object("voltage")
        self.currentSetpoint :Gtk.Adjustment = self.builder.get_object("current")
        self.ovp : Gtk.CheckButton = self.builder.get_object("ovp_toggle")
        self.ocp : Gtk.CheckButton = self.builder.get_object("ocp_toggle")
        self.latestVoltage : Gtk.Label =self.builder.get_object("latest_voltage")
        self.latestCurrent : Gtk.Label=self.builder.get_object("latest_current")
        self.latestPower : Gtk.Label=self.builder.get_object("latest_power")
        self.latestEnergy : Gtk.Label= self.builder.get_object("latest_energy")
        self.window : Gtk.Window = self.builder.get_object("window")
        
    def onCreate(self, *args):
        pass

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onDeviceDraw(self, *comboBox : (Gtk.ComboBoxText)):
        self.updateDeviceList()
        comboBox[0].set_model(self.deviceList)
        comboBox[0].set_active(0)

    def onConnectClick(self, *button : (Gtk.ToggleButton)):
        if button[0].get_active():
            try:
                self.powerSupply = koradctl.PowerSupply(koradctl.get_port(self.portNames[self.deviceComboBox.get_active()]))
                self.voltageSetpoint.set_value(self.powerSupply.get_voltage_setpoint().value)
                self.currentSetpoint.set_value(self.powerSupply.get_current_setpoint().value)
            except Exception as e:
                button[0].set_active(False)
                dialog = Gtk.MessageDialog(self.window, 
                Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, 
                Gtk.ButtonsType.CLOSE, f"Error connecting to device:\n{str(e)}")
                dialog.run()
                dialog.destroy()



    def onEnableClick(self, *button : (Gtk.ToggleButton)) :
        state = button[0].get_active()
        self.powerSupply.set_output_state(state)
        if state:
            self.dataHandler = DataHandler(self.powerSupply)
            self.plotHandler = PlotHandler(self.graph)
            self.dataHandler.connect('event', self.onDataRefresh)
            self.dataHandler.start()
        else:
            self.dataHandler.stop()

    def onVoltageChange(self, *voltage : (Gtk.Adjustment)) :
        print(voltage[0].get_value())
        self.powerSupply.set_voltage_setpoint(voltage[0].get_value())

    def onCurrentChange(self, *current : (Gtk.Adjustment)) :
        self.powerSupply.set_current_setpoint(current[0].get_value())

    def onXRangeChanged(self, *x_range : (Gtk.Adjustment)):
        self.plotHandler.timeFilter = int(x_range[0].get_value())

    def onOcpClick(self, *switch : (Gtk.CheckButton)) :
        self.powerSupply.set_ocp_state(switch[0].get_active())

    def onOvpClick(self, *switch : (Gtk.CheckButton)) :
        self.powerSupply.set_ovp_state(switch[0].get_active())

    def onShowSetpointChanged(self, *switch : (Gtk.Switch)):
        self.plotHandler.showSetpoints = switch[0].get_active()
        self.plotHandler.redrawTrigger = True

    def onDataRefresh(self, *parameter):
        self.plotHandler.updatePlot(self.dataHandler.data)
        self.latestVoltage.set_text(f"{self.dataHandler.data[DataHandler.DATA_ENTRIES[1]][-1]:.3}")
        self.latestCurrent.set_text(f"{self.dataHandler.data[DataHandler.DATA_ENTRIES[2]][-1]:.3}")
        self.latestPower.set_text(f"{self.dataHandler.data[DataHandler.DATA_ENTRIES[3]][-1]:.3}")
        self.latestEnergy.set_text(f"----")

    def onExportClick(self, *button : (Gtk.Button)):
        saveDialog = Gtk.FileChooserDialog( 
            action=Gtk.FileChooserAction.SAVE, 
            title="Export Data"
            )
        saveDialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, Gtk.ResponseType.OK)        
        saveDialog.set_do_overwrite_confirmation(True)
        saveDialog.set_current_name( os.path.basename("korad_export-%s.csv" % (time.strftime("%Y%m%d%H%M%S")) ))
        if not hasattr(self,'lastPath'):
            self.lastPath = os.path.expanduser("~")
        saveDialog.set_current_folder(self.lastPath)
        filter = Gtk.FileFilter()
        filter.set_name("CSV file")
        filter.add_pattern("*.csv")
        saveDialog.add_filter(filter)
        response = saveDialog.run()

        if response == Gtk.ResponseType.OK:
            filename = saveDialog.get_filename()
            self.lastPath = os.path.dirname(filename)
            with open(filename, 'w') as file:
                writer = csv.DictWriter(file, fieldnames=DataHandler.DATA_ENTRIES)
                writer.writeheader()
                writer.writerows(self.dataHandler.getDataAsDict())
        saveDialog.destroy()

    def updateDeviceList(self):
            self.portNames = []
            self.deviceList = Gtk.ListStore(str)
            for port, _, _ in serial.tools.list_ports.comports():
                self.portNames.append(port)
                self.deviceList.append([port])
            if len(self.deviceList) == 0:
                self.deviceList.append(["-- No device --"])
