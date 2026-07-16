import paho.mqtt.client as mqtt
from pymavlink import mavutil
import time


YESIL = '\033[92m'
CYAN = '\033[96m'
SARI = '\033[93m'
KIRMIZI = '\033[91m'
SIFIRLA = '\033[0m'


class RaspberryPiSubscriber:
    def __init__(self, broker_ip, port=1883):
        self.broker_ip = broker_ip
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        print(f"{CYAN}Connecting to the drone simulation...{SIFIRLA}")
        self.master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
        self.master.wait_heartbeat()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"{YESIL}Raspberry Pİ connected to the channel succesfully.{SIFIRLA}\n")
            # Bağlanır bağlanmaz kanala abone oluyoruz
            client.subscribe("simulation/control/command")
            print(f"{CYAN}channel is being listened..\ncommand is being waited...{SIFIRLA}\n")
        else:
            print(f"{KIRMIZI}ERROR! something went wrong{SIFIRLA}\n")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        recv_commnd = msg.payload.decode('utf-8')
        print(f"message from {topic}: {recv_commnd}\n")

        # Gelen komutları ayrıştır
        if recv_commnd == "ARM":
            print(f"{CYAN} Motors are being started...{SIFIRLA}\n")
            self.arm_drone()

        elif recv_commnd == "TAKEOFF":
            print(f"{CYAN}Otomatik kalkış sekansı başlatılıyor...{SIFIRLA}\n")
            self.otomatik_kalkis_testi()
            # print(f"{CYAN}Initiating takeoff sequence...{SIFIRLA}\n")
            # self.takeoff_drone()

        elif recv_commnd == "MOVE":
            print(f"{CYAN}Moving to target...{SIFIRLA}\n")
            self.move_drone()

        elif recv_commnd == "LAND":
            print(f"{CYAN}Initiating landing sequence...{SIFIRLA}\n")
            self.land_drone()

        elif recv_commnd == "DISARM":
            print(f"{CYAN}Disarming motors...{SIFIRLA}\n")
            self.disarm_drone()

        elif recv_commnd == "GUIDED":
            print(f"{CYAN}Guided mode is on.{SIFIRLA}\n")
            self.guided_mode_drone()

        else:
            print(f"{KIRMIZI}Unknown command!{SIFIRLA}\n")

    def arm_drone(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0
        )
        self.confirm_command("ARM")
        print(""f"{YESIL}-> ARM command is sent to the drone!{SIFIRLA}\n")

    def disarm_drone(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        self.confirm_command("DISARM")
        print(f"{YESIL}-> DISARM command sent to the drone!{SIFIRLA}\n")

    def takeoff_drone(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 20.0
        )
        self.confirm_command("TAKEOFF")
        print(f"{YESIL}-> TAKEOFF command sent to the drone! (Ascending to 20m){SIFIRLA}\n")

    def move_drone(self):
        self.master.mav.set_position_target_local_ned_send(
            0,
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
            0b0000111111111000,
            60, 80, 1,
            0, 0, 0,
            0, 0, 0,
            0, 0
        )
        self.confirm_command("MOVE")
        print(f"{YESIL}-> MOVE command sent to the drone! (Moving forward 100m){SIFIRLA}\n")

    def land_drone(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0,
            0, 0, 0, 0,
            0, 0, 0
        )
        self.confirm_command("LAND")
        print(f"{YESIL}-> LAND command sent to the drone! (Descending vertically){SIFIRLA}\n")

    def guided_mode_drone(self):
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4,  # ArduCopter GUIDED mod numarası
            0, 0, 0, 0, 0
        )
        self.confirm_command("GUIDED MODE")

    def confirm_command(self, command_name=""):
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        if ack:
            print(f"{CYAN}{command_name} ACK alındı -> result: {ack.result}{SIFIRLA}")
        else:
            print(f"{KIRMIZI}{command_name}: ACK alınamadı (timeout){SIFIRLA}")

    def otomatik_kalkis_testi(self):
        print("1. GUIDED moda geçiliyor...")
        self.guided_mode_drone()
        time.sleep(1)

        print("2. ARM ediliyor...")
        self.arm_drone()
        time.sleep(2)

        print("3. TAKEOFF komutu gönderiliyor...")
        self.takeoff_drone()

    def sistemi_baslat(self):
        print(f"{CYAN}Connecting to the Broker ({self.broker_ip})...{SIFIRLA}\n")
        self.client.connect(self.broker_ip, self.port)
        self.client.loop_forever()


if __name__ == "__main__":
    BROKER_ADRESI = "test.mosquitto.org"
    drone_dinleyici = RaspberryPiSubscriber(broker_ip=BROKER_ADRESI)

    drone_dinleyici.sistemi_baslat()
