import requests
from serial import *
from datetime import  datetime
from tkinter import  *
from tkinter import ttk


PRESET_Value = 0xFFFF
POLYNOMIAL = 0x8408

port = ['COM1', 'COM2', 'COM3', 'COM4']
reader_add = "FF"
test_serial = Serial('COM3', 57600, timeout=0.1);

now = datetime.now()
dt_string = now.strftime("%d/%m/%y %H:%M:%S")

#SCANNER UNTUK RFID
#scan
INVENTORY1 = f'06 {reader_add} 01 00 06' #Membaca TID
INVENTORY2 = f'04 {reader_add} 0F' #Membaca EPC

#Read EPC
readTagMem = f'12 {reader_add} 02 02 11 22 33 44 01 00 04 00 00 00 00 00 02'

#Change EPC
writeEpc = '0F 03 04 03 00 00 00 00 11 22 33 44 55 66'

#Set Data
setAddress = '05 03 24 00'

#URL API
url = 'https://reqres.in/api/users'


def crc(cmd):
    cmd = bytes.fromhex(cmd)
    uiCrcValue = PRESET_Value
    for x in range((len(cmd))):
        uiCrcValue = uiCrcValue ^ cmd[x]
        for y in range(8):
            if(uiCrcValue & 0x0001):
                uiCrcValue = (uiCrcValue >> 1) ^ POLYNOMIAL
            else:
                uiCrcValue = uiCrcValue >> 1

        crc_H = (uiCrcValue >> 8) & 0xFF
        crc_L = uiCrcValue & 0xFF
        cmd = cmd + bytes([crc_L])
        cmd = cmd + bytes([crc_H])
        return cmd


def send_cmd(cmd):
    data = crc(cmd)
    print(data)
    test_serial.write(data)
    response = test_serial.read(512)
    response_hex = response.hex().upper()
    hex_list = [response_hex[i:i + 2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)
    uid = INVENTORY1[-6:]
    uid_no = uid.replace(" ", "")
    inventory = {
        "uid": str(uid_no),
        "time" : str(dt_string)

    }
    if(hex_space.find("FB") != -1):
        cmd = "Data Kosong"
    elif(hex_space.find("FE") != -1):
        cmd = "Kartu Tidak Terdeteksi"
    elif(hex_space == ""):
        cmd = "Data Tidak Ada"
    else:
        send = requests.post(url, json=inventory)
        print(send.json())

    return cmd


def btnConfigCallback():
    global value
    value = lbReader.get()

    reader_add = value

    return  reader_add



INV1 = send_cmd(INVENTORY1)
INV2 = send_cmd(INVENTORY2)

main = Tk()
main.geometry("800x500")

# FRAME UNTUK SETUP READER
configFrame = ttk.LabelFrame(main)
configFrame.configure(height=150, width=300, text="Setup Scanner")
configFrame.grid(column=0, row=0)

lbPort = ttk.Label(configFrame, text="COM Port communication", anchor="w")
lbPort.grid(column=0, row=0)

cbPort = ttk.Combobox(configFrame)
cbPort.configure(values=port)
cbPort.grid(column=0, row=1)

lbReader = ttk.Label(configFrame, text="ID Reader")
lbReader.grid(column=1, row=0)

lbReader = ttk.Entry(configFrame)
lbReader.grid(column=1, row=1)
lbReader.insert("0", reader_add)
lbReader.configure(width=30)

btnReader = ttk.Button(configFrame, command=btnConfigCallback)
btnReader.configure(text="Open Port COM")
btnReader.grid(column=2, row=1)

lbreaderNow = ttk.Label(configFrame, text=f"COMP Port : {reader_add}")
lbreaderNow.grid(column=1, row=2)


    # DATA YANG DI BACA KARTU
frame = ttk.LabelFrame(main)
frame.configure(height=150, width=300, text="Data Kartu")
frame.grid(column=0, row=1)

# LABEL
lb1 = ttk.Label(frame, text="INVENTORY 1", foreground="blue", font=("Helvetica", 12), padding=10)
lb1.grid(column=0, row=0)
lb2 = ttk.Label(frame, text="INVENTORY 2", foreground="blue", font=("Helvetica", 12), padding=10)
lb2.grid(column=0, row=1)

ev1 = ttk.Entry(frame)
ev1.grid(column=1, row=0)
ev1.insert("0", INV1)
ev1.configure(state="readonly", width=50)

ev2 = ttk.Entry(frame)
ev2.grid(column=1, row=1)
ev2.insert("0", INV2)
ev2.configure(state="readonly", width=50)

main.mainloop()

