import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from DataHandler import DataHandler

from matplotlib.figure import Figure
import mplcyberpunk
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
from threading import Thread
import time

class PlotHandler(Thread):
    LABEL = ['Voltage', 'Current', 'Power', 'Voltage Setpoint', 'Current Setpoint']
    STYLE = ['b-', 'r-', 'g-', 'b--', 'r--']

    def __init__(self, drawingArea: Gtk.Box) -> None:
        super().__init__()
        self.axis = []
        self.drawingArea = drawingArea
        self.stopCondition = False
        self.initPlot()

    def initPlot(self):
        plt.style.use("cyberpunk")
        self.axis = []
            self.axis.append(newAx)
        self.plot.grid(True)
        self.plot.set_xlabel('Time[s]')
        self.plot.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=True, ncol=5, title='Values', title_fontsize = 13, labels=PlotHandler.LABEL)
    
        for child in self.drawingArea.get_children():
            self.drawingArea.remove(child)
        self.drawingArea.pack_end(FigureCanvasGTK3Agg(self.figure),1,1,1)
        self.drawingArea.show_all()

    def updatePlot(self, data):
        try:
            for id, entry  in enumerate(DataHandler.DATA_ENTRIES[1:]):
                self.axis[id].set_xdata(data["time"])
                self.axis[id].set_ydata(data[entry])
            self.plot.set_xlim([0,data["time"][-1]])
            ymax = max([max(data[value]) for value in list(data.keys())][1:])
            self.plot.set_ylim([0,ymax])
            self.figure.canvas.draw_idle()
            
        except Exception as e:
            print("Could not update plot")
    
    def stop(self):
        self.stopCondition = True

    def run(self):
        while not self.stopCondition:
            time.sleep(1)
        