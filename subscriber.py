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

        # Gelen mesajı boşluklara göre bölerek ana komutu ve (varsa) koordinat verilerini ayırıyoruz
        cmd_parts = recv_commnd.split()
        main_cmd = cmd_parts[0] if cmd_parts else ""

        # Gelen komutları ayrıştır
        if main_cmd == "ARM":
            print(f"{CYAN} Motors are being started...{SIFIRLA}\n")
            self.arm_drone()

        elif main_cmd  == "TAKEOFF":
            print(f"{CYAN}drone is taking off...{SIFIRLA}\n")
            self.takeoff_drone()
            # print(f"{CYAN}Initiating takeoff sequence...{SIFIRLA}\n")
            # self.takeoff_drone()

        elif main_cmd  == "MOVE":
            # "MOVE x y z" formatındaki mesajdan sayısal verileri çekip float tipine dönüştürüyoruz
            hedef_x = float(cmd_parts[1])
            hedef_y = float(cmd_parts[2])
            hedef_z = float(cmd_parts[3])

            print(f"{CYAN}Moving to target...{SIFIRLA}\n")
            # Çektiğimiz değerleri move_drone fonksiyonuna  gönderiyoruz
            self.move_drone(hedef_x, hedef_y, hedef_z)

        elif main_cmd  == "LAND":  # recv_commnd yerine ana_komut kullanıldı
            print(f"{CYAN}Initiating landing sequence...{SIFIRLA}\n")
            self.land_drone()

        elif main_cmd  == "DISARM":  # recv_commnd yerine ana_komut kullanıldı
            print(f"{CYAN}Disarming motors...{SIFIRLA}\n")
            self.disarm_drone()

        elif main_cmd  == "GUIDED":  # recv_commnd yerine ana_komut kullanıldı
            print(f"{CYAN}Guided mode is on.{SIFIRLA}\n")
            self.guided_mode_drone()

        else:
            print(f"{KIRMIZI}Unknown command!{SIFIRLA}\n")

    def arm_drone(self):
        self.master.arducopter_arm()
        self.master.motors_armed_wait()  # Drone arm olana kadar bekle
        print(f"{YESIL}-> ARM command is sent and verified!{SIFIRLA}\n")

    # def arm_drone(self):
    #     self.master.mav.command_long_send(
    #         self.master.target_system,
    #         self.master.target_component,
    #         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    #         0,
    #         1, 0, 0, 0, 0, 0, 0
    #     )
    #     self.confirm_command("ARM")
    #     print(""f"{YESIL}-> ARM command is sent to the drone!{SIFIRLA}\n")

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

    def move(self, x, y, z):

        self.master.mav.set_position_target_local_ned_send(
            0,  # time_boot_ms
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED,
            0b011111111000,
            x, y, -z,
            0, 0, 0,
            0, 0, 0,
            0, 0
        )
        print(f"{YESIL}-> MOVE command sent!{SIFIRLA}\n")

    # def move_drone(self):
    #     # Fonksiyonun ihtiyaç duyduğu tam 16 parametreyi sırasıyla gönderiyoruz
    #     self.master.mav.send(
    #         mavutil.mavlink.MAVLink_set_position_target_local_ned_message(
    #             0,  # time_boot_ms (0: önemsiz)
    #             self.master.target_system,  # target_system
    #             self.master.target_component,  # target_component
    #             mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,  # Referans: Gövde
    #             int(0b0000111111111000),  # Maske: Sadece konumu (x,y,z) dinle
    #             5,  # X (m)
    #             5,  # Y (m)
    #             0,  # Z (m) (Yukarı doğru hareket için eksi)
    #             0, 0, 0,  # VX, VY, VZ (Hızlar - Maskeli)
    #             0, 0, 0,  # AFX, AFY, AFZ (İvmeler - Maskeli)
    #             0, 0  # YAW, YAW_RATE (Dönüşler - Maskeli)
    #         )
    #     )

    # def move_drone(self):
    #     self.master.mav.set_position_target_local_ned_send(
    #         0,
    #         self.master.target_system,
    #         self.master.target_component,
    #         mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,  # Drone'un baktığı yönü referans alır
    #         0b0000111111111000,
    #         60,  # X: Baktığı yöne doğru 60 metre ileri
    #         80,  # Y: Kendi sağına doğru 80 metre
    #         0,  # Z: 0 offset (Mevcut irtifasını kesinlikle korur)
    #         0, 0, 0,
    #         0, 0, 0,
    #         0, 0
    #     )
    #     self.confirm_command()
    #     print(f"{YESIL}-> MOVE command sent! (Baktığı yöne 60m ileri, 80m sağa){SIFIRLA}\n")

    # def move_drone(self):
    #     self.master.mav.set_position_target_local_ned_send(
    #         0,
    #         self.master.target_system,
    #         self.master.target_component,
    #         mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
    #         0b0000111111111000,
    #         60, 80, 1,
    #         0, 0, 0,
    #         0, 0, 0,
    #         0, 0
    #     )
    #     print(f"{YESIL}-> MOVE command sent to the drone! (Moving forward 100m){SIFIRLA}\n")

    def land(self):
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0
        )
        self.confirm_command("LAND")
        print("drone is landing...")

    def guided_mode_drone(self):
        self.master.set_mode('GUIDED')
        print(f"{YESIL}-> GUIDED mode command sent.{SIFIRLA}\n")
        self.confirm_command("GUIDED MODE")

    def confirm_command(self, command_name=""):
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
        if ack:
            print(f"{CYAN}{command_name} ACK alındı -> result: {ack.result}{SIFIRLA}")
            # Eğer komut reddedildiyse (Result 4), nedenini yakala:
            if ack.result == 4:
                status_msg = self.master.recv_match(type='STATUSTEXT', blocking=True, timeout=2)
                if status_msg:
                    print(f"{KIRMIZI}HATA SEBEBİ: {status_msg.text}{SIFIRLA}")
        else:
            print(f"{KIRMIZI}{command_name}: ACK alınamadı (timeout){SIFIRLA}")

    def sistemi_baslat(self):
        print(f"{CYAN}Connecting to the Broker ({self.broker_ip})...{SIFIRLA}\n")
        self.client.connect(self.broker_ip, self.port)
        self.client.loop_forever()


if __name__ == "__main__":
    BROKER_ADRESI = "test.mosquitto.org"
    drone_dinleyici = RaspberryPiSubscriber(broker_ip=BROKER_ADRESI)

    drone_dinleyici.sistemi_baslat()