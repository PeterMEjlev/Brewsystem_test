import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# =============================================================================
# from w1thermsensor import W1ThermSensor, SensorNotReadyError
# =============================================================================
import datetime
from datetime import date
# =============================================================================
#import RPi.GPIO as GPIO
# =============================================================================
import pygsheets
import pandas as pd
from pygsheets.datarange import DataRange
import time
import random
import os

import StaticGUI

# =============================================================================
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM)

#GPIO_17_BK_POWER = 17
#GPIO_27_HLT_POWER = 27
#GPIO_12_BK_PWM = 12
#GPIO_13_HLT_PWM = 13

#GPIO.setup(GPIO_17_BK_POWER, GPIO.OUT)
#GPIO.setup(GPIO_27_HLT_POWER, GPIO.OUT)
#GPIO.setup(GPIO_12_BK_PWM, GPIO.OUT)
#GPIO.setup(GPIO_13_HLT_PWM, GPIO.OUT)

#GPIO.output(GPIO_17_BK_POWER, GPIO.LOW)
#GPIO.output(GPIO_27_HLT_POWER, GPIO.LOW)
PWM_frequency = 100
#PWM_BK = GPIO.PWM(GPIO_12_BK_PWM, PWM_frequency) #Initialize PWM with 100 Hz (pin 12)
#PWM_HLT = GPIO.PWM(GPIO_13_HLT_PWM, PWM_frequency) #Initialize PWM with 100 Hz (pin 13)


# =============================================================================


degree_sign = u'\N{DEGREE SIGN}'

#Initialize neccesary variables
HLT_buttonPressed = False
HLT_buttonToggle = False
HLT_PowerPressed = False
HLT_PowerToggle = False

MLT_LoggingPressed = False
MLT_LoggingToggle = False
LOG_PowerPressed = False
LOG_PowerToggle = False

BK_PowerPressed = False
BK_PowerToggle = False
HLT_PowerPressed = False
HLT_PowerToggle = False

triangleUp_buttonPressed = False
triangleDown_buttonPressed = False

bk_sv_up_pressed = False
bk_sv_down_pressed = False
bk_dc_up_pressed = False
bk_dc_down_pressed = False

hlt_sv_up_pressed = False
hlt_sv_down_pressed = False
hlt_dc_up_pressed = False
hlt_dc_down_pressed = False

pump_dc_up_pressed = False
pump_dc_down_pressed = False
pump1_selected = False
pump2_selected = False

quit_buttonPressed = False
quitDialogBoxCancelPressed = False
quitDialogBoxQuitPressed = False

HLT_REG = False
BK_REG = False
LOG = False
LOG_buttonPressed = False
LOG_buttonToggle = False

HLT_GPIO_Power = False
BK_GPIO_Power = False

BK_SV = 77
BK_DC = 100
HLT_SV = 72
HLT_DC = 37

HLT_PV = 10
MLT_PV = 10
BK_PV =  10


#PUMP PWM (SOFTWARE)
pump1_MLT_DC = 50
pump2_HLT_DC = 50

pump_pwm_freq = 200

pump_1_mlt_pin = 23
pump_2_hlt_pin = 25

#GPIO.setup(pump_1_mlt_pin, GPIO.OUT)
#GPIO.setup(pump_2_hlt_pin, GPIO.OUT)

#soft_pwm_pump_1 = GPIO.PWM(pump_1_mlt_pin,pump_pwm_freq) # (pin, frequency)
#soft_pwm_pump_2 = GPIO.PWM(pump_2_hlt_pin,pump_pwm_freq) # (pin, frequency)

#soft_pwm_pump_1.start(pump_1_mlt_pin) #(DC)
#soft_pwm_pump_1.ChangeDutyCycle(pump1_MLT_DC) #Updates to the set DC

#soft_pwm_pump_2.start(pump_2_hlt_pin) #(DC)
#soft_pwm_pump_2.ChangeDutyCycle(pump2_HLT_DC) #Updates to the set DC

BK_Time_mins = 32
BK_Time_seconds = 0

increment_amount = 1

sensor_HLT = "3c01b556f06d"
sensor_BK = "3c01b556163d"
temp_sensorHLT = 0
temp_sensorMLT = 0
temp_sensorBK = 0

temp_data = []
temp_data_i = 0
temp_flag = False

imagePath = r"C:\Users\Torsten\Desktop\newGUI_files/"


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.threadpool = QThreadPool()
        
        self.mashingWindow = MashingWindow()
        self.settingsWindow = SettingsWindow()
        MainWindow.pumpsWindow = PumpsWindow()
        
        
        global worksheet

        self.setWindowTitle("Brew System")
        self.setGeometry(0,0,800,480)
        self.setWindowFlag(Qt.FramelessWindowHint)
# =============================================================================
#         self.resetOutputs()
# =============================================================================
        
        StaticGUI.initStaticGUI_Heating(self)
        self.initDynamicGUI()
# =============================================================================
        self.showFullScreen()
