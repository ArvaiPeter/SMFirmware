import logging 
import chelper
import math

class Ros:
    
    def __init__(self, config):
        logging.info("ROS2 interface startup...")
        self.config = config
        self.printer = config.get_printer()
        self.reactor = self.printer.reactor

        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        self.position = [0.0, 0.0, 0.0]

    def _handle_ready(self):
        self.toolhead = self.printer.lookup_object('toolhead', None)
        self.kinematics = self.toolhead.get_kinematics()
        self.steppers = self.kinematics.get_steppers()
        
        self.update_timer = self.reactor.register_timer(self.status_update, self.reactor.monotonic() + 10.0)

        self.ros = self.printer.start_args["ROS"]

        self.ffi_main, self.ffi_lib = chelper.get_ffi()
       
    
    def status_update(self, time):
        position = self.get_trapq_position(time)
        if position is not None:
            self.ros.publish_position(position)

        return time + 0.1
    
    def get_trapq_position(self, time):
        data = self.ffi_main.new(f"struct pull_move[1]")
        count = self.ffi_lib.trapq_extract_old(self.toolhead.get_trapq(), data, 1, 0.0, time)

        if not count:
            return None

        move = data[0]
        move_time = max(0.0, min(move.move_t, time- move.print_time))
        dist = (move.start_v + 0.5 * move.accel * move_time) * move_time
        pos = (move.start_x + move.x_r * dist,
               move.start_y + move.y_r * dist,
               move.start_z + move.z_r * dist)
        return pos 

    
    def get_curr_pos(self):
        cinfo = [(s.get_name(), s.get_mcu_position(), s.get_rotation_distance()) for s in self.steppers]
        return [self.convert_mcu_position(name, mcu, move_info)/1000 for name, mcu, move_info in cinfo] # mm to m

    def set_position(self, new_pos):
        self.position = new_pos

    def convert_mcu_position(self, name, pos, info):
        # MCU pos is the total number of steps taken in the positive direction minus the total numner of steps talen in the negative direction. This function converts this mcu pos based on printer kinematics (belts, pulleys, ...)
        # info = (rotation_dist, steps_per rotation)
        rotation_dist, steps_per_rotation = info
        
        return (pos / steps_per_rotation) * rotation_dist # mcu pos in mm



def load_config(config):
    return Ros(config)