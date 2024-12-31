from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.uic import loadUi
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import QIODevice, QPoint, QIODeviceBase
from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
import numpy as np
import sys
import time
import pandas as pd

class MyApp(QMainWindow): #define la clase de MYApp 
    def __init__(self):
        super(MyApp,self).__init__()
        loadUi("TU_GAF_23.ui",self)
        self.bt_normal.hide()
        self.click_posicion = QPoint()
        self.bt_minimize.clicked.connect(lambda :self.showMinimized())
        self.bt_normal.clicked.connect(self.control_bt_normal)
        self.bt_maximize.clicked.connect(self.control_bt_maximize)
        self.bt_close.clicked.connect(lambda: self.close())
        self.datos = []
        self.tiempo = []
        self.setpoint = []
        self.cnt = 0
        self.slider1 = '0'        #eliminar barra de titulo y opacidad
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        #timer 100ms
        '''self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)'''
        

        #SizeGrip
        self.gripSize = 10
        self.grip =QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)
        #mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        ## control connect
        self.serial = QSerialPort()
        self.bt_update.clicked.connect(self.read_ports)
        self.bt_connect.clicked.connect(self.serial_connect)
        self.bt_disconnect.clicked.connect(lambda:self.serial.close())
        #self.serial.event
        self.serial.readyRead.connect(self.read_data)
        self.slider_one.valueChanged.connect(self.slider_one_pwm)
        
        #self.slider_two.valueChanged.connect(self.slider_two_pwm)
        self.led_one.toggled.connect(self.control_led_one)      #cuando cambie de estado el objeto active la funcion control_led_one
        self.led_two.toggled.connect(self.control_led_two)
        self.x = list(np.linspace(0, 100, 100))
        self.y = list(np.linspace(0, 0, 100))

        #GRAFICA
        pg.setConfigOption('background', '#808080')
        pg.setConfigOption('foreground', '#FFFFFF')
        self.plt = pg.PlotWidget(title='Velocidad Motor DC')
        #self.plt.setYRange(-20, 3500)
        self.plt.enableAutoRange(axis='y', enable=True)
        self.graph_layout.addWidget(self.plt)

        #self.read_ports()

    def read_ports(self):
        self.baudrates = ['1200', '2400', '4800', '9600', 
                          '19200', '38400', '115200']

        portList = []
        ports = QSerialPortInfo().availablePorts()
        for i in ports:
            portList.append(i.portName())

        self.cb_list_ports.clear()
        self.cb_list_baudrates.clear()
        self.cb_list_ports.addItems(portList)
        self.cb_list_baudrates.addItems(self.baudrates)
        self.cb_list_baudrates.setCurrentText("115200")

    def serial_connect(self):
        #self.serial.waitForReadyRead(100)              #no se pone pyqt6
        self.port = self.cb_list_ports.currentText()
        self.baud = self.cb_list_baudrates.currentText()
        self.serial.setBaudRate(int(self.baud))
        self.serial.setPortName(self.port)
        self.serial.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        #self.serial.readAll()        
        #self.serial.clear()
        
        #self.timer.start()

    def read_data(self):
        if not self.serial.canReadLine(): return
        rx = ['0.0','0.0','0.0']
        rx = self.serial.readLine()
        x =str(rx, 'utf-8').strip()
        xy = x.split(',')
        #print(xy)
        x = float(xy[0])
        y = float(xy[1])
        sp = float(xy[2])
        self.cnt = self.cnt + 1
        if self.cnt < 100:
            if y > 1000.0:
                y = 0.0
        print(x)
        #self.datos.append(x)
        #self.tiempo.append(y)    #lectura del tiempo de muestreo
        #self.setpoint.append(sp)
        self.velocidad.display(x)
        self.x.append(y)
        self.y.append(x)
        self.plt.clear()
        self.plt.plot(self.x,self.y, pen=pg.mkPen('#007832', width=2))
        #self.serial.flush()

    '''def update(self):
        print(self.y)
        self.y = self.y[1:]
        self.x = self.x[1:]
        self.plt.clear()
        self.plt.plot(self.x,self.y, pen=pg.mkPen('#007832', width=2))
        self.velocidad.display(self.x[-1])'''


    def send_data(self, data):
        data = data #+ "\n"
        #print(data)
        #if self.serial.isOpen():
        self.serial.write(data.encode())

    def slider_one_pwm(self, event):
        self.slider_one.setValue(event)
        self.value_one.setText(str(event))
        self.slider1 = str(event)
        #print(self.slider1)
        #self.send_data(slider1)

    '''def slider_two_pwm(self, event):
        self.slider_two.setValue(event)
        self.value_two.setText(str(event))
        slider2 = '2,'+ str(event)
        self.send_data(slider2)'''

    def control_led_one(self):                          #esta funcion se activa cuando presiono el boton len one
        self.send_data(self.slider1)
        #self.send_data('50')
        #if self.led_one.isChecked()==True:
        #    led1 = '40'
        #else:
        #    led1 = '80'
        #self.send_data(led1)
        #print(self.datos)
        #print(self.tiempo)
        #df = pd.DataFrame(self.datos,self.tiempo)       #se crea el cuadro de datos 
        #print(df)                                       #imprimo en l salida el dataframe
        #df.to_excel("Identificacion.xlsx", sheet_name="Datos")#creo el archivo de excel y guardo el dataframe.'''

        
    def control_led_two(self):       
        #self.led_two.toogle = True

        #self.send_data(led2)
        '''print(len(self.datos))
        print(len(self.tiempo))
        print(len(self.setpoint))
        #todos = self.datos,self.tiempo,self.setpoint
        df = pd.DataFrame()       #se crea el cuadro de datos    ,self.setpoint,columns=['a','b','c']
        df['Tiempo'] = self.tiempo
        df['Datos'] = self.datos
        df['SetPoint'] = self.setpoint''
        #df = pd.DataFrame(todos).transpose()
        #print(df)                                       #imprimo en l salida el dataframe
        df.to_excel("Identificacion_12_ConCorreaAjustada.xlsx", sheet_name="Datos") #creo el archivo de excel y guardo el dataframe.'''
        #self.send_data('70')
        '''if self.led_two.isChecked()==True:
            led2 = '5'
        else:
            led2 = '6'
        self.send_data(led2)'''

    ##########################################
    def control_bt_normal(self):
        self.showNormal()
        self.bt_normal.hide()
        self.bt_maximize.show()

    def control_bt_maximize(self):
        self.showMaximized()
        self.bt_maximize.hide()
        self.bt_normal.show()

    ##SizeGrip
    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    ## mover ventana
    def mousePressEvent(self, event):
        self.click_posicion = event.pos()

    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.pos() - self.click_posicion)
                self.click_posicion = event.pos()
                event.accept()
        if event.pos().y() <=10 or event.pos().x() <=10 :
            self.showMaximized()
            self.bt_maximize.hide()
            self.bt_normal.show()
        else:
            self.showNormal()
            self.bt_normal.hide()
            self.bt_maximize.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec())