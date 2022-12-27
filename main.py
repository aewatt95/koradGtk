#!/usr/bin/python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from Handler import Handler

class KoradUi:
    def __init__(self) -> None:
        self.setupUi()
    
    def setupUi(self):
        builder = Gtk.Builder()
        builder.add_from_file("korad_ui.glade")

        self.window : Gtk.Window = builder.get_object("window")
        self.handler = Handler(builder)

    def run(self):
        self.window.show_all()
        Gtk.main()

if __name__ == "__main__":
    KoradUi().run()