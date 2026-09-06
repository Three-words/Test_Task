import tkinter as tk
from Connect import BD
from tkinter import messagebox
from Command import Commands

"""
Родительский класс для создания окна
Тут идет настройка размеров окна/подстраивание размеров окна под экран 
и разделение окна на области (это понадобится для главного окна)
"""
class Window:
    height = 0
    width = 0
    fullscreen = False
    resizable = True
    background = "white"
    text_color = "black"

    def __init__(self, resizable=None, height=0, width=0, fullscreen=None):
        self.root = tk.Tk()
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.resizable = resizable

        if self.fullscreen or self.width == 0 or self.height == 0:
            self.width = self.root.winfo_screenwidth()
            self.height = self.root.winfo_screenheight()

        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(self.resizable, self.resizable)
        self.root.title("Connect/Disconnect BD")


    def close_window(self):
        if self.root:
            self.root.quit()
            self.root.destroy()

    def run(self):
        if self.root is None:
            raise Exception("ERROR")
        self.root.mainloop()

    def show_info(self, message):
        messagebox.showinfo("Информация", message)

    def place_window(self, color=None, column_number=None):
        frame = tk.Frame(
            self.root,
            bg=color,
            relief="solid",
            bd=1
        )
        frame.grid(row=0, column=column_number, sticky="nsew", padx=2, pady=2)
        return frame


"""
Дочерний класс создания окна
Тут настраивается визуал основного окна для взаимодействия с БД
Применяется метод родительского класса по разделению окна на области,
добавление кнопок и полей ввода в основное меню взаимодействия с БД 

Этот класс является связующим для остальных классов (возможно не очень хорошая идея так делать)
"""
class SeconWindow(Window):
    bd = None
    commands = None

    def __init__(self, bd=None, resizable=None, height=0, width=0, fullscreen=None):
        super().__init__(resizable, height, width, fullscreen)
        self.root.title("Main Window")
        self.bd = bd
        self.create_layout()

    def create_layout(self):
        left = self.place_window("lightblue", 0)
        center = self.place_window("white", 1)
        right = self.place_window("lightblue", 2)
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=5)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        center.grid_propagate(False)
        self.center_frame = center
        
        # Создаем экземпляр Commands
        self.commands = Commands(self.bd, self.center_frame)
        self.right_place(right)

    # Метод по настройке правой области окна (тут распологается основное меню с кнопками и полями для ввода)
    def right_place(self, frame):
        tk.Label(frame, text="Menu", font=("Arial", 14, "bold")).pack(pady=20)

        self.button_for_menu(frame, "Show existing tables", self.commands.command_show_tables_name)

        # Общие настройки для полей ввода
        entries = [
            ("Show table", self.commands.command_show_table_content, "table_entry"),
            ("New table", self.commands.command_for_new_table, "table_entry2"),
            ("Delete table", self.commands.command_for_delete_table, "table_entry3"),
            ("Add new column", self.commands.command_for_add_new_column, "table_entry4"),
            ("Add new record", self.commands.command_for_new_recording, "table_entry5"),
            ("Edit record", self.commands.command_edit_record, "table_entry6")
        ]

        for text, command, attr_name in entries:
            entry_frame = tk.Frame(frame, bg="lightblue")
            entry_frame.pack(pady=5)
            self.button_for_menu(entry_frame, text, command, side="left")
            entry = tk.Entry(entry_frame, font=("Arial", 10), width=20, bd=2, relief="groove")
            entry.pack(side="left", padx=(5, 0))
            # Сохраняем поле ввода в commands
            setattr(self.commands, attr_name, entry)


    # Этот медот немного упрощает создание кнопок 
    def button_for_menu(self, frame, text, command=None, side=None):
        button = tk.Button(
            frame,
            text=text,
            command=command,
            width=16,
            height=2,
            bg="white",
            fg="black",
            relief="groove",
            bd=2
        )
        
        if side:
            button.pack(side=side, padx=(0, 5))
        else:
            button.pack(pady=10)
        return button


    
# Немного бесполезный класс, используется только в функционале стартового окна
class Button:
    master = None
    text = "Button"
    command = None
    width = 0
    height = 0
    fg = "black"
    bg = "lightblue"
    state = "normal"
    anchor = "center"
    front = "Arial"
    front_size = 12

    def __init__(self, master=None, text=None, command=None, x=None, y=None, width=0, height=0):
        self.master = master
        self.width = width
        self.height = height
        self.command = command
        self.text = text

        self.button = tk.Button(
            master=self.master,
            text=self.text,
            width=self.width,
            height=self.height,
            command=self.command,
            fg=self.fg,
            bg=self.bg
        )
        if x is not None and y is not None:
            self.button.place(x=x, y=y)

    def set_text(self, new_text=None):
        self.text = new_text
        self.button.config(text=new_text)

    def set_command(self, new_command=None):
        self.command = new_command
        self.button.config(command=new_command)


# Создание второго окна, если удалось подключиться к БД
def button_connection(BD):
    BD.Connect_BD()
    if BD.open:
        window = SeconWindow(bd=BD, resizable=True)
        window.run()




# По хорошему -- это main программы
window = Window(True, 500, 300)
bd = BD(window)
button_start = Button(window.root, "Start", None, 90, 150, 15, 3)
button_start.set_command(lambda: button_connection(bd))

button_exit = Button(window.root, "Disconnect", None, 90, 230, 15, 3)
button_exit.set_command(bd.Disconnect_BD)

window.run()