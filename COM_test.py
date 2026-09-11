import serial
import time
import serial.tools.list_ports
import tkinter as tk
from tkinter import scrolledtext
# =========================================================
# НАСТРОЙКИ [)>\x1e06\x1d25SABS13456789261\x1e\x04
# KRUA117O1115418
# 6115571685611
# =========================================================

class Window:
    def __init__(self, root):  
        self.root = root
        self.root.title("Serial Monitor")  
        self.root.geometry("600x500")

        self.ser = None
        self.reading = False

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill=tk.X, pady=10, padx=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.refresh_button = tk.Button( root, text = "Обновить список портов", command = self.refresh_com_ports)
        self.refresh_button.pack(pady=(0, 10))

        self.disconnect_button = tk.Button(root, text = "Отключиться", command = self.disconnect_com)
        self.disconnect_button.pack(pady=(0,10))
        self.refresh_com_ports()

    def refresh_com_ports(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        ports = serial.tools.list_ports.comports()
        
        if not ports:
            tk.Label(self.button_frame, text="Порты не найдены").pack()
            return
        
        for port in ports:
            self.button = tk.Button(
                self.button_frame,
                text=f"Подключиться к {port.device}",
                command=lambda p=port.device: self.connect_com(p)  # ← передаём порт
            )
            self.button.pack(side=tk.LEFT, padx=5, pady=5)

    def connect_com(self, port):
        """Подключение к выбранному COM-порту"""
        try:
            # Закрываем предыдущее соединение
            if self.ser and self.ser.is_open:
                self.ser.close()
            
            self.ser = serial.Serial(port, baudrate=9600, timeout=1)
            self.text_area.insert(tk.END, f"Подключено к {port}\n")
            self.text_area.see(tk.END)
            
            # Запускаем чтение
            self.reading = True
            self.read_from_port()
            
        except Exception as e:
            self.text_area.insert(tk.END, f"Ошибка подключения к {port}: {e}\n")
            self.text_area.see(tk.END)

    def read_from_port(self):
        """Чтение данных из порта"""
        if not self.reading or not self.ser or not self.ser.is_open:
            return
        try:
            if self.ser.in_waiting > 0 :
                data = self.ser.read(self.ser.in_waiting)
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    text = data.decode('utf-8', errors='replace')
                self.log(text.strip())
        except serial.SerialException as e:
            self.log("Ошибка чтения {e}")
            self.reading = False
            return

        self.root.after(50, self.read_from_port)


    def disconnect_com(self):
        """Отключение от порта"""
        self.reading = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.log("Отключено")
        self.disconnect_button.config(state="disabled")

    def log(self, message):
        """Вывод сообщения в текстовую область"""
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def on_close(self):
        """Обработка закрытия окна"""
        self.reading = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Window(root)
    root.mainloop()

'''
ser = serial.Serial('COM5', baudrate=9600, timeout=1)

while True:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        print("Get data:", data.decode('utf-8'))
    time.sleep(1)
'''