#        self.setCursor(Qt.BlankCursor)
# =============================================================================
# =============================================================================
#        worksheet = self.setUpGoogleSheets()
# =============================================================================
         
        self.show()
        
        
        #self.timerUpdateTemp = QTimer()
        #self.timerUpdateTemp.setInterval(1000)
        #self.timerUpdateTemp.timeout.connect(self.startThread1)
        #self.timerUpdateTemp.start()
        
        
    
    

    
    def startThread1(self): # Function run by timer every 1 second
        thread1 = Thread1(self.updateTempLabels)
        self.threadpool.start(thread1)
        
    
    
    def updateTempLabels(self):
        global temp_sensorHLT
        global temp_sensorBK
        global HLT_SV, BK_SV
        global HLT_REG, BK_REG
        global temp_data
        global temp_flag
        
        now = datetime.datetime.now()
        
        for sensor in W1ThermSensor.get_available_sensors():
            
            if sensor.id == sensor_HLT:
                try:
                    temp_sensorHLT = round(sensor.get_temperature(),1)
                    MainWindow.txt_HLT_PV.setText(str(temp_sensorHLT) + degree_sign)
                    MashingWindow.txt_HLT_PV.setText(str(temp_sensorHLT) + degree_sign)
                    
                    if HLT_REG == True:
                        if temp_sensorHLT <= HLT_SV:
                            self.turnOnHLTPower()
                        elif temp_sensorHLT > HLT_SV:
                            self.turnOffHLTPower()
   
                except SensorNotReadyError:
                    print("Sensor not ready to read")
                    
            elif sensor.id == sensor_BK:
                try:
                    temp_sensorBK = round(sensor.get_temperature(),1)
                    MainWindow.txt_BK_temp.setText(str(temp_sensorBK) + degree_sign)
                    BoilingWindow.txt_BK_temp.setText(str(temp_sensorBK) + degree_sign)
                    
                    if BK_REG == True:
                        if temp_sensorBK <= BK_SV:
                            self.turnOnBKPower()
                        elif temp_sensorBK > BK_SV:
                            self.turnOffBKPower()
                    
                    self.checkBKTime()
                    
                except SensorNotReadyError:
                    print("Sensor not ready to read")
    
        if LOG == True & temp_flag == True:
            timestamp = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
            temp_data.append([timestamp, temp_sensorHLT , temp_sensorMLT, temp_sensorBK])
            temp_flag = False
            
        elif temp_flag == False   :
            temp_flag = True
               
    
    
        
    def turnOnHLTPower():
        global GPIO_27_HLT_POWER
        global GPIO_13_HLT_PWM, PWM_HLT, HLT_DC

        
        if not GPIO.input(GPIO_27_HLT_POWER): #if GPIO 18 (HLT Power) is not high
            GPIO.output(GPIO_27_HLT_POWER, GPIO.HIGH)
            PWM_HLT.start(HLT_DC)
            updateIndicators()
            updateIcons()
    
    def turnOffHLTPower():
        global GPIO_27_HLT_POWER
        global GPIO_13_HLT_PWM, PWM_HLT, HLT_DC
        
        if GPIO.input(GPIO_27_HLT_POWER): #if GPIO 18 (HLT Power) is high
            GPIO.output(GPIO_27_HLT_POWER, GPIO.LOW)
            PWM_HLT.stop()
            updateIndicators()
            updateIcons()

    def turnOnBKPower():
        global GPIO_17_BK_POWER
        global GPIO_12_BK_PWM, PWM_BK, BK_DC
        
        if not GPIO.input(GPIO_17_BK_POWER): #if GPIO 12 (BK Power) is not high
            GPIO.output(GPIO_17_BK_POWER, GPIO.HIGH)
            PWM_BK.start(BK_DC)
            updateIndicators()
            updateIcons()
  
    def turnOffBKPower():
        global GPIO_17_BK_POWER
        global GPIO_12_BK_PWM, PWM_BK, BK_DC
        
        if GPIO.input(GPIO_17_BK_POWER): #if GPIO 12 (BK Power) is high
            GPIO.output(GPIO_17_BK_POWER, GPIO.LOW)
            PWM_BK.stop()
            updateIndicators()
            updateIcons()
            
    def checkBKTime(self):
        global temp_sensorBK
        global BK_Time_seconds
        global BK_Time_mins
        
        if BK_Time_seconds == 60:
            BK_Time_mins += 1
            self.txt_BK_time.setText("Time: " + str(BK_Time_mins) + " min")
            self.txt_BK_temp.adjustSize()
            BK_Time_seconds = 0
            
        elif temp_sensorBK > 96:
            BK_Time_seconds += 1        
        
        
    def create_button(self, image_name, size, position, mouse_press_event=None, mouse_release_event=None):
        btn = QLabel(self)
        btn.setPixmap(QPixmap(imagePath + image_name).scaled(size[0], size[1], transformMode = Qt.SmoothTransformation))
        btn.move(position[0], position[1])
        btn.adjustSize()
        if mouse_press_event:
            btn.mousePressEvent = mouse_press_event
        if mouse_release_event:
            btn.mouseReleaseEvent = mouse_release_event
        return btn
        
    def initDynamicGUI(self):
        print("Dynamic GUI Initializing...")
        
        self.btn_title_heating = self.create_button("title_heating.png", [318, 82], [235,11], self.showMashingWindow)
        self.btn_settings = self.create_button("btn_settings.png", [104, 72], [679,11], self.showSettingsWindow)
        self.showPumpsWindow = self.create_button("btn_pump.png", [104, 72], [16,11], showPumpsWindow)

        self.indicator_B = self.create_button("indicator_B_off.png", [47, 72], [129,11])        
        self.indicator_B = self.create_button("indicator_H_off.png", [47, 72], [179,11])      
        
        self.increment = self.create_button("increment_1.png", [104, 72], [564,11], changeIncrementAmount, changeIncrementAmount)      

        
        #Boil Kettle
        print("BK")
        self.btn_up_bk_temp = self.create_button("btn_up.png", [70, 70], [28,184], increase_BK_SV, increase_BK_SV)      
        

        
        MainWindow.btn_down_bk_temp = QLabel(self)
        MainWindow.btn_down_bk_temp.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_down_bk_temp.move(106,184)
        MainWindow.btn_down_bk_temp.adjustSize()
        MainWindow.btn_down_bk_temp.mousePressEvent = decrease_BK_SV
        MainWindow.btn_down_bk_temp.mouseReleaseEvent = decrease_BK_SV
        
        MainWindow.btn_up_bk_dc = QLabel(self)
        MainWindow.btn_up_bk_dc.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_up_bk_dc.move(28,294)
        MainWindow.btn_up_bk_dc.adjustSize()
        MainWindow.btn_up_bk_dc.mousePressEvent = increase_BK_DC
        MainWindow.btn_up_bk_dc.mouseReleaseEvent = increase_BK_DC
        
        MainWindow.btn_down_bk_dc = QLabel(self)
        MainWindow.btn_down_bk_dc.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_down_bk_dc.move(106,294)
        MainWindow.btn_down_bk_dc.adjustSize()
        MainWindow.btn_down_bk_dc.mousePressEvent = decrease_BK_DC
        MainWindow.btn_down_bk_dc.mouseReleaseEvent = decrease_BK_DC
        
        MainWindow.btn_power_bk = QLabel(self)
        MainWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_power_bk.move(28,380)
        MainWindow.btn_power_bk.adjustSize()
        MainWindow.btn_power_bk.mousePressEvent = update_btn_BKPower
        MainWindow.btn_power_bk.mouseReleaseEvent = update_btn_BKPower
         
        MainWindow.icon_lightning_bk = QLabel(self)
        MainWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.icon_lightning_bk.move(307,380)
        MainWindow.icon_lightning_bk.adjustSize()
        MainWindow.icon_lightning_bk.mousePressEvent = self.showMashingWindow
        
        
        #Hot Liquor Tank
        MainWindow.btn_up_hlt_temp = QLabel(self)
        MainWindow.btn_up_hlt_temp.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_up_hlt_temp.move(419,184)
        MainWindow.btn_up_hlt_temp.adjustSize()
        MainWindow.btn_up_hlt_temp.mousePressEvent = increase_HLT_SV
        MainWindow.btn_up_hlt_temp.mouseReleaseEvent = increase_HLT_SV
        
        MainWindow.btn_down_hlt_temp = QLabel(self)
        MainWindow.btn_down_hlt_temp.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_down_hlt_temp.move(497,184)
        MainWindow.btn_down_hlt_temp.adjustSize()
        MainWindow.btn_down_hlt_temp.mousePressEvent = decrease_HLT_SV
        MainWindow.btn_down_hlt_temp.mouseReleaseEvent = decrease_HLT_SV
        
        MainWindow.btn_up_hlt_dc = QLabel(self)
        MainWindow.btn_up_hlt_dc.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_up_hlt_dc.move(419,294)
        MainWindow.btn_up_hlt_dc.adjustSize()
        MainWindow.btn_up_hlt_dc.mousePressEvent = increase_HLT_DC
        MainWindow.btn_up_hlt_dc.mouseReleaseEvent = increase_HLT_DC
        
        MainWindow.btn_down_hlt_dc = QLabel(self)
        MainWindow.btn_down_hlt_dc.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_down_hlt_dc.move(497,294)
        MainWindow.btn_down_hlt_dc.adjustSize()
        MainWindow.btn_down_hlt_dc.mousePressEvent = decrease_HLT_DC
        MainWindow.btn_down_hlt_dc.mouseReleaseEvent = decrease_HLT_DC
        
        MainWindow.btn_power_hlt = QLabel(self)
        MainWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
        MainWindow.btn_power_hlt.move(419,380)
        MainWindow.btn_power_hlt.adjustSize()
        MainWindow.btn_power_hlt.mousePressEvent = update_btn_HLTPower
        MainWindow.btn_power_hlt.mouseReleaseEvent = update_btn_HLTPower
        
        MainWindow.icon_lightning_hlt = QLabel(self)
        MainWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MainWindow.icon_lightning_hlt.move(698,380)
        MainWindow.icon_lightning_hlt.adjustSize()
    
        MainWindow.txt_BK_SV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MainWindow.txt_BK_SV.setGraphicsEffect(colour_white)
        MainWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign + "  ")
        MainWindow.txt_BK_SV.setFont(QFont("Bahnschrift", 32))
        MainWindow.txt_BK_SV.move(197, 195)
        MainWindow.txt_BK_SV.adjustSize()
        
        MainWindow.txt_BK_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MainWindow.txt_BK_PV.setGraphicsEffect(colour_white)
        MainWindow.txt_BK_PV.setText(str(BK_PV) + degree_sign + "  ")
        MainWindow.txt_BK_PV.setFont(QFont("Bahnschrift", 32))
        MainWindow.txt_BK_PV.move(300, 195)
        MainWindow.txt_BK_PV.adjustSize()
        
        MainWindow.txt_BK_DC = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MainWindow.txt_BK_DC.setGraphicsEffect(colour_white)
        MainWindow.txt_BK_DC.setText(str(BK_DC) + "%" + "  "  )
        MainWindow.txt_BK_DC.setFont(QFont("Bahnschrift", 45))
        MainWindow.txt_BK_DC.move(198, 295)
        MainWindow.txt_BK_DC.adjustSize()
        
        
        MainWindow.txt_HLT_SV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MainWindow.txt_HLT_SV.setGraphicsEffect(colour_white)
        MainWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign + "  ")
        MainWindow.txt_HLT_SV.setFont(QFont("Bahnschrift", 32))
        MainWindow.txt_HLT_SV.move(585, 195)
        MainWindow.txt_HLT_SV.adjustSize()
        
        MainWindow.txt_HLT_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MainWindow.txt_HLT_PV.setGraphicsEffect(colour_white)
        MainWindow.txt_HLT_PV.setText(str(HLT_PV) + degree_sign + "  ")
        MainWindow.txt_HLT_PV.setFont(QFont("Bahnschrift", 32))
        MainWindow.txt_HLT_PV.move(688, 195)
        MainWindow.txt_HLT_PV.adjustSize()
        
        MainWindow.txt_HLT_DC = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MainWindow.txt_HLT_DC.setGraphicsEffect(colour_white)
        MainWindow.txt_HLT_DC.setText(str(HLT_DC) + "%" + "     " )
        MainWindow.txt_HLT_DC.setFont(QFont("Bahnschrift", 45))
        MainWindow.txt_HLT_DC.move(605, 295)
        MainWindow.txt_HLT_DC.adjustSize()


            
    
    
    def setUpGoogleSheets(self):
        print("Setting up Google Sheets...")
        now = datetime.datetime.now()
        date = date.today()
        SheetsPath=r"C:/Users/Torsten/Desktop/RPI/GUI_files/essential-storm-330816-8d59b88e4708.json"
        gc=pygsheets.authorize(service_account_file = SheetsPath)

        googleSheet = gc.open('Python Test')
        
        try:
            worksheet = googleSheet.add_worksheet(date, rows=20, cols=12)
        except: #If name already exist -> concatenate random int 
            name = date + str(random.randrange(1000))
            worksheet = googleSheet.add_worksheet(name , rows=20, cols=12)
    
        worksheet.update_value('A2', 'Timestamp') 
        worksheet.update_value('B2', 'HLT Temp')  
        worksheet.update_value('C2', 'MLT Temp')  
        worksheet.update_value('D2', 'BK Temp')  

        
        return worksheet

    def showMashingWindow(self, checked):
        if self.mashingWindow.isVisible():
            self.mashingWindow.hide()

        else:
            self.mashingWindow.show()

            
            
    def showSettingsWindow(self, checked):
        if self.settingsWindow.isVisible():
            self.settingsWindow.hide()

        else:
            self.settingsWindow.show()
            
  
