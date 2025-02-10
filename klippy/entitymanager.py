# Entity manager
# Manages global instances (singletons) and printer objects
# global entities:
#   printer objects
#   reactor
#   gcode

import reactor

class EntityManager:

    def __init__(self, system_config):
        self.printers = {}
        self.reactor = None 

        # 1. read system_config
        # 2. create printer_objects

    def get_reactor(self):
        if self.reactor is None:
            self.reactor = reactor.Reactor(gc_checking=True)
        return self.reactor 

    def get_printer(self, printer_name):
        if printer_name in self.printers.keys():
            return self.printers[printer_name]