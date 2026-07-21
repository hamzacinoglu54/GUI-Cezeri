import sys
import paho.mqtt.client as mqtt
from PyQt6 import QtWidgets, uic


class MainApp(QtWidgets.QMainWindow):  # pyqt6'ten hazır class yapısı
    def __init__(self):
        super().__init__()  # miras aldık

        uic.loadUi('ui_son.ui', self)  # qt design dosyası

        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.mqtt_client.on_connect = self.on_connect

        self.mqtt_client.connect("test.mosquitto.org", 1883)

        self.mqtt_client.loop_start()  # arayüzün donmasını engelleyen satır döngü için yeni
        # bir sekme açar kod okunmaya devam eder
        self.ARM.clicked.connect(self.ArmCommand)
        self.TAKEOFF.clicked.connect(self.TakeOffCommand)
        self.LAND.clicked.connect(self.LandCommand)
        self.MOVE.clicked.connect(self.MoveCommand)
        self.DISARM.clicked.connect(self.DisArmCommand)
        self.GUIDED.clicked.connect(self.GuidedCommand)

    def on_connect(self, client, userdata, flags, rc):  # bağlantı başarılı mı kontrol eden metot
        if rc == 0:
            print("It is connected to MQTT Broker succesfully.")
        else:
            print("Connection failed.")

    def ArmCommand(self):  # arm komutu metodu
        topic = "simulation/control/command"
        message = "ARM"
        self.mqtt_client.publish(topic, message)
        print(f"\033[94m{message}\033[0m is sent to the channel \033[96m{topic}\033[0m ")

    def TakeOffCommand(self):  # takeoff komutu metodu
        topic = "simulation/control/command"
        message = "TAKEOFF"
        self.mqtt_client.publish(topic, message)
        print(f"\033[94m{message}\033[0m is sent to the channel \033[96m{topic}\033[0m ")

    def LandCommand(self):  # land komutu metodu
        topic = "simulation/control/command"
        message = "LAND"
        self.mqtt_client.publish(topic, message)
        print(f"\033[94m{message}\033[0m is sent to the channel \033[96m{topic}\033[0m ")

    def MoveCommand(self):  # move komutu metodu
        # Arayüzdeki x, y ve z isimli QSpinBox kutucuklarından güncel değerleri çekiyoruz
        x_val = self.x.value()
        y_val = self.y.value()
        z_val = self.z.value()

        topic = "simulation/control/command"

        # Çektiğimiz x, y ve z koordinat değerlerini boşluk bırakarak tek bir MOVE mesajı haline getiriyoruz
        message = f"MOVE {x_val} {y_val} {z_val}"

        self.mqtt_client.publish(topic, message)
        print(f"\033[94m{message}\033[0m is sent to the channel \033[96m{topic}\033[0m ")

    def DisArmCommand(self):  # disarm komutu metodu
        topic = "simulation/control/command"
        message = "DISARM"
        self.mqtt_client.publish(topic, message)
        print(f"\033[94m{message}\033[0m is sent to the channel \033[96m{topic}\033[0m ")

    def GuidedCommand(self):  # disarm komutu metodu
        topic = "simulation/control/command"
        message = "GUIDED"
        self.mqtt_client.publish(topic, message)
        print(f"\033[94m{message}\033[0m is sent to the channel \033[96m{topic}\033[0m ")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    pencere = MainApp()
    pencere.show()
    sys.exit(app.exec())