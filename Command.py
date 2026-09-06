
import tkinter as tk
from tkinter import messagebox
from SQL import SQL 


# Класс с помощью которого настраивается весь функционал взаимодействия пользователя с БД
class Commands:
   
    # Инициализая. Возможно было бы лучше не привязываться к конкретным полям ввода и сделать что то немного более универсальное 
    def __init__(self, bd, center_frame):
        self.bd = bd
        self.center_frame = center_frame
        # Поля ввода
        self.table_entry = None
        self.table_entry2 = None
        self.table_entry3 = None
        self.table_entry4 = None
        self.table_entry5 = None
        self.table_entry6 = None

        self.search_table_entry = None
        self.search_column_var = None
        self.search_column_menu = None
        self.search_entry = None


    # Метод очищения центральной области окна. Чтобы при нажатии другой кнопки, подготовить область для вывода другой информации 
    def clear_center(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()


    # Метод вывода ошибки 
    def show_error(self, message):
        label = tk.Label(self.center_frame, text=message, fg="red")
        label.place(relx=0.5, rely=0.5, anchor="center")
        return label

    # Метод по созданию контейнера для различных элементов окна (кнопки, поля для ввода, подсказки, заголовки и т.д.)
    def create_container(self):
        container = tk.Frame(self.center_frame)
        container.place(x=0, y=0, relwidth=1, relheight=1)
        return container
    
    # Метод для отображения ошибки внутри нужной области окна
    def show_error_in_container(self, container, message):
        tk.Label(container, text=message, fg="red").pack(pady=5)


    # Метод по созданию поля для ввода с подсказкой 
    def create_input_field(self, parent, label_text, hint_text, width=25):
        """Создает поле ввода с подписью и подсказкой"""
        frame = tk.Frame(parent)
        frame.pack(pady=10)
        
        tk.Label(frame, text=label_text, font=("Arial", 14)).pack()
        entry = tk.Entry(frame, font=("Arial", 14), width=width, bd=2, relief="groove")
        entry.pack()
        tk.Label(frame, text=hint_text, font=("Arial", 8), fg="gray").pack()
        
        return entry


    # Используется в методе по добавлению нового столбца 
    def create_column_input_fields(self, container):
        col_frame = tk.Frame(container)
        col_frame.pack(pady=10)
        tk.Label(col_frame, text="Column name:", font=("Arial", 14)).pack()
        column_entry = tk.Entry(col_frame, font=("Arial", 14), width=25, bd=2, relief="groove")
        column_entry.pack()
        tk.Label(col_frame, text="column name", font=("Arial", 8), fg="gray").pack()

        type_frame = tk.Frame(container)
        type_frame.pack(pady=10)
        tk.Label(type_frame, text="Data type:", font=("Arial", 14)).pack()
        type_entry = tk.Entry(type_frame, font=("Arial", 14), width=25, bd=2, relief="groove")
        type_entry.pack()
        tk.Label(type_frame, text="TEXT, INTEGER, DATE, etc.", font=("Arial", 8), fg="gray").pack()
        
        return column_entry, type_entry



    # Вывод названий существующих таблиц в одной БД
    def command_show_tables_name(self):
        self.clear_center()
        tables = SQL.get_tables(self.bd)
        
        if tables:
            container = self.create_container()
            text_widget = tk.Text(container, font=("Arial", 12), height=15, width=30,
                                wrap="none", relief="groove", bd=2)
            text_widget.pack(side="left", fill="both", expand=True)
            text_widget.insert("1.0", "Tables in BD:\n\n")
            for table in tables:
                text_widget.insert("end", f"-- {table}\n")
            text_widget.config(state="disabled")
            text_widget.focus_set()
        else:
            tk.Label(self.center_frame, text="Tables are not found", font=("Arial", 14)).pack(pady=20)


    # Метод для вывода содержимого выбранной таблицы по имени 
    def command_show_table_content(self):
        self.clear_center()
        table_name = self.table_entry.get().strip()
        
        if not table_name:
            self.show_error("Input name of table!")
            return

        self.table_entry.delete(0, tk.END)
        columns, data = SQL.get_table_data(self.bd, table_name)
        
        if not data:
            self.show_error(f"Table '{table_name}' is empty or not found")
            return

        container = self.create_container()
        tk.Label(container, text=f"Table: {table_name}", font=("Arial", 16, "bold")).pack(pady=10)

        text_frame = tk.Frame(container)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        text_widget = tk.Text(text_frame, font=("Courier", 14), wrap="none",
                            relief="groove", bd=2, height=15, width=80)
        text_widget.pack(side="left", fill="both", expand=True)

        formatted_text = self.format_table(columns, data)
        text_widget.insert("1.0", formatted_text)
        text_widget.config(state="disabled")
        text_widget.focus_set()


    # Команда для кнопки по созданию новой таблицы. Нужно ввести количество столбцов 
    def command_for_new_table(self):
        self.clear_center()
        
        try:
            table_columns = int(self.table_entry2.get().strip())
            if table_columns <= 0:
                raise ValueError
        except:
            self.show_error("Enter valid number of columns!")
            return
        
        self.table_entry2.delete(0, tk.END)
        container = self.create_container()
        columns_list = {'table_name': None, 'columns': []}

        for n in range(table_columns + 1):
            frame = tk.Frame(container)
            frame.pack(pady=5)
            
            if n == 0:
                tk.Label(frame, text="Name of table:", font=("Arial", 14)).pack(side="left", padx=5)
                entry = tk.Entry(frame, font=("Arial", 14), width=25, bd=2, relief="groove")
                entry.pack(side="left", padx=5)
                columns_list["table_name"] = entry
            else:
                col_frame = tk.Frame(frame)
                col_frame.pack(side="left", padx=10)
                
                tk.Label(col_frame, text=f"Name of column {n}:", font=("Arial", 14)).pack()
                entry = tk.Entry(col_frame, font=("Arial", 14), width=25, bd=2, relief="groove")
                entry.pack()
                tk.Label(col_frame, text="column name", font=("Arial", 8), fg="gray").pack()

                type_frame = tk.Frame(frame)
                type_frame.pack(side="left", padx=10)
                
                tk.Label(type_frame, text=f"Data type of column {n}:", font=("Arial", 14)).pack()
                entry2 = tk.Entry(type_frame, font=("Arial", 14), width=25, bd=2, relief="groove")
                entry2.pack()
                tk.Label(type_frame, text="TEXT, INTEGER, etc.", font=("Arial", 8), fg="gray").pack()

                columns_list['columns'].append((entry, entry2))

        button_frame = tk.Frame(container)
        button_frame.pack(pady=20)
        self.create_button(button_frame, "Create Table", 
                      lambda: self.create_new_table(columns_list, container), 
                      "#4CAF50")


    # Теперь само создание новой таблицы 
    def create_new_table(self, columns_list, container):
        table_name = columns_list['table_name'].get().strip()
        if not table_name:
            self.show_error_in_container(container, "Please enter table name!")
            return
        
        columns = []
        for name_entry, type_entry in columns_list['columns']:
            col_name = name_entry.get().strip()
            col_type = type_entry.get().strip()
            
            if not col_name:
                self.show_error_in_container(container, "Please enter all column names!")
                return
            if not col_type:
                col_type = "TEXT"
            columns.append({"name": col_name, "type": col_type})
        
        try:
            SQL.create_table(self.bd, table_name, columns)
            self.show_info(f"Table '{table_name}' created successfully!")
            self.table_entry2.delete(0, tk.END)
            self.clear_center()
        except Exception as e:
            self.show_error_in_container(container, f"Error: {str(e)}")


    # Форматирование таблицы, для ровного вывода в центральную часть окна 
    def format_table(self, columns, data):
        widths = [len(col) for col in columns]
        for row in data:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))

        result = []
        result.append(" | ".join(col.ljust(widths[i]) for i, col in enumerate(columns)))
        result.append("-" * (sum(widths) + len(columns) * 3 - 1))
        for row in data:
            result.append(" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)))
        return "\n".join(result)

    # Команда для удаления таблицы. Нужно ввести название таблицы и потом подтвердить 
    def command_for_delete_table(self):
        self.clear_center()
        table_name = self.table_entry3.get().strip()
        
        if not table_name:
            self.show_error("Enter valid name of table!")
            return

        self.table_entry3.delete(0, tk.END)
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete table '{table_name}'?", icon='warning')
        if not confirm:
            return
        
        try:
            SQL.delete_table(self.bd, table_name)
            self.show_info(f"Table '{table_name}' deleted successfully!")
            self.table_entry3.delete(0, tk.END)
            self.clear_center()
        except Exception as e:
            self.show_error(f"Error: {str(e)}")


    # Команда для добавления столбца в таблицу 
    def command_for_add_new_column(self):
        self.clear_center()
        table_name = self.table_entry4.get().strip()
        
        if not table_name:
            self.show_error("Enter valid name of table!")
            return
        
        try:
            if not SQL.table_exists(self.bd, table_name):
                self.show_error(f"Table '{table_name}' does not exist!")
                return
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
            return

        self.table_entry4.delete(0, tk.END)
        container = self.create_container()
        tk.Label(container, text=f"Add column to table: {table_name}",
                font=("Arial", 16, "bold")).pack(pady=10)
        
        column_entry, type_entry = self.create_column_input_fields(container)
        
        button_frame = tk.Frame(container)
        button_frame.pack(pady=20)
        self.create_button(button_frame, "Add Column", 
                      lambda: self.add_column_to_table(container, table_name, column_entry, type_entry),
                      "#4CAF50")


    # Добавление столбца в структуру таблицы БД
    def add_column_to_table(self, container, table_name, column_entry, type_entry):
        column_name = column_entry.get().strip()
        column_type = type_entry.get().strip()
        
        if not column_name:
            self.show_error_in_container(container, "Please enter column name!")
            return
        
        if not column_type:
            column_type = "TEXT"
        
        try:
            SQL.add_column(self.bd, table_name, column_name, column_type)
            self.show_info(f"Column '{column_name}' added successfully to table '{table_name}'!")
            column_entry.delete(0, tk.END)
            type_entry.delete(0, tk.END)
            self.table_entry4.delete(0, tk.END)
            self.clear_center()
        except Exception as e:
            self.show_error_in_container(container, f"Error: {str(e)}")


    # Команда по добавлению новой запсии в таблицу 
    def command_for_new_recording(self):
        self.clear_center()
        table_name = self.table_entry5.get().strip()
        
        if not table_name:
            self.show_error("Input name of table!")
            return

        self.table_entry5.delete(0, tk.END)
        columns_info = SQL.get_table_structure(self.bd, table_name)
        
        if not columns_info:
            self.show_error(f"Table '{table_name}' does not exist!")
            return
        
        container = self.create_container()
        tk.Label(container, text=f"Add record to table: {table_name}",
                font=("Arial", 16, "bold")).pack(pady=10)
        
        entries = {}
        for col in columns_info:
            if col.get('default') and 'nextval' in str(col['default']).lower():
                continue
            
            hint_text = f"type: {col['type']}"
            if not col['nullable']:
                hint_text += " (NOT NULL)"
            
            entry = self.create_input_field(container, f"{col['name']}:", hint_text)
            entries[col['name']] = entry
        
        if not entries:
            self.show_error_in_container(container, "No columns available for insertion!")
            return
        
        button_frame = tk.Frame(container)
        button_frame.pack(pady=20)
        self.create_button(button_frame, "Add Record", 
                      lambda: self.add_record_to_table(container, table_name, columns_info, entries),
                      "#4CAF50")


    # Добавление запсии в таблицу 
    def add_record_to_table(self, container, table_name, columns_info, entries):
        values = []
        column_names = []
        
        for col in columns_info:
            if col.get('default') and 'nextval' in str(col['default']).lower():
                continue
            
            col_name = col['name']
            value = entries[col_name].get().strip()
            
            if not col['nullable'] and not value:
                self.show_error_in_container(container, f"Please enter value for {col_name}!")
                return
            
            if not value and col['nullable']:
                values.append(None)
            else:
                values.append(value)
            
            column_names.append(col_name)
        
        try:
            SQL.add_record(self.bd, table_name, column_names, values)
            messagebox.showinfo(f"Record added successfully to table '{table_name}'!")
            
            for entry in entries.values():
                entry.delete(0, tk.END)
            self.table_entry5.delete(0, tk.END)
            self.clear_center()
            
        except Exception as e:
            self.show_error_in_container(container, f"Error: {str(e)}")


    # Команда для редактирвоания записи в таблице. Нужно ввести имя таблицы, после чего происходит отображение всех записей в теблице
    # которые можно редактировать по двойному нажатию на нужную запись 
    def command_edit_record(self):
        self.clear_center()
        table_name = self.table_entry6.get().strip()
        
        if not table_name:
            self.show_error("Input name of table!")
            return
        
        try:
            if not SQL.table_exists(self.bd, table_name):
                self.show_error(f"Table '{table_name}' does not exist!")
                return
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
            return
        
        self.table_entry6.delete(0, tk.END)
        
        self.show_table_for_editing(table_name)


    # Вспомогательный метод для вывода содержимого таблицы с возможностью редактирования записей по двойному клику и выводу 
    # меню для поиска нужной записи  
    def show_table_for_editing(self, table_name):
        columns, data = SQL.get_table_data(self.bd, table_name)
        
        if not data:
            self.show_error(f"Table '{table_name}' is empty!")
            return
        
        container = self.create_container()
        
        tk.Label(container, text=f"Table: {table_name}", 
                font=("Arial", 18, "bold"), fg="#1a5276").pack(pady=10)
        
        search_frame = tk.Frame(container, bg="#e8f4f8", relief="groove", bd=1)
        search_frame.pack(fill="x", padx=15, pady=5)
        
        from tkinter import ttk
        
        tk.Label(search_frame, text="Search in:", font=("Arial", 10), bg="#e8f4f8").pack(side="left", padx=5)
        
        search_column_menu = ttk.Combobox(search_frame, values=columns, width=15, state="readonly")
        search_column_menu.pack(side="left", padx=5)
        if columns:
            search_column_menu.set(columns[0])
        
        search_entry = tk.Entry(search_frame, font=("Arial", 10), width=20, bd=2, relief="groove")
        search_entry.pack(side="left", padx=5)

        # Вспомогательный метод. Применяет выбранную колонку из списка и считывает значение из поля для ввода 
        def apply_search():
            search_text = search_entry.get().strip()
            search_column = search_column_menu.get()  
            
            print(f"Search column: '{search_column}'")
            print(f"Search text: '{search_text}'")
            
            if not search_text:
                return
            
            try:
                filtered_data = SQL.search_records(self.bd, table_name, search_column, search_text)
                
                if not filtered_data:
                    text_widget.config(state="normal")
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", f"No records found for '{search_text}' in column '{search_column}'")
                    text_widget.config(state="disabled")
                    return
                
                formatted_text = self.format_table(columns, filtered_data)
                text_widget.config(state="normal")
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", formatted_text)
                text_widget.config(state="disabled")
                
            except Exception as e:
                print(f"Search error: {e}")
                messagebox.showerror("Error", f"Search error: {str(e)}")

        # Очищение настроек поиска 
        def clear_search():
            formatted_text = self.format_table(columns, data)
            text_widget.config(state="normal")
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", formatted_text)
            text_widget.config(state="disabled")
            search_entry.delete(0, tk.END)
        
        self.create_button(search_frame, "🔍 Search", apply_search, "#2e86c1")
        self.create_button(search_frame, "✕ Clear", clear_search, "#e74c3c")
        
        tk.Label(search_frame, text="Double-click to edit", 
                font=("Arial", 9, "italic"), bg="#e8f4f8", fg="gray").pack(side="right", padx=10)
        
        text_frame = tk.Frame(container, bg="white")
        text_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        text_widget = tk.Text(text_frame, font=("Courier", 14), wrap="none",
                            relief="groove", bd=2, height=15)
        text_widget.pack(side="left", fill="both", expand=True)
        
        formatted_text = self.format_table(columns, data)
        text_widget.insert("1.0", formatted_text)
        text_widget.config(state="disabled")

        # Обработка двойного клика 
        def on_double_click(event):
            index = text_widget.index(f"@{event.x},{event.y}")
            line = int(index.split('.')[0])
            if line >= 3 and line - 3 < len(data):
                record_id = data[line - 3][0]
                self.open_edit_window(table_name, columns, record_id, None, container)
        
        text_widget.bind("<Double-1>", on_double_click)
        

    # Метод для отображения окна редактирования запсии
    def open_edit_window(self, table_name, columns, record_id, tree, parent_container):
        record_data = SQL.get_record_by_id(self.bd, table_name, record_id)
        
        if not record_data:
            self.show_error_in_container(parent_container, "Record not found!")
            return
        
        edit_window = tk.Toplevel(self.center_frame)
        edit_window.title(f"Edit Record - {table_name}")
        edit_window.geometry("400x550")
        edit_window.transient(self.center_frame)
        edit_window.grab_set()
        
        main_frame = tk.Frame(edit_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"Editing record {record_id}", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        entries = {}
        for col in columns:
            if col.lower() == 'id':
                continue
            
            frame = tk.Frame(main_frame)
            frame.pack(pady=5, fill="x")
            
            tk.Label(frame, text=f"{col}:", font=("Arial", 12), width=15, anchor="w").pack(side="left", padx=5)
            
            entry = tk.Entry(frame, font=("Arial", 12), width=25, bd=2, relief="groove")
            entry.pack(side="left", padx=5, fill="x", expand=True)
            
            current_value = record_data.get(col, "")
            entry.insert(0, str(current_value) if current_value is not None else "")
            entries[col] = entry
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def save_changes():
            new_data = {}
            for col, entry in entries.items():
                value = entry.get().strip()
                if value:
                    new_data[col] = value
                else:
                    new_data[col] = None
            
            try:
                SQL.update_record(self.bd, table_name, record_id, new_data)
                messagebox.showinfo("Success", f"Record {record_id} updated successfully!")
                edit_window.destroy()
                
                self.show_table_for_editing(table_name)
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        def delete_record():
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete record {record_id}?",
                icon='warning'
            )
            
            if not confirm:
                return
            
            try:
                SQL.delete_record(self.bd, table_name, record_id)
                messagebox.showinfo("Success", f"Record {record_id} deleted successfully!")
                edit_window.destroy()
                
                self.show_table_for_editing(table_name)
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        self.create_button(button_frame, "Save", save_changes, "#4CAF50")
        self.create_button(button_frame, "Delete Record", delete_record, "#f44336")
        self.create_button(button_frame, "Cancel", edit_window.destroy, "#9e9e9e")


    def create_button(self, parent, text, command, bg_color="#4CAF50", fg_color="white"):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=16,
            height=2,
            bg=bg_color,
            fg=fg_color,
            relief="groove",
            bd=2
        )
        button.pack(side="left", padx=10)
        return button


    