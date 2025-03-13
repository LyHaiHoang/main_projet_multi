"Motor Functions File, this file contain methods with motors of TRB25CC by using smc100v3 library"


import smc100v3 as smc
import serial

class Main_Motor():
    def __init__(self):
        super().__init__()        
        self.motors = smc.SMC100("123","COM6")
        print(self.motors._smcID)

        self.x_current = self.motors.get_position_um(1)
        self.y_current = self.motors.get_position_um(2)
        self.z_current = self.motors.get_position_um(3)
        
        print("current position = ("+str(self.x_current)+","+str(self.y_current)+","+str(self.z_current)+")")

        self.initial_position = None
        self.final_position = None
        self.current_position = None
        #self.current_position = (self.x_current, self.y_current, self.z_current)
        
    def set_speed(self,speed):   
        self.motors.set_speed_um(1,self.speed)
        self.motors.set_speed_um(2,self.speed)
        self.motors.set_speed_um(3,self.speed)
             
    def update_position(self):
        self.x_current = self.motors.get_position_um(1)
        self.y_current = self.motors.get_position_um(2)
        self.z_current = self.motors.get_position_um(3)
        return self.x_current, self.y_current, self.z_current
    
    # Function to set up positions of motors

    def reset_position(self):
        self.motors.home(1, 0, waitStop=True) 
        self.motors.home(2, 0, waitStop=True) 
        self.motors.home(3, 0, waitStop=True) 
        print("Motors returned to origin.")
        self.current_position = self.update_position()

    def get_initial_position(self):
        self.initial_position = self.update_position()
        print("Initial position is ",self.initial_position)
        return self.initial_position
    
    def get_final_position(self):
        self.final_position = self.update_position()
        print("Final position is ",self.final_position)
        return self.final_position
    
    def get_current_position(self):
        self.current_position = self.update_position()
        print("Current position is ",self.current_position)
        return self.current_position
    
    def move_motor_rlt(self,direction,step):
        x, y, z = self.update_position()
        
        def check_limit(pos,axis,limit):
            t = True
            if pos > limit or pos < -limit :
                print(f"Warning : Your motor at axis {axis} has reached its limit. It cannot move.")
                t = False
            return t

        if direction == "UP" :
            if check_limit(y+step,'Y',12000) :
                self.motors.move_relative_um(step,2)
        elif direction == "DOWN" :
            if check_limit(y-step,'Y',12000) :
                self.motors.move_relative_um(-step,2)
        elif direction == "LEFT" : 
            if check_limit(x-step, 'X',12000) :
                self.motors.move_relative_um(-step,1)
        elif direction == "RIGHT" :
            if check_limit(x+step,'X',12000) :
                self.motors.move_relative_um(step,1)
        elif direction == "Z-UP" :
            if check_limit(z+step,'Z',24000) : 
                self.motors.move_relative_um(step,3)
        elif direction == "Z-DOWN" :
            if check_limit(z-step,'Z',24000) :
                self.motors.move_relative_um(-step,3)      

    def stop_motor(self):
        for axis in [1, 2, 3]:
            self.motors.stop(axis) 
            #print("Motors stopped")
    