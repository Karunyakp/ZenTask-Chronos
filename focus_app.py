import tkinter as tk
from tkinter import ttk, messagebox, Menu
import math
import json
import os
from datetime import datetime, date
import platform
import sys

if platform.system() == 'Windows':
    import winsound

DATA_FILE = "zentask_data.json"

class DataManager:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename

    def save_data(self, data):
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        default_data = {
            'tasks': [],
            'timer_settings': {'mode': 'Focus', 'seconds': 25 * 60},
            'custom_timer_settings': {'focus_time': 25, 'short_break_time': 5, 'long_break_time': 15},
            'pomodoro_cycle': 0,
            'current_filter': 'All',
            'current_sort_order': 'None',
            'completed_focus_sessions': 0,
            'total_focus_time': 0,
            'current_theme': 'dark',
            'xp': 0,
            'level': 1
        }

        if not os.path.exists(self.filename):
            return default_data
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for key, value in default_data.items():
                    if key not in data:
                        data[key] = value
                return data
        except (IOError, json.JSONDecodeError):
            return default_data

class ThemeManager:
    def __init__(self, root, style_obj, initial_theme='dark'):
        self.root = root
        self.style = style_obj
        self.current_theme = initial_theme
        
        self.themes = {
            'dark': {
                'bg': '#0f172a', 'card': '#1e293b', 'text': '#f1f5f9', 
                'text_dim': '#94a3b8', 'primary': '#6366f1', 
                'secondary': '#f59e0b', 'success': '#10b981', 'danger': '#ef4444',
                'accent': '#818cf8'
            },
            'light': {
                'bg': '#f8fafc', 'card': '#ffffff', 'text': '#1e293b', 
                'text_dim': '#64748b', 'primary': '#4f46e5', 
                'secondary': '#f97316', 'success': '#16a34a', 'danger': '#dc2626',
                'accent': '#a5b4fc'
            }
        }
        self.colors = self.themes[self.current_theme]
        self.apply_theme()

    def switch_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme()
            return True
        return False

    def apply_theme(self):
        self.colors = self.themes[self.current_theme]
        self.root.configure(bg=self.colors['bg'])
        self.setup_styles()

    def setup_styles(self):
        self.style.theme_use('clam')
        c = self.colors
        
        self.style.configure('TFrame', background=c['bg'])
        self.style.configure('Card.TFrame', background=c['card'], relief='flat')
        
        self.style.configure('TLabel', background=c['bg'], foreground=c['text'], font=('Segoe UI', 11))
        self.style.configure('Card.TLabel', background=c['card'], foreground=c['text'], font=('Segoe UI', 11))
        self.style.configure('Header.TLabel', background=c['bg'], foreground=c['text'], font=('Segoe UI', 22, 'bold'))
        self.style.configure('Stat.TLabel', background=c['card'], foreground=c['primary'], font=('Segoe UI', 24, 'bold'))
        
        self.style.configure('TButton', font=('Segoe UI', 11, 'bold'), borderwidth=0, background=c['card'], foreground=c['text'], focuscolor=c['bg'], padding=8)
        self.style.map('TButton', background=[('active', c['text_dim']), ('pressed', c['text_dim'])], foreground=[('active', 'white')])
        
        self.style.configure('Primary.TButton', background=c['primary'], foreground='white', font=('Segoe UI', 12, 'bold'), borderwidth=0, padding=10)
        self.style.map('Primary.TButton', background=[('active', c['accent']), ('pressed', c['secondary'])], foreground=[('active', 'white'), ('pressed', 'white')])

        self.style.configure('Secondary.TButton', background=c['secondary'], foreground='white', font=('Segoe UI', 12, 'bold'), borderwidth=0, padding=10)
        self.style.map('Secondary.TButton', background=[('active', c['primary']), ('pressed', c['accent'])])

        self.style.configure('Danger.TButton', background=c['danger'], foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=8)
        self.style.map('Danger.TButton', background=[('active', '#dc2626'), ('pressed', '#991b1b')])

        self.style.configure('TEntry', fieldbackground=c['card'], foreground=c['text'], insertcolor=c['primary'], borderwidth=1, relief='solid', padding=5)
        self.style.configure('TSpinbox', fieldbackground=c['card'], foreground=c['text'], arrowcolor=c['text'], borderwidth=1, relief='solid')
        self.style.configure('TCombobox', fieldbackground=c['card'], foreground=c['text'], selectbackground=c['primary'], borderwidth=1, relief='solid')
        
        self.style.configure('TNotebook', background=c['bg'], borderwidth=0)
        self.style.configure('TNotebook.Tab', background=c['bg'], foreground=c['text_dim'], padding=[20, 10], font=('Segoe UI', 11, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', c['card'])], foreground=[('selected', c['primary'])])

    def apply_to_widget(self, widget, role, state=None):
        c = self.colors
        try:
            if role == 'root': widget.configure(bg=c['bg'])
            elif role == 'canvas': widget.configure(bg=c['card'], highlightthickness=0)
            elif isinstance(widget, tk.Label):
                if role == 'card_label': widget.configure(bg=c['card'], fg=c['text'])
                else: widget.configure(bg=c['bg'], fg=c['text'])
            elif isinstance(widget, tk.Frame):
                if role == 'card': widget.configure(bg=c['card'])
                else: widget.configure(bg=c['bg'])
            elif isinstance(widget, tk.Entry):
                 widget.configure(bg=c['card'], fg=c['text'], insertbackground=c['text'])
        except:
            pass

class ZenTaskChronos:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenTask Chronos")
        self.root.geometry("600x800")
        
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Icon load error: {e}")
        
        self.data_mgr = DataManager()
        self.data = self.data_mgr.load_data()
        
        self.theme_mgr = ThemeManager(root, ttk.Style(), self.data['current_theme'])
        self.widgets_to_theme = []

        self.timer_running = False
        self.timer_seconds = self.data['timer_settings']['seconds']
        self.current_mode = self.data['timer_settings']['mode']
        
        self.var_filter = tk.StringVar(value=self.data['current_filter'])
        self.var_sort = tk.StringVar(value=self.data['current_sort_order'])
        self.var_focus_time = tk.IntVar(value=self.data['custom_timer_settings']['focus_time'])
        self.var_short_break = tk.IntVar(value=self.data['custom_timer_settings']['short_break_time'])
        self.var_long_break = tk.IntVar(value=self.data['custom_timer_settings']['long_break_time'])

        self.setup_ui()
        self.update_clock()
        self.run_timer()

    def play_sound(self, sound_type='notification'):
        try:
            if platform.system() == 'Windows':
                if sound_type == 'notification':
                    winsound.Beep(1000, 300)
                elif sound_type == 'success':
                    winsound.Beep(1200, 150)
                    self.root.after(200, lambda: winsound.Beep(1400, 150))
                elif sound_type == 'warning':
                    winsound.Beep(800, 200)
                    self.root.after(250, lambda: winsound.Beep(600, 200))
            else:
                import os
                os.system('play -nq -t alsa synth 0.3 sine 1000' if sys.platform != 'darwin' else 'afplay /System/Library/Sounds/Glass.aiff')
        except Exception as e:
            print(f"Sound error: {e}")

    def setup_ui(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=view_menu)
        view_menu.add_command(label="Dark Mode", command=lambda: self.change_theme('dark'))
        view_menu.add_command(label="Light Mode", command=lambda: self.change_theme('light'))
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "ZenTask Chronos v1.0"))

        self.main_container = ttk.Frame(self.root, padding=20)
        self.main_container.pack(fill='both', expand=True)

        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill='x', pady=(0, 25))
        
        lbl_title = ttk.Label(header_frame, text="🎯 ZenTask Chronos", style='Header.TLabel')
        lbl_title.pack(side='left')
        
        self.lbl_level = ttk.Label(header_frame, text=f"⭐ Lvl {self.data['level']} • {self.data['xp']} XP", style='Card.TLabel', font=("Segoe UI", 13, "bold"))
        self.lbl_level.pack(side='right', pady=10)

        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True)
        
        self.tab_timer = ttk.Frame(self.notebook, style='Card.TFrame', padding=20)
        self.tab_tasks = ttk.Frame(self.notebook, style='Card.TFrame', padding=20)
        self.tab_stats = ttk.Frame(self.notebook, style='Card.TFrame', padding=20)
        
        self.notebook.add(self.tab_timer, text=' Timer ')
        self.notebook.add(self.tab_tasks, text=' Tasks ')
        self.notebook.add(self.tab_stats, text=' Stats ')

        self.setup_timer_tab()
        self.setup_tasks_tab()
        self.setup_stats_tab()

    def setup_timer_tab(self):
        self.clock_canvas = tk.Canvas(self.tab_timer, width=220, height=220, highlightthickness=0)
        self.clock_canvas.pack(pady=(10, 20))
        self.theme_mgr.apply_to_widget(self.clock_canvas, 'canvas')
        self.register_widget(self.clock_canvas, 'canvas')

        self.lbl_timer = ttk.Label(self.tab_timer, text="25:00", font=("Segoe UI", 64, "bold"), style='Card.TLabel')
        self.lbl_timer.pack(pady=20)

        btn_frame = ttk.Frame(self.tab_timer, style='Card.TFrame')
        btn_frame.pack(pady=25)

        self.btn_start = ttk.Button(btn_frame, text="▶ START FOCUS", command=self.toggle_timer, style='Primary.TButton', width=18)
        self.btn_start.pack(side='left', padx=12)

        btn_reset = ttk.Button(btn_frame, text="↻ RESET", command=self.reset_timer, style='TButton', width=12)
        btn_reset.pack(side='left', padx=12)
        
        mode_frame = ttk.Frame(self.tab_timer, style='Card.TFrame')
        mode_frame.pack(pady=20)
        for m, t in [("⏱ Focus", 25), ("☕ Short Break", 5), ("🌙 Long Break", 15)]:
            ttk.Button(mode_frame, text=m, style='TButton', command=lambda mod=m.split()[0], tim=t: self.set_mode(mod, tim)).pack(side='left', padx=8)

    def setup_tasks_tab(self):
        input_frame = ttk.Frame(self.tab_tasks, style='Card.TFrame')
        input_frame.pack(fill='x', pady=(0, 20))
        
        self.entry_task = ttk.Entry(input_frame, font=("Segoe UI", 12))
        self.entry_task.pack(side='left', fill='x', expand=True, padx=(0, 12))
        self.entry_task.bind('<Return>', lambda e: self.add_task())
        
        btn_add = ttk.Button(input_frame, text="➕ ADD", command=self.add_task, style='Primary.TButton', width=8)
        btn_add.pack(side='right')

        filter_frame = ttk.Frame(self.tab_tasks, style='Card.TFrame')
        filter_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(filter_frame, text="Filter:", style='Card.TLabel', font=("Segoe UI", 11, "bold")).pack(side='left', padx=(0, 8))
        cb_filter = ttk.Combobox(filter_frame, textvariable=self.var_filter, values=['All', 'Completed', 'Pending'], state='readonly', width=12)
        cb_filter.pack(side='left', padx=(0, 20))
        cb_filter.bind('<<ComboboxSelected>>', lambda e: self.render_tasks())
        
        ttk.Label(filter_frame, text="Sort:", style='Card.TLabel', font=("Segoe UI", 11, "bold")).pack(side='left', padx=(0, 8))
        cb_sort = ttk.Combobox(filter_frame, textvariable=self.var_sort, values=['None', 'Priority'], state='readonly', width=12)
        cb_sort.pack(side='left')
        cb_sort.bind('<<ComboboxSelected>>', lambda e: self.render_tasks())

        self.canvas_tasks = tk.Canvas(self.tab_tasks, highlightthickness=0)
        self.scrollbar_tasks = ttk.Scrollbar(self.tab_tasks, orient="vertical", command=self.canvas_tasks.yview)
        self.task_list_frame = ttk.Frame(self.canvas_tasks, style='Card.TFrame')
        
        self.canvas_tasks.create_window((0, 0), window=self.task_list_frame, anchor="nw")
        self.canvas_tasks.configure(yscrollcommand=self.scrollbar_tasks.set)
        
        self.canvas_tasks.pack(side='left', fill='both', expand=True)
        self.scrollbar_tasks.pack(side='right', fill='y')
        
        self.task_list_frame.bind("<Configure>", lambda e: self.canvas_tasks.configure(scrollregion=self.canvas_tasks.bbox("all")))
        self.theme_mgr.apply_to_widget(self.canvas_tasks, 'canvas')
        self.register_widget(self.canvas_tasks, 'canvas')
        
        self.render_tasks()

    def setup_stats_tab(self):
        stats_container = ttk.Frame(self.tab_stats, style='Card.TFrame')
        stats_container.pack(fill='both', expand=True)
        
        def create_card(parent, title, value_var):
            f = tk.Frame(parent, bg=self.theme_mgr.colors['card'], bd=2, relief='raised')
            f.pack(fill='x', pady=15, padx=10, ipadx=15, ipady=15)
            self.register_widget(f, 'card')
            
            tk.Label(f, text=title, font=("Segoe UI", 11, "bold"), fg=self.theme_mgr.colors['text_dim'], bg=self.theme_mgr.colors['card']).pack(anchor='w', pady=(0, 8))
            l = tk.Label(f, textvariable=value_var, font=("Segoe UI", 32, "bold"), fg=self.theme_mgr.colors['primary'], bg=self.theme_mgr.colors['card'])
            l.pack(anchor='w')
            self.register_widget(f.winfo_children()[0], 'card_label_dim')
            self.register_widget(l, 'stat_value')
            return f

        self.var_sessions = tk.StringVar(value=str(self.data['completed_focus_sessions']))
        self.var_time = tk.StringVar(value=f"{self.data['total_focus_time']} m")
        
        create_card(stats_container, "Total Sessions Completed", self.var_sessions)
        create_card(stats_container, "Total Focus Time", self.var_time)

   
    def set_mode(self, mode, minutes):
        self.timer_running = False
        mode_map = {'⏱': 'Focus', '☕': 'Short Break', '🌙': 'Long Break'}
        self.current_mode = mode_map.get(mode, mode)
        self.timer_seconds = minutes * 60
        self.update_timer_display()
        self.btn_start.config(text="START FOCUS")

    def toggle_timer(self):
        self.timer_running = not self.timer_running
        if self.timer_running:
            self.btn_start.config(text="⏸ PAUSE", style='Secondary.TButton')
            self.run_timer()
        else:
            self.btn_start.config(text="▶ RESUME", style='Primary.TButton')

    def run_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            self.root.after(1000, self.run_timer)
            
            if self.current_mode == 'Focus' and self.timer_seconds % 60 == 0:
                self.add_xp(1)
                
        elif self.timer_seconds == 0:
            self.timer_running = False
            self.btn_start.config(text="▶ START FOCUS", style='Primary.TButton')
            self.play_sound('success')
            if self.current_mode == 'Focus':
                self.complete_session()
            else:
                self.play_sound('notification')
                messagebox.showinfo("ZenTask Chronos", "☕ Break Over! Time to focus.")

    def complete_session(self):
        self.data['completed_focus_sessions'] += 1
        self.data['total_focus_time'] += (self.data['custom_timer_settings']['focus_time'])
        self.var_sessions.set(str(self.data['completed_focus_sessions']))
        self.var_time.set(f"{self.data['total_focus_time']} m")
        self.add_xp(50)
        self.play_sound('success')
        self.save()
        messagebox.showinfo("🎉 Session Complete!", "Session Complete! 🎉 +50 XP")

    def add_xp(self, amount):
        self.data['xp'] += amount
        new_level = (self.data['xp'] // 100) + 1
        if new_level > self.data['level']:
            self.data['level'] = new_level
            self.play_sound('success')
            messagebox.showinfo("⭐ Level Up!", f"You reached Level {new_level}! ⭐")
        self.lbl_level.config(text=f"⭐ Lvl {self.data['level']} • {self.data['xp']} XP")
        self.save()

    def add_task(self):
        text = self.entry_task.get().strip()
        if text:
            self.data['tasks'].append({'text': text, 'completed': False, 'priority': 'Medium'})
            self.entry_task.delete(0, 'end')
            self.play_sound('notification')
            self.save()
            self.render_tasks()

    def render_tasks(self):
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
            
        filter_val = self.var_filter.get()
        tasks_to_show = []
        for i, task in enumerate(self.data['tasks']):
            if filter_val == 'All': tasks_to_show.append((i, task))
            elif filter_val == 'Completed' and task['completed']: tasks_to_show.append((i, task))
            elif filter_val == 'Pending' and not task['completed']: tasks_to_show.append((i, task))
            
        if self.var_sort.get() == 'Priority':
            priority_map = {'High': 3, 'Medium': 2, 'Low': 1}
            tasks_to_show.sort(key=lambda x: priority_map.get(x[1].get('priority', 'Medium'), 1), reverse=True)

        for i, task in tasks_to_show:
            f = tk.Frame(self.task_list_frame, bg=self.theme_mgr.colors['card'], pady=8, padx=8)
            f.pack(fill='x', pady=5)
            f.config(relief='raised', bd=1)
            self.register_widget(f, 'card')
            
            status_char = "✓" if task['completed'] else "○"
            btn_check = tk.Button(f, text=status_char, command=lambda idx=i: self.toggle_task(idx), 
                                  font=("Segoe UI", 16, "bold"), borderwidth=0, bg=self.theme_mgr.colors['card'], 
                                  fg=self.theme_mgr.colors['primary'], activebackground=self.theme_mgr.colors['card'],
                                  activeforeground=self.theme_mgr.colors['secondary'], relief='flat', padx=2, pady=2)
            btn_check.pack(side='left', padx=8)
            self.register_widget(btn_check, 'card_btn_primary')

            lbl = tk.Label(f, text=task['text'], font=("Segoe UI", 11), bg=self.theme_mgr.colors['card'], fg=self.theme_mgr.colors['text'], justify='left')
            lbl.pack(side='left', fill='x', expand=True, padx=5)
            self.register_widget(lbl, 'card_label')
            
            if task['completed']:
                lbl.config(fg=self.theme_mgr.colors['text_dim'], font=("Segoe UI", 11, "overstrike"))

            btn_del = tk.Button(f, text="✕", command=lambda idx=i: self.delete_task(idx),
                                font=("Segoe UI", 11, "bold"), borderwidth=0, bg=self.theme_mgr.colors['card'], 
                                fg=self.theme_mgr.colors['danger'], activebackground=self.theme_mgr.colors['card'],
                                activeforeground='#ef4444', relief='flat', padx=4, pady=2)
            btn_del.pack(side='right', padx=5)
            self.register_widget(btn_del, 'card_btn_danger')

    def toggle_task(self, index):
        self.data['tasks'][index]['completed'] = not self.data['tasks'][index]['completed']
        if self.data['tasks'][index]['completed']:
            self.add_xp(10)
        self.save()
        self.render_tasks()
        self.apply_all_themes()

    def delete_task(self, index):
        del self.data['tasks'][index]
        self.save()
        self.render_tasks()

    def update_timer_display(self):
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        self.lbl_timer.config(text=f"{mins:02d}:{secs:02d}")

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 25 * 60
        self.update_timer_display()
        self.btn_start.config(text="START FOCUS", style='Primary.TButton')

    def update_clock(self):
        self.clock_canvas.delete("all")
        c = self.theme_mgr.colors
        w, h = 220, 220
        cx, cy = w/2, h/2
        
        self.clock_canvas.create_oval(10, 10, 210, 210, outline=c['primary'], width=4)
        
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        sec_str = now.strftime("%S")
        self.clock_canvas.create_text(cx, cy-10, text=time_str, fill=c['text'], font=("Segoe UI", 40, "bold"))
        self.clock_canvas.create_text(cx, cy+30, text=sec_str, fill=c['secondary'], font=("Segoe UI", 20))
        
        self.root.after(1000, self.update_clock)

    def change_theme(self, mode):
        self.data['current_theme'] = mode
        self.theme_mgr.switch_theme(mode)
        self.reapply_all_themes()
        self.save()

    def register_widget(self, widget, role):
        self.widgets_to_theme.append((widget, role))

    def reapply_all_themes(self):
        c = self.theme_mgr.colors
        for widget, role in self.widgets_to_theme:
            try:
                if role == 'canvas': widget.configure(bg=c['card'])
                elif role == 'card': widget.configure(bg=c['card'])
                elif role == 'card_label': widget.configure(bg=c['card'], fg=c['text'])
                elif role == 'card_btn_primary': widget.configure(bg=c['card'], fg=c['primary'])
                elif role == 'card_btn_danger': widget.configure(bg=c['card'], fg=c['danger'])
            except: pass
        self.render_tasks()

    def save(self):
        self.data['current_filter'] = self.var_filter.get()
        self.data['current_sort_order'] = self.var_sort.get()
        self.data_mgr.save_data(self.data)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZenTaskChronos(root)
    root.mainloop()