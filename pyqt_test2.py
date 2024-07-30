from http_test import *
import time

import io
import os

# import os
import sys
import folium
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import *


ds18b20 = 0
dht11 = 0
air = 0
humi = 0


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setMinimumSize(800,600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"#centralwidget{background-color: #465461;}")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")


        self.webEngineView = QWebEngineView(self.centralwidget)
        self.webEngineView.setObjectName(u"webEngineView")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webEngineView.sizePolicy().hasHeightForWidth())
        self.webEngineView.setSizePolicy(sizePolicy)
        self.webEngineView.setUrl(QUrl(u"about:blank"))

        self.horizontalLayout.addWidget(self.webEngineView)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"#frame{background-color: #C4DCDF;}")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.Temperatureds18 = QLabel(self.frame)
        self.Temperatureds18.setObjectName(u"Temperatureds18")
        sizePolicy.setHeightForWidth(self.Temperatureds18.sizePolicy().hasHeightForWidth())
        self.Temperatureds18.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"Comic Sans MS"])
        font.setPointSize(24)
        self.Temperatureds18.setFont(font)

        self.verticalLayout.addWidget(self.Temperatureds18)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.TemperatureDHT11 = QLabel(self.frame)
        self.TemperatureDHT11.setObjectName(u"TemperatureDHT11")
        sizePolicy.setHeightForWidth(self.TemperatureDHT11.sizePolicy().hasHeightForWidth())
        self.TemperatureDHT11.setSizePolicy(sizePolicy)
        self.TemperatureDHT11.setFont(font)

        self.verticalLayout.addWidget(self.TemperatureDHT11)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.Humidity = QLabel(self.frame)
        self.Humidity.setObjectName(u"Humidity")
        sizePolicy.setHeightForWidth(self.Humidity.sizePolicy().hasHeightForWidth())
        self.Humidity.setSizePolicy(sizePolicy)
        self.Humidity.setFont(font)

        self.verticalLayout.addWidget(self.Humidity)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.AirQuality = QLabel(self.frame)
        self.AirQuality.setObjectName(u"AirQuality")
        sizePolicy.setHeightForWidth(self.AirQuality.sizePolicy().hasHeightForWidth())
        self.AirQuality.setSizePolicy(sizePolicy)
        self.AirQuality.setFont(font)
        self.AirQuality.setCursor(QCursor(Qt.ArrowCursor))
        self.AirQuality.setScaledContents(False)

        self.verticalLayout.addWidget(self.AirQuality)


        self.horizontalLayout.addWidget(self.frame)

        MainWindow.setCentralWidget(self.centralwidget)


        self.retranslateUi(MainWindow)


        self.coordinate = (0 ,0)
        self.maps = folium.Map(zoom_start= 16, location=self.coordinate, popup="<strong>Current\nLocation</strong>")
        self.data = io.BytesIO()
        folium.Marker(location=self.coordinate).add_to(self.maps)
        self.maps.save(self.data, close_file=False)
        self.webEngineView.setHtml(self.data.getvalue().decode())

        # map_file = "map.html"
        # self.maps.save(map_file)
        # self.webEngineView.load(QUrl.fromLocalFile(os.path.abspath(map_file)))


        ##########################################################################
        #THREADS
        ##########################################################################

        runserverforever.start()
        qtthread = threading.Thread(target=self.update_values)
        qtthread.start()

        self.maptimer = QTimer()
        self.maptimer.timeout.connect(self.update_map)
        self.maptimer.start(10000)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Temperatureds18.setText(QCoreApplication.translate("MainWindow", u"  Temp DS18B20 : -127 °C", None))
        self.Temperatureds18.setStyleSheet(r"#Temperatureds18{ background-color: #729CA2;"
                                           r"border-radius: 30px;}")
        self.TemperatureDHT11.setText(QCoreApplication.translate("MainWindow", u"  Temp DHT11 : -127 °C", None))
        self.TemperatureDHT11.setStyleSheet(r"#TemperatureDHT11{ background-color: #729CA2;"
                                            r"border-radius: 30px;}")
        self.Humidity.setText(QCoreApplication.translate("MainWindow", "  Humidity : 0%", None))
        self.Humidity.setStyleSheet(r"#Humidity{ background-color: #729CA2;"
                                    r"border-radius: 30px;}")
        self.AirQuality.setText(QCoreApplication.translate("MainWindow", u"  Air Quality : 0 ppm", None))
        self.AirQuality.setStyleSheet(r"#AirQuality{ background-color: #729CA2;"
                                      r"border-radius: 30px;}")

        # retranslateUi


    def update_values(self):
        while(True):
            # try:
            global ds18b20
            global dht11
            global humi
            global air

            global text
            self.k = return_text().split()

            ds18b20 = self.k[0]
            dht11 = self.k[1]
            humi = self.k[2]
            air = self.k[3]



            self.Temperatureds18.setText(QCoreApplication.translate("MainWindow", f"  Temp DS18B20 : {str(ds18b20)} °C", None))
            self.TemperatureDHT11.setText(QCoreApplication.translate("MainWindow", f"  Temp DHT11 : {str(dht11)} °C", None))
            self.Humidity.setText(QCoreApplication.translate("MainWindow", f"  Humidity : {humi} %", None))
            self.AirQuality.setText(QCoreApplication.translate("MainWindow", f"  Air Quality : {air} ppm", None))

    def update_map(self):

        coordinates = self.k[4]
        coordinates = coordinates.split(',')
        coordinates = (float(coordinates[0][1:]), float(coordinates[1][:-2]))

        if(coordinates[0] != self.coordinate[0] or coordinates[1] != self.coordinate[1]):
            self.coordinate = coordinates

            self.maps = folium.Map(location=self.coordinate, popup="<strong>Current\nLocation</strong>",zoom_start=16)
            folium.Marker(location=self.coordinate).add_to(self.maps)
            self.data = io.BytesIO()
            self.maps.save(self.data, close_file=False)
            self.webEngineView.setHtml(self.data.getvalue().decode())
        print(self.k)

            # print(coordinates, self.coordinate)
        # map_file = "map.html"
        # self.maps.save(map_file)
        # self.webEngineView.load(QUrl.fromLocalFile(os.path.abspath(map_file)))

        # time.sleep(10)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    widget = Ui_MainWindow()
    widget.setupUi(window)
    window.show()
    try:
        sys.exit(app.exec())
        print("Exception occurred")
    except SystemExit:
        print('Closing Window...')


        os._exit(os.EX_OK)

