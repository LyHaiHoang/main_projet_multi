
import sys 
import time
import smc100v3 as smc

import motor_functions as mot
import serial

import numpy as np
import math
from PyQt5 import uic
from PyQt5 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
from PyQt5.QtCore import pyqtSlot,pyqtSignal,Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QWidget, QDesktopWidget, QCheckBox

Ui_MainWindow, QtBaseClass = uic.loadUiType("Face_avant_Acquisition.ui")


"py -m PyQt5.uic.pyuic -x Face_avant_Acquisition.ui -o Face_avant_Acquisition.py"
        
        
class MainWindowFinal(qtw.QMainWindow,Ui_MainWindow):


    def __init__(self): 
        super(MainWindowFinal,self).__init__() 
        
        
        self.i=0
        self.setupUi(self)
        
        self.pushButtonQuit.clicked.connect(self.CB_quitter)      
        self.pushButtonStartAcquisition.clicked.connect(self.CB_StartAcquisition)
        
        
        self.pushButtonUp.clicked.connect(lambda: self.Motor.move_motor_rlt("UP",self.Motor.step))
        self.pushButtonDown.clicked.connect(lambda: self.Motor.move_motor_rlt("DOWN",self.Motor.step))
        self.pushButtonLeft.clicked.connect(lambda: self.Motor.move_motor_rlt("LEFT",self.Motor.step))
        self.pushButtonRight.clicked.connect(lambda: self.Motor.move_motor_rlt("RIGHT",self.Motor.step))
        self.pushButtonZUp.clicked.connect(lambda: self.Motor.move_motor_rlt("Z-UP",self.Motor.step))
        self.pushButtonZDown.clicked.connect(lambda : self.Motor.move_motor_rlt("Z-DOWN",self.Motor.step))
        
        self.pushButtonReset.clicked.connect(self.CB_ResetPosition)
        self.pushButtonGetIPosition.clicked.connect(self.CB_GetInitialPosition)
        self.pushButtonGetFPosition.clicked.connect(self.CB_GetFinalPosition)
        self.pushButtonGetCPosition.clicked.connect(self.CB_GetCurrentPosition)
        self.pushButtonSetStep.clicked.connect(self.CB_SetStep)
        self.pushButtonSetSpeed.clicked.connect(self.CB_SetSpeed)
        self.checkBoxFastMovement.stateChanged.connect(self.CB_FastMovement)
        self.pushButtonStopAcquisition.clicked.connect(self.CB_StopAcquisition)

        self.Init_Materials()
        self.Init_Parameters()
        

    def Init_Materials(self):
        
        self.Motor = mot.Main_Motor()
        

    def Init_Parameters(self):
        
        self.Motor.initial_position = None
        self.Motor.final_position = None
        self.Motor.current_position = None
        self.Motor.step = 200
        self.Motor.speed = 200
        

    def CB_FastMovement(self, state):
        if state == Qt.Checked:
         
            self.Motor.set_speed(1000)
            self.plainTextEdit_Terminal.appendPlainText(f"Set speed is 1000 (um/s)")

        else:
            self.Motor.set_speed(10)
            self.plainTextEdit_Terminal.appendPlainText(f"Set speed is 10 (um/s)")
            
    
    
    def CB_ResetPosition(self):
        self.Motor.reset_position()
        self.plainTextEdit_Terminal.appendPlainText(f"Motors are returned origine ")

    def CB_GetInitialPosition(self,event):
        pos = self.Motor.get_initial_position()
        self.textEdit_IPosition.setText(str(pos))
    
    def CB_GetFinalPosition(self,event):
        pos = self.Motor.get_final_position()
        self.textEdit_FPosition.setText(str(pos))

    def CB_GetCurrentPosition(self,event):
        pos = self.Motor.get_current_position()
        self.textEdit_Position_Current.setText(str(pos))

    def CB_SetStep(self):
        self.Motor.step = int(self.lineEdit_Step.text())
        self.plainTextEdit_Terminal.appendPlainText(f"Step = {self.Motor.step} (um) ")
    
    def CB_SetSpeed(self):
        self.Motor.speed = int(self.lineEdit_Speed.text())
        self.plainTextEdit_Terminal.appendPlainText(f"Speed = {self.Motor.speed} (um/s) ")
    
    def CB_quitter(self,event):
        self.close()

    def CB_StopAcquisition(self):
        self.Motor.stop_motor()
        self.plainTextEdit_Terminal.appendPlainText(f"Motors stopped")
    
    # When button "Start Acquisition" pushed, the acquisition begins.
    def CB_StartAcquisition(self, event):
        
        if self.Motor.initial_position is None or self.Motor.final_position is None:
               print("You must set region of your image that you want to capture")
               return
        
        if self.Motor.initial_position == self.Motor.final_position:           #A MODIFIER avec les bonnes variables
            QMessageBox.warning(self, "Warning", "Initial position and Final position are the same.", QMessageBox.Ok)
        else:

            #1.1 se placer à position initiale
            self.Motor.motors.move_absolute_um(self.Motor.initial_position[0], 1, waitStop=True)
            self.Motor.motors.move_absolute_um(self.Motor.initial_position[1], 2, waitStop=True)


            
            # Set variables for initial and final position
            x_start, y_start, z_start = self.Motor.initial_position
            x_end, y_end, z_end = self.Motor.final_position
          
            # Return initial position

            self.Motor.motors.move_absolute_um(x_start, 1, waitStop=True)
            self.Motor.motors.move_absolute_um(y_start, 2, waitStop=True)
            
            self.x_current, self.y_current = x_start, y_start

            # Get size of image by using camera Amscope
            self.step_size_x = 950
            self.step_size_y = 710
            self.step_size_z = 1000
  
          
          
            # Set directions for automatic scanning
            direction_x = np.sign(x_end - x_start)
            direction_y = np.sign(y_end - y_start)

            # calcule step number of x and y direction for scanning
            nb_x_step = math.ceil(abs(x_end - x_start) / self.step_size_x)
            nb_y_step = math.ceil(abs(y_end - y_start) / self.step_size_y)

          # Start loop for scanning (y_steps times for ligne and x_steps times for column)

        #self.task = mot.Motion_RLT()  

        for y_step in range(nb_y_step + 1):

            for x_step in range(nb_x_step):
                
                self.Motor.motors.move_relative_um(direction_x*self.step_size_x, 1, waitStop=True) 
                #self.Motor.update_position()
                #self.task.run(direction_x*self.task.STEP) 
                #self.task.signal.connect(self.Motor.update_position)
                #self.threadpool.start(self.task)
                    
            self.Motor.motors.move_relative_um(direction_y*self.step_size_y, 2, waitStop=True) 
            #self.Motor.update_position()
            #self.y_current +=  direction_y *(self.step_size_y) 
            #self.task.run()
            #self.task.signal.connect(self.Motor.update_position)
            #self.threadpool.start(self.task)
                    
               
            direction_x *= -1
            
        self.plainTextEdit_Terminal.appendPlainText(f"Scanning finished")
            

if __name__=='__main__':
    app=qtw.QApplication(sys.argv)
    test=MainWindowFinal()
    test.show()
    app.exec()       

"Ok"