class Thread1(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Thread1, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)

class Thread2(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Thread2, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)       



class MashingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.boilingWindow = BoilingWindow()
        #self.setWindowTitle("Brew System")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(800,480)
        #self.setCursor(Qt.BlankCursor)
        MashingWindow.threadpool = QThreadPool()
        self.settingsWindow = SettingsWindow()
        self.pumpsWindow = PumpsWindow()
        

        StaticGUI.initStaticGUI_Mashing(self)
        
        MashingWindow.indicator_B = QLabel(self)
        MashingWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.indicator_B.move(129,11)
        MashingWindow.indicator_B.adjustSize()
        
        MashingWindow.indicator_H = QLabel(self)
        MashingWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.indicator_H.move(179,11)
        MashingWindow.indicator_H.adjustSize()
        
        MashingWindow.increment = QLabel(self)
        MashingWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.increment.move(564,11)
        MashingWindow.increment.adjustSize()
        MashingWindow.increment.mousePressEvent = changeIncrementAmount
        
        self.txt_MLT_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        self.txt_MLT_PV.setGraphicsEffect(colour_white)
        self.txt_MLT_PV.setText(str(MLT_PV) + degree_sign + "     " )
        self.txt_MLT_PV.setFont(QFont("Bahnschrift", 130))
        self.txt_MLT_PV.move(55, 165)
        self.txt_MLT_PV.adjustSize()
        
        MashingWindow.txt_HLT_SV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MashingWindow.txt_HLT_SV.setGraphicsEffect(colour_white)
        MashingWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
        MashingWindow.txt_HLT_SV.setFont(QFont("Bahnschrift", 32))
        MashingWindow.txt_HLT_SV.move(585, 195)
        MashingWindow.txt_HLT_SV.adjustSize()
        
        MashingWindow.txt_HLT_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MashingWindow.txt_HLT_PV.setGraphicsEffect(colour_white)
        MashingWindow.txt_HLT_PV.setText(str(HLT_PV) + degree_sign)
        MashingWindow.txt_HLT_PV.setFont(QFont("Bahnschrift", 32))
        MashingWindow.txt_HLT_PV.move(688, 195)
        MashingWindow.txt_HLT_PV.adjustSize()
        
        MashingWindow.txt_HLT_DC = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        MashingWindow.txt_HLT_DC.setGraphicsEffect(colour_white)
        MashingWindow.txt_HLT_DC.setText(str(HLT_DC) + "%" + "     " )
        MashingWindow.txt_HLT_DC.setFont(QFont("Bahnschrift", 45))
        MashingWindow.txt_HLT_DC.move(605, 295)
        MashingWindow.txt_HLT_DC.adjustSize()
        
        MashingWindow.btn_up_hlt_temp = QLabel(self)
        MashingWindow.btn_up_hlt_temp.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.btn_up_hlt_temp.move(419,184)
        MashingWindow.btn_up_hlt_temp.adjustSize()
        MashingWindow.btn_up_hlt_temp.mousePressEvent = increase_HLT_SV
        MashingWindow.btn_up_hlt_temp.mouseReleaseEvent = increase_HLT_SV
        
        MashingWindow.btn_down_hlt_temp = QLabel(self)
        MashingWindow.btn_down_hlt_temp.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.btn_down_hlt_temp.move(497,184)
        MashingWindow.btn_down_hlt_temp.adjustSize()
        MashingWindow.btn_down_hlt_temp.mousePressEvent = decrease_HLT_SV
        MashingWindow.btn_down_hlt_temp.mouseReleaseEvent = decrease_HLT_SV
        
        MashingWindow.btn_up_hlt_dc = QLabel(self)
        MashingWindow.btn_up_hlt_dc.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.btn_up_hlt_dc.move(419,294)
        MashingWindow.btn_up_hlt_dc.adjustSize()
        MashingWindow.btn_up_hlt_dc.mousePressEvent = increase_HLT_DC
        MashingWindow.btn_up_hlt_dc.mouseReleaseEvent = increase_HLT_DC
        
        MashingWindow.btn_down_hlt_dc = QLabel(self)
        MashingWindow.btn_down_hlt_dc.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.btn_down_hlt_dc.move(497,294)
        MashingWindow.btn_down_hlt_dc.adjustSize()
        MashingWindow.btn_down_hlt_dc.mousePressEvent = decrease_HLT_DC
        MashingWindow.btn_down_hlt_dc.mouseReleaseEvent = decrease_HLT_DC
        
        self.btn_title_mashing = QLabel(self)
        self.btn_title_mashing.setPixmap(QPixmap(imagePath + "title_mashing.png").scaled(318, 82, transformMode = Qt.SmoothTransformation))
        self.btn_title_mashing.move(235,11)
        self.btn_title_mashing.adjustSize()
        self.btn_title_mashing.mousePressEvent = self.showBoilingWindow
        
        self.btn_settings = QLabel(self)
        self.btn_settings.setPixmap(QPixmap(imagePath + "btn_settings.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        self.btn_settings.move(679,11)
        self.btn_settings.adjustSize()
        self.btn_settings.mousePressEvent = self.showSettingsWindow
        
        self.btn_pumps = QLabel(self)
        self.btn_pumps.setPixmap(QPixmap(imagePath + "btn_pump.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        self.btn_pumps.move(16,11)
        self.btn_pumps.adjustSize()
        self.btn_pumps.mousePressEvent = showPumpsWindow

        
        
        MashingWindow.btn_logging_mlt = QLabel(self)
        MashingWindow.btn_logging_mlt.setPixmap(QPixmap(imagePath + "btn_logging_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
        MashingWindow.btn_logging_mlt.move(28,380)
        MashingWindow.btn_logging_mlt.adjustSize()
        MashingWindow.btn_logging_mlt.mousePressEvent = update_btn_LOG
        MashingWindow.btn_logging_mlt.mouseReleaseEvent = update_btn_LOG
        
        MashingWindow.icon_cloud_mlt = QLabel(self)
        MashingWindow.icon_cloud_mlt.setPixmap(QPixmap(imagePath + "icon_cloud.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.icon_cloud_mlt.move(307,380)
        MashingWindow.icon_cloud_mlt.adjustSize()
        
        MashingWindow.btn_power_hlt = QLabel(self)
        MashingWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
        MashingWindow.btn_power_hlt.move(419,380)
        MashingWindow.btn_power_hlt.adjustSize()
        MashingWindow.btn_power_hlt.mousePressEvent = update_btn_HLTPower
        MashingWindow.btn_power_hlt.mouseReleaseEvent = update_btn_HLTPower
        
        MashingWindow.icon_lightning_hlt = QLabel(self)
        MashingWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.icon_lightning_hlt.move(698,380)
        MashingWindow.icon_lightning_hlt.adjustSize()
        
        
        
    def startThread2(self): # Function run by timer every 1 second
        global temp_data
        thread2 = Thread2(log2sheets, temp_data)
        self.threadpool.start(thread2)
    
            
    def increase_HLT_DC_Mashing(self, NaN):
        global hlt_dc_up_pressed
        global HLT_DC
        global BK_DC
        
        if hlt_dc_up_pressed == False and HLT_DC < 100: #Max Watt requirement for increasing Duty Cycle
            self.btn_up_hlt_dc.setPixmap(QPixmap(imagePath + "btn_up_dark.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
            HLT_DC += increment_amount
            hlt_dc_up_pressed = True
            if HLT_DC == 100:
                self.txt_HLT_DC.setText(str(HLT_DC) + "%")
                self.txt_HLT_DC.move(585, 295)
            else:
                self.txt_HLT_DC.setText(str(HLT_DC) + "%")
            
            
        elif hlt_dc_up_pressed == True:
            self.btn_up_hlt_dc.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
            hlt_dc_up_pressed = False
    
    def decrease_HLT_DC_Mashing(self, NaN):
        global hlt_dc_down_pressed
        global HLT_DC
        
        if hlt_dc_down_pressed == False and HLT_DC-1 >= 0:
            self.btn_down_hlt_dc.setPixmap(QPixmap(imagePath + "btn_down_dark.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
            hlt_dc_down_pressed = True
            HLT_DC -= increment_amount
            self.txt_HLT_DC.setText(str(HLT_DC) + "%")
            
        elif hlt_dc_down_pressed == True:
            self.btn_down_hlt_dc.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
            hlt_dc_down_pressed = False
    
    def showBoilingWindow(self, checked):
        self.boilingWindow.show()
        self.close()
            
    def showSettingsWindow(self, checked):
        if self.settingsWindow.isVisible():
            self.settingsWindow.hide()

        else:
            self.settingsWindow.show()
    
    def toggle_window1(self, NaN):
        self.close()

class BoilingWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Brew System")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(800,480)
        #self.setCursor(Qt.BlankCursor)
        self.settingsWindow = SettingsWindow()
        self.pumpsWindow = PumpsWindow()
        
        StaticGUI.initStaticGUI_Boiling(self)
        
        
        
        BoilingWindow.indicator_B = QLabel(self)
        BoilingWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.indicator_B.move(129,11)
        BoilingWindow.indicator_B.adjustSize()
        
        BoilingWindow.indicator_H = QLabel(self)
        BoilingWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.indicator_H.move(179,11)
        BoilingWindow.indicator_H.adjustSize()
        
        BoilingWindow.increment = QLabel(self)
        BoilingWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.increment.move(564,11)
        BoilingWindow.increment.adjustSize()
        BoilingWindow.increment.mousePressEvent = changeIncrementAmount
    
        
        
        
        BoilingWindow.txt_BK_PV_big = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        BoilingWindow.txt_BK_PV_big.setGraphicsEffect(colour_white)
        BoilingWindow.txt_BK_PV_big.setText(str(BK_PV) + degree_sign + "     " )
        BoilingWindow.txt_BK_PV_big.setFont(QFont("Bahnschrift", 80))
        BoilingWindow.txt_BK_PV_big.move(490, 150)
        BoilingWindow.txt_BK_PV_big.adjustSize()
        
        BoilingWindow.txt_BK_time = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        BoilingWindow.txt_BK_time.setGraphicsEffect(colour_white)
        BoilingWindow.txt_BK_time.setText(str(BK_Time_mins) + "  " )
        BoilingWindow.txt_BK_time.setFont(QFont("Bahnschrift", 80))
        BoilingWindow.txt_BK_time.move(490, 340)
        BoilingWindow.txt_BK_time.adjustSize()
        
        BoilingWindow.txt_min_label = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        BoilingWindow.txt_min_label.setGraphicsEffect(colour_white)
        BoilingWindow.txt_min_label.setText(str("min"))
        BoilingWindow.txt_min_label.setFont(QFont("Bahnschrift", 30))
        BoilingWindow.txt_min_label.move(630, 403)
        BoilingWindow.txt_min_label.adjustSize()
        
        
        
        BoilingWindow.txt_BK_SV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        BoilingWindow.txt_BK_SV.setGraphicsEffect(colour_white)
        BoilingWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
        BoilingWindow.txt_BK_SV.setFont(QFont("Bahnschrift", 32))
        BoilingWindow.txt_BK_SV.move(197, 195)
        BoilingWindow.txt_BK_SV.adjustSize()
        
        self.txt_BK_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        self.txt_BK_PV.setGraphicsEffect(colour_white)
        self.txt_BK_PV.setText(str(BK_PV) + degree_sign)
        self.txt_BK_PV.setFont(QFont("Bahnschrift", 32))
        self.txt_BK_PV.move(300, 195)
        self.txt_BK_PV.adjustSize()
        
        BoilingWindow.txt_BK_DC = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        BoilingWindow.txt_BK_DC.setGraphicsEffect(colour_white)
        BoilingWindow.txt_BK_DC.setText(str(BK_DC) + "%" + "  "  )
        BoilingWindow.txt_BK_DC.setFont(QFont("Bahnschrift", 45))
        BoilingWindow.txt_BK_DC.move(198, 295)
        BoilingWindow.txt_BK_DC.adjustSize()
        
        self.btn_title_boiling = QLabel(self)
        self.btn_title_boiling.setPixmap(QPixmap(imagePath + "title_boiling.png").scaled(318, 82, transformMode = Qt.SmoothTransformation))
        self.btn_title_boiling.move(235,11)
        self.btn_title_boiling.adjustSize()
        self.btn_title_boiling.mousePressEvent = self.toggle_window1
        
        self.btn_settings = QLabel(self)
        self.btn_settings.setPixmap(QPixmap(imagePath + "btn_settings.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        self.btn_settings.move(679,11)
        self.btn_settings.adjustSize()
        self.btn_settings.mousePressEvent = self.showSettingsWindow
        
        self.btn_pumps = QLabel(self)
        self.btn_pumps.setPixmap(QPixmap(imagePath + "btn_pump.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        self.btn_pumps.move(16,11)
        self.btn_pumps.adjustSize()
        self.btn_pumps.mousePressEvent = showPumpsWindow
        
        BoilingWindow.btn_up_bk_temp = QLabel(self)
        BoilingWindow.btn_up_bk_temp.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.btn_up_bk_temp.move(28,184)
        BoilingWindow.btn_up_bk_temp.adjustSize()
        BoilingWindow.btn_up_bk_temp.mousePressEvent = increase_BK_SV
        BoilingWindow.btn_up_bk_temp.mouseReleaseEvent = increase_BK_SV
        
        BoilingWindow.btn_down_bk_temp = QLabel(self)
        BoilingWindow.btn_down_bk_temp.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.btn_down_bk_temp.move(106,184)
        BoilingWindow.btn_down_bk_temp.adjustSize()
        BoilingWindow.btn_down_bk_temp.mousePressEvent = decrease_BK_SV
        BoilingWindow.btn_down_bk_temp.mouseReleaseEvent = decrease_BK_SV
        
        BoilingWindow.btn_up_bk_dc = QLabel(self)
        BoilingWindow.btn_up_bk_dc.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.btn_up_bk_dc.move(28,294)
        BoilingWindow.btn_up_bk_dc.adjustSize()
        BoilingWindow.btn_up_bk_dc.mousePressEvent = increase_BK_DC
        BoilingWindow.btn_up_bk_dc.mouseReleaseEvent = increase_BK_DC
        
        BoilingWindow.btn_down_bk_dc = QLabel(self)
        BoilingWindow.btn_down_bk_dc.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.btn_down_bk_dc.move(106,294)
        BoilingWindow.btn_down_bk_dc.adjustSize()
        BoilingWindow.btn_down_bk_dc.mousePressEvent = decrease_BK_DC
        BoilingWindow.btn_down_bk_dc.mouseReleaseEvent = decrease_BK_DC
        
        BoilingWindow.btn_power_bk = QLabel(self)
        BoilingWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
        BoilingWindow.btn_power_bk.move(28,380)
        BoilingWindow.btn_power_bk.adjustSize()
        BoilingWindow.btn_power_bk.mousePressEvent = update_btn_BKPower
        BoilingWindow.btn_power_bk.mouseReleaseEvent = update_btn_BKPower
         
        BoilingWindow.icon_lightning_bk = QLabel(self)
        BoilingWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.icon_lightning_bk.move(307,380)
        BoilingWindow.icon_lightning_bk.adjustSize()
        
        

    
    def toggle_window1(self, NaN):
        self.close()
        
    def showSettingsWindow(self, checked):
        if self.settingsWindow.isVisible():
            self.settingsWindow.hide()

        else:
            self.settingsWindow.show()
            
    def showPumpsWindow(self, checked):
        if self.pumpsWindow.isVisible():
            self.pumpsWindow.hide()

        else:
            self.pumpsWindow.show()
        
class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Brew System")
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        #self.setGeometry(65,55,670,370)
        #self.setCursor(Qt.BlankCursor)
        
        self.setGeometry(0,0,800,480)
        
        
        lbl_background = QLabel(self)
        lbl_background.setPixmap(QPixmap(imagePath + "background.png").scaled(800, 480, transformMode = Qt.SmoothTransformation))
        lbl_background.move(0,0)
        lbl_background.adjustSize()
        
        self.title = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        self.title.setGraphicsEffect(colour_white)
        self.title.setText("SETTINGS")
        self.title.setFont(QFont("Arial", 60, weight=QFont.Bold))
        self.title.move(210, 10)
        self.title.adjustSize()
        
        self.btn_shutdown = QLabel(self)
        self.btn_shutdown.setPixmap(QPixmap(imagePath + "btn_shutdown.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        self.btn_shutdown.move(714,15)
        self.btn_shutdown.adjustSize()
        self.btn_shutdown.mousePressEvent = self.quitApplication
        
        self.btn_back = QLabel(self)
        self.btn_back.setPixmap(QPixmap(imagePath + "btn_left.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        self.btn_back.move(15,15)
        self.btn_back.adjustSize()
        self.btn_back.mousePressEvent = self.closeSettingsWindow

    def closeSettingsWindow(self, NaN):
        self.close()
        
    def quitApplication():
        exit()

class PumpsWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("Brew System")
        self.setWindowFlag(Qt.FramelessWindowHint)
        #self.setGeometry(65,55,670,370)
        #self.setCursor(Qt.BlankCursor)
        
        self.setGeometry(0,0,800,480)
        self.settingsWindow = SettingsWindow()
        
        
        lbl_background = QLabel(self)
        lbl_background.setPixmap(QPixmap(imagePath + "background.png").scaled(800, 480, transformMode = Qt.SmoothTransformation))
        lbl_background.move(0,0)
        lbl_background.adjustSize()
        
        self.btn_title_pumps = QLabel(self)
        self.btn_title_pumps.setPixmap(QPixmap(imagePath + "title_pumps.png").scaled(318, 82, transformMode = Qt.SmoothTransformation))
        self.btn_title_pumps.move(235,11)
        self.btn_title_pumps.adjustSize()
        
        self.btn_settings = QLabel(self)
        self.btn_settings.setPixmap(QPixmap(imagePath + "btn_settings.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        self.btn_settings.move(679,11)
        self.btn_settings.adjustSize()
        self.btn_settings.mousePressEvent = self.showSettingsWindow
        
        PumpsWindow.indicator_B = QLabel(self)
        PumpsWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.indicator_B.move(129,11)
        PumpsWindow.indicator_B.adjustSize()
        
        PumpsWindow.indicator_H = QLabel(self)
        PumpsWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.indicator_H.move(179,11)
        PumpsWindow.indicator_H.adjustSize()
        
        PumpsWindow.increment = QLabel(self)
        PumpsWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.increment.move(564,11)
        PumpsWindow.increment.adjustSize()
        PumpsWindow.increment.mousePressEvent = changeIncrementAmount
        
        PumpsWindow.btn_pumps = QLabel(self)
        PumpsWindow.btn_pumps.setPixmap(QPixmap(imagePath + "btn_pump.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.btn_pumps.move(16,11)
        PumpsWindow.btn_pumps.adjustSize()
        PumpsWindow.btn_pumps.mousePressEvent = self.closePumpsWindow
        
        staticGUI = QLabel(self)
        staticGUI.setPixmap(QPixmap(imagePath + "pumpWindow_staticGUI.png").scaled(465, 248, transformMode = Qt.SmoothTransformation))
        staticGUI.move(115,102)
        staticGUI.adjustSize()
        
        PumpsWindow.BK_HeatCoil = QLabel(self)
        PumpsWindow.BK_HeatCoil.setPixmap(QPixmap(imagePath + "HeatCoil_off.png").scaled(92, 22, transformMode = Qt.SmoothTransformation))
        PumpsWindow.BK_HeatCoil.move(120,315)
        PumpsWindow.BK_HeatCoil.adjustSize()
        
        PumpsWindow.HLT_HeatCoil = QLabel(self)
        PumpsWindow.HLT_HeatCoil.setPixmap(QPixmap(imagePath + "HeatCoil_off.png").scaled(92, 22, transformMode = Qt.SmoothTransformation))
        PumpsWindow.HLT_HeatCoil.move(467,315)
        PumpsWindow.HLT_HeatCoil.adjustSize()
        
        ButtonsBackground = QLabel(self)
        ButtonsBackground.setPixmap(QPixmap(imagePath + "pumpButtonsBackground.png").scaled(104, 181, transformMode = Qt.SmoothTransformation))
        ButtonsBackground.move(696,150)
        ButtonsBackground.adjustSize()
        
        PumpsWindow.pumpIncrementButton = QLabel(self)
        PumpsWindow.pumpIncrementButton.setPixmap(QPixmap(imagePath + "pumpIncrement.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        PumpsWindow.pumpIncrementButton.move(713,166)
        PumpsWindow.pumpIncrementButton.adjustSize()
        PumpsWindow.pumpIncrementButton.mousePressEvent = self.increase_pump_DC
        PumpsWindow.pumpIncrementButton.mouseReleaseEvent = self.increase_pump_DC
        
        PumpsWindow.pumpDecrementButton = QLabel(self)
        PumpsWindow.pumpDecrementButton.setPixmap(QPixmap(imagePath + "pumpDecrement.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        PumpsWindow.pumpDecrementButton.move(713,244)
        PumpsWindow.pumpDecrementButton.adjustSize()
        PumpsWindow.pumpDecrementButton.mousePressEvent = self.decrease_pump_DC
        PumpsWindow.pumpDecrementButton.mouseReleaseEvent = self.decrease_pump_DC
        
        
        PumpsWindow.MLT_pumpSelectionButton = QLabel(self)
        PumpsWindow.MLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_off.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
        PumpsWindow.MLT_pumpSelectionButton.move(292,368)
        PumpsWindow.MLT_pumpSelectionButton.adjustSize()
        
        PumpsWindow.HLT_pumpSelectionButton = QLabel(self)
        PumpsWindow.HLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_off.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
        PumpsWindow.HLT_pumpSelectionButton.move(466,368)
        PumpsWindow.HLT_pumpSelectionButton.adjustSize()
        
        
        PumpsWindow.txt_pump1_MLT_DC = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        PumpsWindow.txt_pump1_MLT_DC.setGraphicsEffect(colour_white)
        PumpsWindow.txt_pump1_MLT_DC.setText(str(pump1_MLT_DC) + "%" + "  "  )
        PumpsWindow.txt_pump1_MLT_DC.setFont(QFont("Bahnschrift", 25))
        PumpsWindow.txt_pump1_MLT_DC.move(300, 380)
        PumpsWindow.txt_pump1_MLT_DC.adjustSize()
        
        PumpsWindow.txt_pump2_HLT_DC = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        PumpsWindow.txt_pump2_HLT_DC.setGraphicsEffect(colour_white)
        PumpsWindow.txt_pump2_HLT_DC.setText(str(pump2_HLT_DC) + "%" + "  "  )
        PumpsWindow.txt_pump2_HLT_DC.setFont(QFont("Bahnschrift", 25))
        PumpsWindow.txt_pump2_HLT_DC.move(474, 380)
        PumpsWindow.txt_pump2_HLT_DC.adjustSize()
        

        PumpsWindow.txt_MLT_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        PumpsWindow.txt_MLT_PV.setGraphicsEffect(colour_white)
        PumpsWindow.txt_MLT_PV.setText(str(MLT_PV) + degree_sign + "  ")
        PumpsWindow.txt_MLT_PV.setFont(QFont("Bahnschrift", 25))
        PumpsWindow.txt_MLT_PV.move(324, 148)
        PumpsWindow.txt_MLT_PV.adjustSize()
        
        PumpsWindow.txt_BK_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        PumpsWindow.txt_BK_PV.setGraphicsEffect(colour_white)
        PumpsWindow.txt_BK_PV.setText(str(BK_PV) + degree_sign + "  ")
        PumpsWindow.txt_BK_PV.setFont(QFont("Bahnschrift", 25))
        PumpsWindow.txt_BK_PV.move(150, 148)
        PumpsWindow.txt_BK_PV.adjustSize()
        
        PumpsWindow.txt_HLT_PV = QLabel(self)
        colour_white = QGraphicsColorizeEffect()
        colour_white.setColor(Qt.white)
        PumpsWindow.txt_HLT_PV.setGraphicsEffect(colour_white)
        PumpsWindow.txt_HLT_PV.setText(str(HLT_PV) + degree_sign + "  ")
        PumpsWindow.txt_HLT_PV.setFont(QFont("Bahnschrift", 25))
        PumpsWindow.txt_HLT_PV.move(500, 148)
        PumpsWindow.txt_HLT_PV.adjustSize()
        

        
        PumpsWindow.MLT_pumpSelectionButton_invisible = QLabel(self)
        PumpsWindow.MLT_pumpSelectionButton_invisible.setPixmap(QPixmap(imagePath + "pumpSelectionButton_invisible.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
        PumpsWindow.MLT_pumpSelectionButton_invisible.move(305,343)
        PumpsWindow.MLT_pumpSelectionButton_invisible.adjustSize()
        PumpsWindow.MLT_pumpSelectionButton_invisible.mousePressEvent = self.selectPump1
        
        PumpsWindow.HLT_pumpSelectionButton_invisible = QLabel(self)
        PumpsWindow.HLT_pumpSelectionButton_invisible.setPixmap(QPixmap(imagePath + "pumpSelectionButton_invisible.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
        PumpsWindow.HLT_pumpSelectionButton_invisible.move(466,368)
        PumpsWindow.HLT_pumpSelectionButton_invisible.adjustSize()
        PumpsWindow.HLT_pumpSelectionButton_invisible.mousePressEvent = self.selectPump2


    def showSettingsWindow(self, checked):
        if self.settingsWindow.isVisible():
            self.settingsWindow.hide()

        else:
            self.settingsWindow.show()
        
    def closePumpsWindow(self, NaN):
        self.close()
        
        
    def selectPump1(self, NaN):
        global pump1_selected
        global pump2_selected
        
        if pump1_selected == False:
            self.MLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_on.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
            pump1_selected = True
            
            self.HLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_off.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
            pump2_selected = False
            
        else:
            self.MLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_off.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
            pump1_selected = False
        

    def selectPump2(self, NaN):
        global pump2_selected
        global pump1_selected
        
        if pump2_selected == False:
            self.HLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_on.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
            pump2_selected = True
            self.MLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_off.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
            pump1_selected = False
        else:
            self.HLT_pumpSelectionButton.setPixmap(QPixmap(imagePath + "pumpSelectionButton_off.png").scaled(111, 60, transformMode = Qt.SmoothTransformation))
            pump2_selected = False
        
    def increase_pump_DC(self, NaN):
        global pump_dc_up_pressed
        global pump1_MLT_DC
        global pump2_HLT_DC
        global increment_amount
        global pump1_selected
        global pump2_selected
        
        if pump1_selected == True:
                if pump_dc_up_pressed == False:
                    if pump1_MLT_DC+increment_amount >= 100:
                            PumpsWindow.pumpIncrementButton.setPixmap(QPixmap(imagePath + "pumpIncrement.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                            pump_dc_up_pressed = True
                            pump1_MLT_DC = 100
                            
                            PumpsWindow.txt_pump1_MLT_DC.setText(str(pump1_MLT_DC) + "%" + "  ")
                            changeTextColour(PumpsWindow.txt_pump1_MLT_DC, "red")
                            

                    elif pump1_MLT_DC+increment_amount < 100:
                            pump1_MLT_DC += increment_amount
                            
                            pump_dc_up_pressed = True
                            PumpsWindow.txt_pump1_MLT_DC.setText(str(pump1_MLT_DC) + "%")
                    else:
                            changeTextColour(PumpsWindow.txt_pump1_MLT_DC, "red")
                            pump_dc_up_pressed = True
                            
                    soft_pwm_pump_1.ChangeDutyCycle(pump1_MLT_DC) #Updates to the set DC
                           
                else:
                    changeTextColour(PumpsWindow.txt_pump1_MLT_DC, "white")
                    pump_dc_up_pressed = False

        if pump2_selected == True:
                if pump_dc_up_pressed == False:
                    if pump2_HLT_DC+increment_amount >= 100:
                            PumpsWindow.pumpIncrementButton.setPixmap(QPixmap(imagePath + "pumpIncrement.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                            pump_dc_up_pressed = True
                            pump2_HLT_DC = 100
                            
                            PumpsWindow.txt_pump2_HLT_DC.setText(str(pump2_HLT_DC) + "%" + "  ")
                            changeTextColour(PumpsWindow.txt_pump2_HLT_DC, "red")
                            
                    elif pump2_HLT_DC+increment_amount < 100:
                            pump2_HLT_DC += increment_amount
                            
                            pump_dc_up_pressed = True
                            PumpsWindow.txt_pump2_HLT_DC.setText(str(pump2_HLT_DC) + "%")
                    else:
                            changeTextColour(PumpsWindow.txt_pump2_HLT_DC, "red")
                            pump_dc_up_pressed = True
                            
                    soft_pwm_pump_2.ChangeDutyCycle(pump2_HLT_DC) #Updates to the set DC
                           
                else:
                    changeTextColour(PumpsWindow.txt_pump2_HLT_DC, "white")
                    pump_dc_up_pressed = False
                

    def decrease_pump_DC(self, NaN):
        global pump_dc_up_pressed
        global pump1_MLT_DC
        global pump2_HLT_DC
        global increment_amount
        global pump1_selected
        global pump2_selected
        
        if pump1_selected == True:
                if pump_dc_up_pressed == False:
                    if pump1_MLT_DC-increment_amount <= 0:
                            PumpsWindow.pumpIncrementButton.setPixmap(QPixmap(imagePath + "pumpIncrement.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                            pump_dc_up_pressed = True
                            pump1_MLT_DC = 0
                            
                            PumpsWindow.txt_pump1_MLT_DC.setText(str(pump1_MLT_DC) + "%" + "  ")
                            changeTextColour(PumpsWindow.txt_pump1_MLT_DC, "red")
                            
                    elif pump1_MLT_DC+increment_amount > 0:
                            pump1_MLT_DC -= increment_amount
                            
                            pump_dc_up_pressed = True
                            PumpsWindow.txt_pump1_MLT_DC.setText(str(pump1_MLT_DC) + "%")
                    else:
                            changeTextColour(PumpsWindow.txt_pump1_MLT_DC, "red")
                            pump_dc_up_pressed = True
                            
                    soft_pwm_pump_1.ChangeDutyCycle(pump1_MLT_DC) #Updates to the set DC
                           
                else:
                    changeTextColour(PumpsWindow.txt_pump1_MLT_DC, "white")
                    pump_dc_up_pressed = False
        
        if pump2_selected == True:
                if pump_dc_up_pressed == False:
                    if pump2_HLT_DC-increment_amount <= 0:
                            PumpsWindow.pumpIncrementButton.setPixmap(QPixmap(imagePath + "pumpIncrement.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                            pump_dc_up_pressed = True
                            pump2_HLT_DC = 0
                            #PWM_HLT.ChangeDutyCycle(HLT_DC) #CHANGE THE DUTY CYCLE!
                            PumpsWindow.txt_pump2_HLT_DC.setText(str(pump2_HLT_DC) + "%" + "  ")
                            changeTextColour(PumpsWindow.txt_pump2_HLT_DC, "red")
                            
                    elif pump2_HLT_DC+increment_amount > 0:
                            pump2_HLT_DC -= increment_amount
                            #PWM_HLT.ChangeDutyCycle(HLT_DC) #CHANGE THE DUTY CYCLE!
                            pump_dc_up_pressed = True
                            PumpsWindow.txt_pump2_HLT_DC.setText(str(pump2_HLT_DC) + "%")
                    else:
                            changeTextColour(PumpsWindow.txt_pump2_HLT_DC, "red")
                            pump_dc_up_pressed = True
                    
                    soft_pwm_pump_2.ChangeDutyCycle(pump2_HLT_DC) #Updates to the set DC
                           
                else:
                    changeTextColour(PumpsWindow.txt_pump2_HLT_DC, "white")
                    pump_dc_up_pressed = False
            
        

def updateIndicators():
    if GPIO.input(GPIO_17_BK_POWER): #if GPIO 12 (BK Power) is high
        MainWindow.indicator_B.setPixmap(QPixmap(imagePath +    "indicator_B_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.BK_HeatCoil.setPixmap(QPixmap(imagePath + "HeatCoil_on.png").scaled(92, 22, transformMode = Qt.SmoothTransformation))
    else:
        MainWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.indicator_B.setPixmap(QPixmap(imagePath + "indicator_B_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.BK_HeatCoil.setPixmap(QPixmap(imagePath + "HeatCoil_off.png").scaled(92, 22, transformMode = Qt.SmoothTransformation))
        
    if GPIO.input(GPIO_27_HLT_POWER): #if GPIO 18 (HLT Power) is high
        MainWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_on.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.HLT_HeatCoil.setPixmap(QPixmap(imagePath + "HeatCoil_on.png").scaled(92, 22, transformMode = Qt.SmoothTransformation))
        
    else:
        MainWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        MashingWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        BoilingWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.indicator_H.setPixmap(QPixmap(imagePath + "indicator_H_off.png").scaled(47, 72, transformMode = Qt.SmoothTransformation))
        PumpsWindow.HLT_HeatCoil.setPixmap(QPixmap(imagePath + "HeatCoil_off.png").scaled(92, 22, transformMode = Qt.SmoothTransformation))
        
def updateIcons():
    global LOG

    if GPIO.input(GPIO_17_BK_POWER): #if GPIO 12 (BK Power) is high
        MainWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning_full.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning_full.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
    else:
        MainWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        BoilingWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
    
    if GPIO.input(GPIO_27_HLT_POWER): #if GPIO 18 (HLT Power) is high
        MainWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning_full.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning_full.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))  
    else:
        MainWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        MashingWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        
    if LOG == True:
        MashingWindow.icon_cloud_mlt.setPixmap(QPixmap(imagePath + "icon_cloud_full.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
    else:
        MashingWindow.icon_cloud_mlt.setPixmap(QPixmap(imagePath + "icon_cloud.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
        
def changeIncrementAmount(NaN):
        global increment_amount
        
        if increment_amount == 1:
            increment_amount = 5
            MainWindow.increment.setPixmap(QPixmap(imagePath + "increment_5.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            MashingWindow.increment.setPixmap(QPixmap(imagePath + "increment_5.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            BoilingWindow.increment.setPixmap(QPixmap(imagePath + "increment_5.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            PumpsWindow.increment.setPixmap(QPixmap(imagePath + "increment_5.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        elif increment_amount == 5:
            increment_amount = 10
            MainWindow.increment.setPixmap(QPixmap(imagePath + "increment_10.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            MashingWindow.increment.setPixmap(QPixmap(imagePath + "increment_10.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            BoilingWindow.increment.setPixmap(QPixmap(imagePath + "increment_10.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            PumpsWindow.increment.setPixmap(QPixmap(imagePath + "increment_10.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
        elif increment_amount == 10:
            increment_amount = 1
            MainWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            MashingWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            BoilingWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))
            PumpsWindow.increment.setPixmap(QPixmap(imagePath + "increment_1.png").scaled(104, 72, transformMode = Qt.SmoothTransformation))

def update_btn_LOG(NaN): #Updates HLT buttons status
        global LOG_buttonPressed
        global LOG_buttonToggle
        global LOG
        
        if LOG_buttonPressed == False: 
            if LOG_buttonToggle == False:
                MashingWindow.btn_logging_mlt.setPixmap(QPixmap(imagePath + "btn_logging_off_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MashingWindow.icon_cloud_mlt.setPixmap(QPixmap(imagePath + "icon_cloud_stroke.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                LOG_buttonToggle = True
                
                
            elif LOG_buttonToggle == True:
                MashingWindow.btn_logging_mlt.setPixmap(QPixmap(imagePath + "btn_logging_on_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MashingWindow.icon_cloud_mlt.setPixmap(QPixmap(imagePath + "icon_cloud_stroke.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                LOG_buttonToggle = False
                
            LOG_buttonPressed = True 
    
        elif LOG_buttonPressed == True:
            if LOG_buttonToggle == True:
                MashingWindow.btn_logging_mlt.setPixmap(QPixmap(imagePath + "btn_logging_on.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                LOG_buttonToggle = True
                LOG = True #Turn on logging
                MashingWindow.startThread2(MashingWindow)
                updateIcons()
                
                
            elif LOG_buttonToggle == False: 
                MashingWindow.btn_logging_mlt.setPixmap(QPixmap(imagePath + "btn_logging_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                LOG_buttonToggle = False
                LOG = False #Turn off logging
                updateIcons()

                
            LOG_buttonPressed = False

def update_btn_HLTPower(NaN): #Updates HLT buttons status
        global HLT_PowerToggle
        global HLT_PowerPressed
        
        if HLT_PowerPressed == True:
            if HLT_PowerToggle == False:
                HLT_PowerPressed = False
                MainWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MashingWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                
                MainWindow.turnOffHLTPower()

            elif HLT_PowerToggle == True:
                MainWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_on_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MainWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                MashingWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_on_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MashingWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                
                HLT_PowerToggle = False
                
        elif HLT_PowerPressed == False:
            if HLT_PowerToggle == True:
                HLT_PowerPressed = True
                MainWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_on.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MashingWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_on.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                
                MainWindow.turnOnHLTPower()
                
            elif HLT_PowerToggle == False: 
                MainWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_off_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MainWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                MashingWindow.btn_power_hlt.setPixmap(QPixmap(imagePath + "btn_power_off_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
                MashingWindow.icon_lightning_hlt.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                
                HLT_PowerToggle = True  



def update_btn_BKPower(NaN): #Updates HLT buttons status
    global BK_PowerToggle
    global BK_PowerPressed
        
    if BK_PowerPressed == True:
        if BK_PowerToggle == False:
            BK_PowerPressed = False
            MainWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            BoilingWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_off.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            
            MainWindow.turnOffBKPower()

        elif BK_PowerToggle == True:
            MainWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_on_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            MainWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
            BoilingWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_on_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            BoilingWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
                        
            BK_PowerToggle = False
                
    elif BK_PowerPressed == False:
        if BK_PowerToggle == True:
            BK_PowerPressed = True
            MainWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_on.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            BoilingWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_on.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            
            MainWindow.turnOnBKPower()
                
        elif BK_PowerToggle == False: 
            MainWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_off_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            MainWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))
            BoilingWindow.btn_power_bk.setPixmap(QPixmap(imagePath + "btn_power_off_dark.png").scaled(268, 71, transformMode = Qt.SmoothTransformation))
            BoilingWindow.icon_lightning_bk.setPixmap(QPixmap(imagePath + "icon_lightning_stroke").scaled(70, 70, transformMode = Qt.SmoothTransformation))

            BK_PowerToggle = True

def increase_HLT_SV(NaN):
        global hlt_sv_up_pressed
        global HLT_SV
        global increment_amount
        
        if hlt_sv_up_pressed == False and HLT_SV+increment_amount < 100:
            setButtonDark(MainWindow.btn_up_hlt_temp, "up")
            setButtonDark(MashingWindow.btn_up_hlt_temp, "up")
            hlt_sv_up_pressed = True
            HLT_SV += increment_amount
            MainWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
            MashingWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
            
        elif hlt_sv_up_pressed == False and HLT_SV+increment_amount >= 100:
            setButtonDark(MainWindow.btn_up_hlt_temp, "up")
            setButtonDark(MashingWindow.btn_up_hlt_temp, "up")
            hlt_sv_up_pressed = True
            HLT_SV = 100
            MainWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
            MainWindow.txt_HLT_SV.setFont(QFont("Bahnschrift", 25))
            MainWindow.txt_HLT_SV.move(585, 195)
            MashingWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
            MashingWindow.txt_HLT_SV.setFont(QFont("Bahnschrift", 25))
            MashingWindow.txt_HLT_SV.move(585, 195)

        elif hlt_sv_up_pressed == True:
            setButtonNormal(MainWindow.btn_up_hlt_temp, "up")
            setButtonNormal(MashingWindow.btn_up_hlt_temp, "up")
            hlt_sv_up_pressed = False
    
def decrease_HLT_SV(NaN):
    global hlt_sv_down_pressed
    global HLT_SV
    global increment_amount
        
    if hlt_sv_down_pressed == False and HLT_SV-increment_amount <= 0:
        setButtonDark(MainWindow.btn_down_hlt_temp, "down")
        setButtonDark(MashingWindow.btn_down_hlt_temp, "down")
        hlt_sv_down_pressed = True
        HLT_SV = 0
        MainWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
        MashingWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)    
    
    elif hlt_sv_down_pressed == False and HLT_SV-increment_amount < 100 and HLT_SV-increment_amount > 0:
        print("2")
        setButtonDark(MainWindow.btn_down_hlt_temp, "down")
        setButtonDark(MashingWindow.btn_down_hlt_temp, "down")
        hlt_sv_down_pressed = True
        HLT_SV = HLT_SV-increment_amount
        MainWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
        MainWindow.txt_HLT_SV.setFont(QFont("Bahnschrift", 32))
        MainWindow.txt_HLT_SV.move(585, 195)
        MashingWindow.txt_HLT_SV.setText(str(HLT_SV) + degree_sign)
        MashingWindow.txt_HLT_SV.setFont(QFont("Bahnschrift", 32))
        MashingWindow.txt_HLT_SV.move(585, 195)
        
    elif hlt_sv_down_pressed == True:
        setButtonNormal(MainWindow.btn_down_hlt_temp, "down")
        setButtonNormal(MashingWindow.btn_down_hlt_temp, "down")
        hlt_sv_down_pressed = False
        

def increase_HLT_DC(NaN):
        global hlt_dc_up_pressed
        global HLT_DC
        global BK_DC
        global increment_amount
        global GPIO_13_HLT_PWM, PWM_HLT
        
        if hlt_dc_up_pressed == False:
            if HLT_DC+increment_amount >= 100:
                if ((BK_DC/100)*8500)+((100/100)*5500) < 10560:
                    setButtonDark(MainWindow.btn_up_hlt_dc, "up")
                    setButtonDark(MashingWindow.btn_up_hlt_dc, "up")
                    hlt_dc_up_pressed = True
                    HLT_DC = 100
                    PWM_HLT.ChangeDutyCycle(HLT_DC)
                    MainWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
                    MainWindow.txt_HLT_DC.move(585, 295)
                    MashingWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
                    MashingWindow.txt_HLT_DC.move(585, 295)
                else:
                    setButtonDark(MainWindow.btn_up_hlt_dc, "up")
                    setButtonDark(MashingWindow.btn_up_hlt_dc, "up") 
                    changeTextColour(MainWindow.txt_HLT_DC, "red")
                    changeTextColour(MashingWindow.txt_HLT_DC, "red")
                    hlt_dc_up_pressed = True
                    
            elif HLT_DC+increment_amount < 100:
                if ((BK_DC/100)*8500)+(((HLT_DC+increment_amount)/100)*5500) < 10560:
                    setButtonDark(MainWindow.btn_up_hlt_dc, "up")
                    setButtonDark(MashingWindow.btn_up_hlt_dc, "up")
                    HLT_DC += increment_amount
                    PWM_HLT.ChangeDutyCycle(HLT_DC)
                    hlt_dc_up_pressed = True
                    MainWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
                    MashingWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
                else:
                    setButtonDark(MainWindow.btn_up_hlt_dc, "up")
                    setButtonDark(MashingWindow.btn_up_hlt_dc, "up")
                    changeTextColour(MainWindow.txt_HLT_DC, "red")
                    changeTextColour(MashingWindow.txt_HLT_DC, "red")
                    hlt_dc_up_pressed = True
                   
        else:
            setButtonNormal(MainWindow.btn_up_hlt_dc, "up")
            setButtonNormal(MashingWindow.btn_up_hlt_dc, "up")
            changeTextColour(MainWindow.txt_HLT_DC, "white")
            changeTextColour(MashingWindow.txt_HLT_DC, "white")
            hlt_dc_up_pressed = False

def decrease_HLT_DC(NaN):
    global hlt_dc_down_pressed
    global HLT_DC
    global increment_amount
    global GPIO_13_HLT_PWM, PWM_HLT
    
    if hlt_dc_down_pressed == False and HLT_DC-increment_amount >= 0:
        setButtonDark(MainWindow.btn_down_hlt_dc, "down")
        setButtonDark(MashingWindow.btn_down_hlt_dc, "down")
        hlt_dc_down_pressed = True
        HLT_DC -= increment_amount
        PWM_HLT.ChangeDutyCycle(HLT_DC)
        MainWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
        MashingWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
        
    elif hlt_dc_down_pressed == False and HLT_DC-increment_amount < 0:
        setButtonDark(MainWindow.btn_down_hlt_dc, "down")
        setButtonDark(MashingWindow.btn_down_hlt_dc, "down")
        hlt_dc_down_pressed = True
        HLT_DC = 0
        PWM_HLT.ChangeDutyCycle(HLT_DC)
        MainWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
        MashingWindow.txt_HLT_DC.setText(str(HLT_DC) + "%")
        
    elif hlt_dc_down_pressed == True:
        setButtonNormal(MainWindow.btn_down_hlt_dc, "down")
        setButtonNormal(MashingWindow.btn_down_hlt_dc, "down")
        hlt_dc_down_pressed = False
        
def increase_BK_SV(NaN):
        global bk_sv_up_pressed
        global BK_SV
        global increment_amount
        
        if bk_sv_up_pressed == False and BK_SV+increment_amount < 100:
            setButtonDark(MainWindow.btn_up_bk_temp, "up")
            setButtonDark(BoilingWindow.btn_up_bk_temp, "up")
            bk_sv_up_pressed = True
            BK_SV += increment_amount
            MainWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
            BoilingWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
            
        elif bk_sv_up_pressed == False and BK_SV+increment_amount >= 100:
            setButtonDark(MainWindow.btn_up_bk_temp, "up")
            setButtonDark(BoilingWindow.btn_up_bk_temp, "up")
            bk_sv_up_pressed = True
            BK_SV = 100
            MainWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
            MainWindow.txt_BK_SV.setFont(QFont("Bahnschrift", 25))
            MainWindow.txt_BK_SV.move(195, 195)
            BoilingWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
            BoilingWindow.txt_BK_SV.setFont(QFont("Bahnschrift", 25))
            BoilingWindow.txt_BK_SV.move(195, 195)
            
        elif bk_sv_up_pressed == True:
            setButtonNormal(MainWindow.btn_up_bk_temp, "up")
            setButtonNormal(BoilingWindow.btn_up_bk_temp, "up")
            bk_sv_up_pressed = False
    
def decrease_BK_SV(NaN):
    global bk_sv_down_pressed
    global BK_SV
    global increment_amount
        
    if bk_sv_down_pressed == False and BK_SV-increment_amount <= 0:
        setButtonDark(MainWindow.btn_down_bk_temp, "down")
        setButtonDark(BoilingWindow.btn_down_bk_temp, "down")
        bk_sv_down_pressed = True
        BK_SV = 0
        MainWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
        BoilingWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)    
    
    elif bk_sv_down_pressed == False and BK_SV-increment_amount < 100 and BK_SV-increment_amount > 0:
        setButtonDark(MainWindow.btn_down_bk_temp, "down")
        setButtonDark(BoilingWindow.btn_down_bk_temp, "down")
        bk_sv_down_pressed = True
        BK_SV = BK_SV-increment_amount
        MainWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
        MainWindow.txt_BK_SV.setFont(QFont("Bahnschrift", 32))
        MainWindow.txt_BK_SV.move(197, 195)
        BoilingWindow.txt_BK_SV.setText(str(BK_SV) + degree_sign)
        BoilingWindow.txt_BK_SV.setFont(QFont("Bahnschrift", 32))
        BoilingWindow.txt_BK_SV.move(197, 195)


    elif bk_sv_down_pressed == True:
        setButtonNormal(MainWindow.btn_down_bk_temp, "down")
        setButtonNormal(BoilingWindow.btn_down_bk_temp, "down")
        bk_sv_down_pressed = False
        
            
def increase_BK_DC(NaN):
        global bk_dc_up_pressed
        global BK_DC
        global HLT_DC
        global increment_amount
        global GPIO_12_BK_PWM, PWM_BK
        
        if bk_dc_up_pressed == False:
            if BK_DC+increment_amount >= 100:
                if (((100)/100)*8500)+((HLT_DC/100)*5500) < 10560:
                    setButtonDark(MainWindow.btn_up_bk_dc, "up")
                    setButtonDark(BoilingWindow.btn_up_bk_dc, "up")
                    bk_dc_up_pressed = True
                    BK_DC = 100
                    PWM_BK.ChangeDutyCycle(BK_DC)
                    MainWindow.txt_BK_DC.setText(str(BK_DC) + "%")
                    MainWindow.txt_BK_DC.move(198, 295)
                    BoilingWindow.txt_BK_DC.setText(str(BK_DC) + "%")
                    BoilingWindow.txt_BK_DC.move(198, 295)
                else:
                    setButtonDark(MainWindow.btn_up_bk_dc, "up")
                    setButtonDark(BoilingWindow.btn_up_bk_dc, "up")  
                    changeTextColour(MainWindow.txt_BK_DC, "red")
                    changeTextColour(BoilingWindow.txt_BK_DC, "red")
                    bk_dc_up_pressed = True
                
            elif BK_DC+increment_amount < 100:
                if (((BK_DC+increment_amount)/100)*8500)+((HLT_DC/100)*5500) < 10560:
                    setButtonDark(MainWindow.btn_up_bk_dc, "up")
                    setButtonDark(BoilingWindow.btn_up_bk_dc, "up")
                    bk_dc_up_pressed = True
                    BK_DC += increment_amount
                    PWM_BK.ChangeDutyCycle(BK_DC)
                    MainWindow.txt_BK_DC.setText(str(BK_DC) + "%")
                    BoilingWindow.txt_BK_DC.setText(str(BK_DC) + "%")  
                else:
                    setButtonDark(MainWindow.btn_up_bk_dc, "up")
                    setButtonDark(BoilingWindow.btn_up_bk_dc, "up")
                    changeTextColour(MainWindow.txt_BK_DC, "red")
                    changeTextColour(BoilingWindow.txt_BK_DC, "red")
                    bk_dc_up_pressed = True
                   
        else:
            setButtonNormal(MainWindow.btn_up_bk_dc, "up")
            setButtonNormal(BoilingWindow.btn_up_bk_dc, "up")
            changeTextColour(MainWindow.txt_BK_DC, "white")
            changeTextColour(BoilingWindow.txt_BK_DC, "white")
            bk_dc_up_pressed = False
        
def decrease_BK_DC(NaN):
    global bk_dc_down_pressed
    global BK_DC
    global increment_amount
        
    if bk_dc_down_pressed == False and BK_DC-increment_amount >= 0:
        setButtonDark(MainWindow.btn_down_bk_dc, "down")
        setButtonDark(BoilingWindow.btn_down_bk_dc, "down")
        bk_dc_down_pressed = True
        BK_DC -= increment_amount
        MainWindow.txt_BK_DC.setText(str(BK_DC) + "%")
        BoilingWindow.txt_BK_DC.setText(str(BK_DC) + "%")
    
    elif bk_dc_down_pressed == False and BK_DC-increment_amount < 0:
        setButtonDark(MainWindow.btn_down_bk_dc, "down")
        setButtonDark(BoilingWindow.btn_down_bk_dc, "down")
        bk_dc_down_pressed = True
        BK_DC = 0
        MainWindow.txt_BK_DC.setText(str(BK_DC) + "%")
        BoilingWindow.txt_BK_DC.setText(str(BK_DC) + "%")
            
    elif bk_dc_down_pressed == True:
        setButtonNormal(MainWindow.btn_down_bk_dc, "down")
        setButtonNormal(BoilingWindow.btn_down_bk_dc, "down")
        bk_dc_down_pressed = False
                
def log2sheets(data):
    global worksheet
    global temp_data_i
    global LOG
    
    if LOG == True:
        
        try:
            worksheet.append_table(data[temp_data_i], start='A3')
            temp_data_i += 1
            
            if temp_data_i == 5:
                worksheet.add_chart(('A3', 'A22'), [('B3', 'B22')], 'Mash Chart', anchor_cell='F3')
        except:
            print("Index out of bounds")
        
        MashingWindow.startThread2(MashingWindow) #Start thread responsible for calling log2sheets function
            
def changeTextColour(text, colour):
    if colour == "red":
        colour = QGraphicsColorizeEffect()
        colour.setColor(QColor(245, 75, 100, 255))
    if colour == "white":
        colour = QGraphicsColorizeEffect()
        colour.setColor(Qt.white)
    text.setGraphicsEffect(colour)

def setButtonDark(button, direction):
    if direction == "up":
        button.setPixmap(QPixmap(imagePath + "btn_up_dark.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
    if direction == "down":
       button.setPixmap(QPixmap(imagePath + "btn_down_dark.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))

def setButtonNormal(button, direction):
    if direction == "up":
        button.setPixmap(QPixmap(imagePath + "btn_up.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
    if direction == "down":
       button.setPixmap(QPixmap(imagePath + "btn_down.png").scaled(70, 70, transformMode = Qt.SmoothTransformation))
    
def showPumpsWindow(window):
        
        
        
        if MainWindow.pumpsWindow.isVisible():
            window.pumpsWindow.hide()

        else:
            MainWindow.pumpsWindow.show()


        

def resetOutputs():
    global GPIO_17_BK_POWER
    global GPIO_27_HLT_POWER
    
    GPIO.output(GPIO_17_BK_POWER, GPIO.LOW)
    GPIO.output(GPIO_27_HLT_POWER, GPIO.LOW)
            

            
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

