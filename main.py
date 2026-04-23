import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime, timedelta
import os

DATA_FILE = 'project_good_habits\habits.json'

class HabitTracker:
    def __init__(self, root):
        self.root = root
        self.root.title(" ")
        self.root.geometry("800x600")
        self.root.update_idletasks()  # Для правильного центрирования
        

        # Загрузка данных
        self.habits = self.load_data()
        self.current_date = datetime.now().date()
        
        self.setup_ui()
        self.refresh_display()
        

    # Загрузка привычек из файла формата JSON
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {k: v for k, v in data.items()}
                
            except FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError:     # Частые ошибки при работе с JSON.
                return {}
        return {}
    

    # Сохранение привычек в файле формата JSON
    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.habits, f, ensure_ascii=False, indent=2)
    

    # Пользовательский интерфейс приложения.
    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root, text="Трекер привычек", font=("Arial", 20, "bold"))
        title.pack(pady=10)
        
        # Дата
        self.date_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.date_label.pack()
        
        # Главный фрейм с таблицей слева и кнопками справа
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=10)
        
        # Левая часть: таблица привычек + скроллбар
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(left_frame, columns=("Habit", "Streak", "Percent", "Done"), 
                            show="headings", height=15)
        self.tree.heading("Habit", text="Привычка")
        self.tree.heading("Streak", text="Серия (дней)")
        self.tree.heading("Percent", text="% выполнения")
        self.tree.heading("Done", text="Выполнено")
        self.tree.column("Habit", width=250)
        self.tree.column("Streak", width=100)
        self.tree.column("Percent", width=100)
        self.tree.column("Done", width=100)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Правая часть: кнопки в нужном порядке
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(side=tk.RIGHT, padx=(10,0))


        # Кнопки:
        # Кнопка "Добавить привычку"
        tk.Button(btn_frame, text="➕ Добавить\nпривычку", command=self.add_habit, 
                bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=14, height=2).pack(pady=(0,10))

        # Кнопки: Пред. день + След. день
        nav_frame = tk.Frame(btn_frame)
        nav_frame.pack(pady=5)

        tk.Button(nav_frame, text="←", command=self.prev_day, 
                bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=7).pack(side=tk.LEFT, padx=2)
        tk.Button(nav_frame, text="→", command=self.next_day, 
                bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=7).pack(side=tk.LEFT, padx=2)

        # Кнопка "Сегодня"
        tk.Button(btn_frame, text="📅 Сегодня", command=self.today, 
                bg="#FF9800", fg="white", font=("Arial", 11, "bold"), width=14, height=2).pack(pady=(5,0))
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Отметить соблюдение", command=self.mark_done)
        self.context_menu.add_command(label="Редактировать название привычки", command=self.edit_habit)
        self.context_menu.add_command(label="Удалить", command=self.delete_habit)
        self.tree.bind("<Button-3>", self.show_context_menu)


    # Обновление отображения
    def refresh_display(self):

        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.date_label.config(text=f"Дата: {self.current_date.strftime('%d.%m.%Y')}")
        
        for habit_name, data in self.habits.items():
            streak = self.calculate_streak(habit_name)
            percent = self.calculate_percent(habit_name)
            done_today = self.is_done_today(habit_name)
            
            self.tree.insert("", "end", values=(
                habit_name,
                streak,
                f"{percent:.1f}%",
                "✓" if done_today else "✗"
            ))
    

    # Расчёт текущей серии дней
    def calculate_streak(self, habit_name):
        data = self.habits.get(habit_name, [])
        streak = 0
        for i in range(len(data)-1, -1, -1):
            if data[i]['date'] == self.current_date.strftime('%Y-%m-%d'):
                streak += 1
                break
            elif data[i]['done']:
                streak += 1
            else:
                break
        return streak
    

    # Процент выполнения за 30 дней
    def calculate_percent(self, habit_name):
        data = self.habits.get(habit_name, [])
        if not data:
            return 0
        
        recent = []
        target_date = self.current_date
        for _ in range(30):
            recent.append(False)
            target_date -= timedelta(days=1)
        
        for entry in data[-30:]:  # Последние 30 дней
            try:
                entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
                if self.current_date - timedelta(days=30) <= entry_date <= self.current_date:
                    idx = (self.current_date - entry_date).days
                    recent[29 - idx] = entry['done']
            except:
                continue
        
        return sum(recent) / len(recent) * 100
    

    # Соблюдена ли привычка сегодня.
    def is_done_today(self, habit_name):
        data = self.habits.get(habit_name, [])
        today_str = self.current_date.strftime('%Y-%m-%d')
        for entry in data:
            if entry['date'] == today_str:
                return entry['done']
        return False
    
    
    # Всплывающее окно по центру основного окна
    def show_centered_dialog(self, title, message, width=400, height=200, buttons=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрирование
        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        x = root_x + (root_width - width) // 2
        y = root_y + (root_height - height) // 2
        dialog.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        
        dialog.configure(bg="#f0f0f0")
        
        msg_label = tk.Label(dialog, text=message, font=("Arial", 12), 
                            bg="#f0f0f0", pady=30, wraplength=width-50, justify=tk.CENTER)
        msg_label.pack(expand=True)
        
        btn_frame = tk.Frame(dialog, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        if buttons is None:
            buttons = [{'text': 'OK', 'bg': '#4CAF50', 'fg': 'white'}]
        
        def create_button_handler(btn_cmd):
            def handler():
                if btn_cmd is not None:
                    btn_cmd()
                dialog.destroy()
            return handler
        
        for btn_config in buttons:
            cmd = btn_config.get('command')
            tk.Button(btn_frame, text=btn_config['text'], 
                    command=create_button_handler(cmd),
                    bg=btn_config.get('bg', '#4CAF50'), fg=btn_config.get('fg', 'white'),
                    font=("Arial", 11, "bold"), width=12, height=1).pack(side=tk.LEFT, padx=10)
        
        dialog.update_idletasks()


    # Добавление новой привычки в список.
    def add_habit(self):
        name = simpledialog.askstring("➕ Новая привычка", "Введите название привычки:",
                                    initialvalue="", parent=self.root)
        if name and name.strip():
            name = name.strip()
            if name in self.habits:
                self.show_centered_dialog("⚠️ Ошибка", f"Привычка '{name}' уже существует!")
            else:
                self.habits[name] = []
                self.save_data()
                self.refresh_display()
                self.show_centered_dialog("✅ Готово", f"Добавлена привычка: {name}")

    
    def mark_done(self):
        selection = self.tree.selection()
        if selection:
            habit = self.tree.item(selection)['values'][0]
            today_str = self.current_date.strftime('%Y-%m-%d')
            
            data = self.habits.get(habit, [])
            # Заменяем или добавляем запись за сегодня
            for i, entry in enumerate(data):
                if entry['date'] == today_str:
                    data[i]['done'] = True
                    break
            else:
                data.append({'date': today_str, 'done': True})
            
            self.save_data()
            self.refresh_display()
    

    # Переключение на предыдущий день
    def prev_day(self):
        self.current_date -= timedelta(days=1)
        self.refresh_display()
    
    # Переключение на следующий день
    def next_day(self):
        self.current_date += timedelta(days=1)
        self.refresh_display()
    

    # Возвращаемся на сегодня.
    def today(self):
        self.current_date = datetime.now().date()
        self.refresh_display()
    

    # Показывает контектное меню при нажатии правой кнопки мыши после выделения привычки нажатием левой.
    def show_context_menu(self, event):
        selection = self.tree.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)
    

    # Редактирование названия привычки
    def edit_habit(self):
        selection = self.tree.selection()
        if selection:
            old_name = self.tree.item(selection)['values'][0]
            new_name = simpledialog.askstring("✏️ Редактировать", "Новое название:",
                                            initialvalue=old_name, parent=self.root)
            if new_name and new_name.strip() != old_name:
                new_name = new_name.strip()
                if new_name in self.habits:
                    self.show_centered_dialog("⚠️ Ошибка", f"Название '{new_name}' уже занято!")
                else:
                    self.habits[new_name] = self.habits.pop(f"{old_name}")
                    self.save_data()
                    self.refresh_display()
                    self.show_centered_dialog("✅ Готово", f"Переименовано в: {new_name}")
    

    # Удалить привычку
    def delete_habit(self):
        selection = self.tree.selection()
        if selection:
            habit = self.tree.item(selection)['values'][0]
            
            def confirm_delete():
                try:
                    del self.habits[habit]
                except KeyError:
                    del self.habits[f"{habit}"]

                self.save_data()
                self.refresh_display()
            
            buttons = [
                {'text': '❌ Да, удалить', 'command': confirm_delete, 'bg': '#f44336', 'fg': 'white'},
                {'text': '❌ Отмена', 'command': None, 'bg': '#4CAF50', 'fg': 'white'}
            ]
            
            self.show_centered_dialog("🗑️ Удалить привычку", 
                                    f"Удалить привычку '{habit}'?\nВсе данные будут потеряны!",
                                    buttons=buttons)

root = tk.Tk()
app = HabitTracker(root)
root.mainloop()