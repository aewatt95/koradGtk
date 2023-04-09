import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from DataHandler import DataHandler

from matplotlib.figure import Figure
from matplotlib.axes import Axes 
import matplotlib.pyplot as plt
import mplcyberpunk
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
from threading import Thread
import time

class PlotHandler(Thread):

    LABEL = ['Voltage', 'Current', 'Power', 'Voltage Setpoint', 'Current Setpoint']
    STYLE = ['b-', 'r-', 'g-', 'b--', 'r--']

    def __init__(self, drawingArea: Gtk.Box, showSetpoints = False, showLegend = True) -> None:
        super().__init__()
        self.drawingArea = drawingArea
        self.stopCondition = False
        self.timeFilter = 60
        self.showSetpoints = showSetpoints
        self.showLegend = showLegend
        self.redrawTrigger = False
        self.initPlot()

    def initPlot(self):
        plt.style.use("cyberpunk")
        self.axis = []
        self.figure = Figure(figsize=(10,6), tight_layout=True)
        self.plot : Axes = self.figure.add_subplot()
        for id, lineSettings in enumerate(PlotHandler.STYLE):
            if not self.showSetpoints and id > 2:
                break
            newAx, = self.plot.plot([],[], linewidth=2)
            self.axis.append(newAx)
        self.plot.grid(True)
        self.plot.set_xlabel('Time[s]')
        if self.showLegend:
            self.plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
            fancybox=True, shadow=True, ncol=5, title='Values', title_fontsize = 13, labels=PlotHandler.LABEL)
    
        for child in self.drawingArea.get_children():
            self.drawingArea.remove(child)
        self.drawingArea.pack_end(FigureCanvasGTK3Agg(self.figure),1,1,1)
        self.drawingArea.show_all()


    def updatePlot(self, data):
        try:
            if self.redrawTrigger:
                self.initPlot()
                self.redrawTrigger = False
            yMinIndex = min(range(len(data["time"])), key=lambda i: abs(data["time"][i]-self.timeFilter))
            for id, entry  in enumerate(DataHandler.DATA_ENTRIES[1:]):
                if not self.showSetpoints and id > 2:
                    break
                self.axis[id].set_xdata(data["time"][-yMinIndex:])
                self.axis[id].set_ydata(data[entry][-yMinIndex:])

            self.plot.set_xlim([data["time"][-yMinIndex:][0],data["time"][-1]])
            ymax = max([max(data[value]) for value in list(data.keys())][1:])

            self.plot.set_ylim([0,ymax])
            self.figure.canvas.draw_idle()
            
        except Exception as e:
            print("Could not update plot")
            self.initPlot()
    
    def stop(self):
        self.stopCondition = True

    def run(self):
        while not self.stopCondition:
            time.sleep(1)
        