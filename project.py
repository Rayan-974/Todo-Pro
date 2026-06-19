import customtkinter
import json
import os
import uuid
from datetime import datetime

# Set appearance mode and default color theme
customtkinter.set_default_color_theme("blue")

# Theme colors (Light Lavender ↔️ Dark Grape tuples)
BG_COLOR = ("#F4F0FA", "#130B24")         # Soft lavender background vs Deep Grape background
SIDEBAR_BG = ("#E9D5FF", "#25163F")       # Light vs Dark sidebar background
SIDEBAR_HOVER = ("#D8B4FE", "#3B2163")    # Hover state for sidebar buttons
CARD_BG = ("#FFFFFF", "#311D52")          # White card vs rich violet card
TEXT_PRIMARY = ("#3B0764", "#F3E8FF")      # Deep purple text vs light lavender text
TEXT_SECONDARY = ("#6B21A8", "#C084FC")    # Medium purple vs light purple text
ACCENT_COLOR = ("#8B5CF6", "#A78BFA")      # Purple accent color for buttons/checkboxes
ACCENT_HOVER = ("#7C3AED", "#8B5CF6")      # Hover color for buttons
BORDER_COLOR = ("#DDD6FE", "#4C2F7F")      # Soft lavender vs grape border color

PRIORITY_COLORS = {
    "Urgent": ("#EF4444", "#F87171"),      # Vibrant Red vs Soft Red
    "High": ("#F97316", "#FB923C"),        # Vibrant Orange vs Soft Orange
    "Medium": ("#3B82F6", "#60A5FA"),      # Vibrant Blue vs Soft Blue
    "Normal": ("#DDD6FE", "#4C2F7F")       # Matching border color for normal tasks
}

class AddTaskDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, on_add=None, task_data=None):
        super().__init__(parent)
        self.title("Add New Task" if not task_data else "Edit Task")
        self.geometry("480x750")
        self.configure(fg_color=BG_COLOR)
        self.on_add = on_add
        self.task_data = task_data # If provided, we are editing
        
        # Make modal
        self.transient(parent)
        self.grab_set()

        # Grid config for window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable container inside the dialog
        self.scroll_container = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.subtasks_list = []

        # Title Label & Entry
        self.title_label = customtkinter.CTkLabel(self.scroll_container, text="Task Title", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.title_label.grid(row=0, column=0, padx=20, pady=(10, 2), sticky="w")
        
        self.title_entry = customtkinter.CTkEntry(
            self.scroll_container, placeholder_text="What needs to be done?", font=("Roboto", 14),
            fg_color="white", border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=35
        )
        self.title_entry.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Description Label & Textbox
        self.desc_label = customtkinter.CTkLabel(self.scroll_container, text="Description (optional)", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.desc_label.grid(row=2, column=0, padx=20, pady=(0, 2), sticky="w")
        
        self.desc_textbox = customtkinter.CTkTextbox(
            self.scroll_container, height=100, fg_color="white", border_width=1, border_color=BORDER_COLOR,
            text_color=TEXT_PRIMARY, font=("Roboto", 13)
        )
        self.desc_textbox.grid(row=3, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.desc_textbox.insert("0.0", "Description (optional)...")
        self.desc_textbox.bind("<FocusIn>", self.clear_placeholder)

        # Priority Label & Menu
        self.priority_label = customtkinter.CTkLabel(self.scroll_container, text="Priority", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.priority_label.grid(row=4, column=0, padx=20, pady=(0, 2), sticky="w")
        
        self.priority_var = customtkinter.StringVar(value="Normal")
        self.priority_menu = customtkinter.CTkOptionMenu(
            self.scroll_container, values=["Urgent", "High", "Medium", "Normal"], variable=self.priority_var,
            fg_color=ACCENT_COLOR, button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER,
            text_color="white", font=("Roboto Medium", 13), height=35
        )
        self.priority_menu.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Section Label & ComboBox
        self.section_label = customtkinter.CTkLabel(self.scroll_container, text="Section (Select or type custom)", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.section_label.grid(row=6, column=0, padx=20, pady=(0, 2), sticky="w")
        
        existing_sections = self.get_existing_sections(parent)
        self.section_var = customtkinter.StringVar(value="General")
        self.section_combobox = customtkinter.CTkComboBox(
            self.scroll_container, values=existing_sections, variable=self.section_var,
            fg_color="white", border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER, font=("Roboto", 13),
            dropdown_font=("Roboto", 13), height=35
        )
        self.section_combobox.grid(row=7, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Due Date Label & Entry Frame
        self.due_label = customtkinter.CTkLabel(self.scroll_container, text="Due Date (YYYY-MM-DD HH:MM)", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.due_label.grid(row=8, column=0, padx=20, pady=(0, 2), sticky="w")
        
        self.due_frame = customtkinter.CTkFrame(self.scroll_container, fg_color="transparent")
        self.due_frame.grid(row=9, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.due_frame.grid_columnconfigure(0, weight=1)
        
        self.due_entry = customtkinter.CTkEntry(
            self.due_frame, placeholder_text="e.g., 2026-06-20 18:00", font=("Roboto", 13),
            fg_color="white", border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=35
        )
        self.due_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.presets_frame = customtkinter.CTkFrame(self.due_frame, fg_color="transparent")
        self.presets_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        self.add_preset_btn("Today", lambda: self.set_due_preset(0), 0)
        self.add_preset_btn("Tomorrow", lambda: self.set_due_preset(1), 1)
        self.add_preset_btn("Next Week", lambda: self.set_due_preset(7), 2)

        # Labels Label & Entry
        self.labels_label = customtkinter.CTkLabel(self.scroll_container, text="Labels (comma separated)", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.labels_label.grid(row=10, column=0, padx=20, pady=(0, 2), sticky="w")
        
        self.labels_entry = customtkinter.CTkEntry(
            self.scroll_container, placeholder_text="e.g., waiting, learning", font=("Roboto", 14),
            fg_color="white", border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=35
        )
        self.labels_entry.grid(row=11, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Subtasks Label & Entry + Add
        self.subtasks_label = customtkinter.CTkLabel(self.scroll_container, text="Subtasks Checklist", font=("Roboto Medium", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.subtasks_label.grid(row=12, column=0, padx=20, pady=(0, 2), sticky="w")
        
        self.subtask_input_frame = customtkinter.CTkFrame(self.scroll_container, fg_color="transparent")
        self.subtask_input_frame.grid(row=13, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.subtask_input_frame.grid_columnconfigure(0, weight=1)
        
        self.subtask_entry = customtkinter.CTkEntry(
            self.subtask_input_frame, placeholder_text="Add checklist step...", font=("Roboto", 13),
            fg_color="white", border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=35
        )
        self.subtask_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.subtask_add_btn = customtkinter.CTkButton(
            self.subtask_input_frame, text="+", width=35, height=35,
            fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="white",
            font=("Roboto", 18, "bold"), command=self.add_subtask_to_list
        )
        self.subtask_add_btn.grid(row=0, column=1, sticky="e")
        
        # Subtasks list display
        self.subtasks_display_frame = customtkinter.CTkFrame(self.scroll_container, fg_color="transparent")
        self.subtasks_display_frame.grid(row=14, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.subtasks_display_frame.grid_columnconfigure(0, weight=1)

        # Save Button
        self.add_btn = customtkinter.CTkButton(
            self.scroll_container, text="Save Task", command=self.save_task,
            fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="white",
            font=("Roboto Medium", 14, "bold"), height=40
        )
        self.add_btn.grid(row=15, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Pre-fill if editing
        if self.task_data:
            self.title_entry.insert(0, self.task_data["text"])
            
            desc = self.task_data.get("description", "")
            if desc:
                self.desc_textbox.delete("1.0", "end")
                self.desc_textbox.insert("0.0", desc)
            
            self.priority_var.set(self.task_data.get("priority", "Normal"))
            self.section_var.set(self.task_data.get("section", "General"))
            self.labels_entry.insert(0, ", ".join(self.task_data.get("labels", [])))
            self.due_entry.insert(0, self.task_data.get("due_date", ""))
            self.subtasks_list = list(self.task_data.get("subtasks", []))
            self.render_dialog_subtasks()

    def get_existing_sections(self, parent):
        sections = {"General", "Work", "Personal"}
        if hasattr(parent, "tasks"):
            for t in parent.tasks:
                sect = t.get("section")
                if sect:
                    sections.add(sect.strip().title())
        return sorted(list(sections))

    def clear_placeholder(self, event):
        if self.desc_textbox.get("1.0", "end-1c") == "Description (optional)...":
            self.desc_textbox.delete("1.0", "end")

    def add_preset_btn(self, text, command, col):
        btn = customtkinter.CTkButton(
            self.presets_frame, text=text, command=command,
            fg_color=SIDEBAR_BG, text_color=TEXT_PRIMARY, hover_color=SIDEBAR_HOVER,
            font=("Roboto", 11), height=25, width=80
        )
        btn.grid(row=0, column=col, padx=(0, 5))

    def set_due_preset(self, days):
        from datetime import timedelta
        dt = datetime.now() + timedelta(days=days)
        preset_str = dt.strftime("%Y-%m-%d 18:00")
        self.due_entry.delete(0, "end")
        self.due_entry.insert(0, preset_str)

    def add_subtask_to_list(self):
        text = self.subtask_entry.get().strip()
        if not text:
            return
        self.subtasks_list.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "done": False
        })
        self.subtask_entry.delete(0, "end")
        self.render_dialog_subtasks()

    def delete_subtask_from_list(self, idx):
        self.subtasks_list.pop(idx)
        self.render_dialog_subtasks()

    def render_dialog_subtasks(self):
        for widget in self.subtasks_display_frame.winfo_children():
            widget.destroy()
            
        for i, subtask in enumerate(self.subtasks_list):
            sf = customtkinter.CTkFrame(self.subtasks_display_frame, fg_color=CARD_BG, border_width=1, border_color=BORDER_COLOR)
            sf.grid(row=i, column=0, sticky="ew", pady=2)
            sf.grid_columnconfigure(0, weight=1)
            
            lbl = customtkinter.CTkLabel(sf, text=subtask["text"], font=("Roboto", 12), text_color=TEXT_PRIMARY, anchor="w")
            lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            del_btn = customtkinter.CTkButton(
                sf, text="✕", width=20, height=20, fg_color="transparent",
                text_color="#EF4444", hover_color="#FEE2E2", font=("Roboto", 10),
                command=lambda idx=i: self.delete_subtask_from_list(idx)
            )
            del_btn.grid(row=0, column=1, padx=5, sticky="e")

    def save_task(self):
        title = self.title_entry.get().strip()
        if not title:
            return

        desc = self.desc_textbox.get("1.0", "end-1c").strip()
        if desc == "Description (optional)...":
            desc = ""
        
        # New data
        updated_data = {
            "text": title,
            "description": desc,
            "priority": self.priority_var.get(),
            "section": self.section_var.get().strip().title() or "General",
            "labels": [l.strip() for l in self.labels_entry.get().split(",") if l.strip()],
            "due_date": self.due_entry.get().strip(),
            "subtasks": self.subtasks_list
        }
        
        # If editing, merge with existing (keeping id, done status, timestamp)
        if self.task_data:
            self.task_data.update(updated_data)
            final_data = self.task_data
        else:
            final_data = {
                "id": str(uuid.uuid4()),
                "done": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                **updated_data
            }
        
        if self.on_add:
            self.on_add(final_data)
        self.destroy()

def parse_due_date(due_str):
    if not due_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(due_str, fmt)
        except ValueError:
            pass
    return None

class TaskItem(customtkinter.CTkFrame):
    def __init__(self, master, task_data, on_update=None, on_delete=None, on_edit=None, **kwargs):
        prio = task_data.get("priority", "Normal")
        border_color = PRIORITY_COLORS.get(prio, BORDER_COLOR)
        
        super().__init__(master, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=border_color, **kwargs)
        self.task_data = task_data
        self.on_update = on_update
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.subtasks_expanded = False

        self.grid_columnconfigure(1, weight=1)

        self.checkbox_var = customtkinter.BooleanVar(value=task_data["done"])
        self.checkbox = customtkinter.CTkCheckBox(
            self, text="", variable=self.checkbox_var, command=self.status_changed,
            width=24, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, border_color=ACCENT_COLOR
        )
        self.checkbox.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="n")

        self.content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.content_frame.grid_columnconfigure(0, weight=1)

        title_font = ("Roboto Medium", 14, "overstrike") if task_data["done"] else ("Roboto Medium", 14)
        title_color = "#94A3B8" if task_data["done"] else TEXT_PRIMARY
        self.label = customtkinter.CTkLabel(self.content_frame, text=task_data["text"], anchor="w", text_color=title_color, font=title_font)
        self.label.grid(row=0, column=0, sticky="ew")

        current_row = 1
        if task_data.get("description"):
            self.desc_label = customtkinter.CTkLabel(self.content_frame, text=task_data["description"], anchor="w", text_color=TEXT_SECONDARY, font=("Roboto", 12))
            self.desc_label.grid(row=current_row, column=0, sticky="ew")
            current_row += 1
        
        prio_symbols = {
            "Urgent": "🚨 Urgent",
            "High": "⚡ High",
            "Medium": "🔔 Medium",
            "Normal": "⚪ Normal"
        }
        prio_text = prio_symbols.get(prio, f"⚪ {prio}")
        
        info_parts = [f"📁 {task_data.get('section', 'General')}", prio_text]
        if task_data.get("labels"):
            info_parts.append(f"🏷️ {', '.join(task_data['labels'])}")
        info_text = "  |  ".join(info_parts)
        
        self.info_label = customtkinter.CTkLabel(self.content_frame, text=info_text, anchor="w", text_color=TEXT_SECONDARY, font=("Roboto", 11))
        self.info_label.grid(row=current_row, column=0, sticky="ew")
        current_row += 1

        # Due Date Countdown tag
        due_str = task_data.get("due_date", "")
        due_dt = parse_due_date(due_str)
        if due_dt:
            diff = due_dt - datetime.now()
            if diff.total_seconds() < 0:
                if abs(diff.days) > 0:
                    countdown_text = f"⚠️ Overdue by {abs(diff.days)}d {abs(diff.seconds)//3600}h"
                else:
                    countdown_text = f"⚠️ Overdue by {abs(diff.seconds)//3600}h {abs(diff.seconds)%3600//60}m"
                countdown_color = ("#DC2626", "#F87171")
            elif diff.days == 0:
                countdown_text = f"⏰ Due in {diff.seconds//3600}h {diff.seconds%3600//60}m"
                countdown_color = ("#D97706", "#FBBF24")
            else:
                countdown_text = f"📅 Due in {diff.days}d ({due_dt.strftime('%b %d')})"
                countdown_color = ("#7C3AED", "#A78BFA")
                
            self.due_label = customtkinter.CTkLabel(self.content_frame, text=countdown_text, font=("Roboto Bold", 11), text_color=countdown_color, anchor="w")
            self.due_label.grid(row=current_row, column=0, sticky="ew", pady=(2, 0))
            current_row += 1

        # Subtasks Summary & Expand/Collapse accordion
        self.subtasks = task_data.get("subtasks", [])
        if self.subtasks:
            total_subtasks = len(self.subtasks)
            done_subtasks = sum(1 for s in self.subtasks if s["done"])
            progress_text = f"✓ {done_subtasks}/{total_subtasks} Subtasks"
            
            self.subtasks_summary_frame = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")
            self.subtasks_summary_frame.grid(row=current_row, column=0, sticky="ew", pady=(5, 0))
            self.subtasks_summary_frame.grid_columnconfigure(1, weight=1)
            current_row += 1
            
            self.expand_btn = customtkinter.CTkButton(
                self.subtasks_summary_frame, text="▶ Expand Checklist",
                width=110, height=22, font=("Roboto Medium", 10),
                fg_color=SIDEBAR_BG, text_color=TEXT_PRIMARY, hover_color=SIDEBAR_HOVER,
                command=self.toggle_subtasks
            )
            self.expand_btn.grid(row=0, column=0, padx=(0, 10))
            
            self.progress_lbl = customtkinter.CTkLabel(self.subtasks_summary_frame, text=progress_text, font=("Roboto", 11), text_color=TEXT_SECONDARY)
            self.progress_lbl.grid(row=0, column=1, sticky="w")
            
            self.subtasks_container = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")

        # Buttons Frame
        self.btns_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.btns_frame.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="n")

        # Edit Button
        self.edit_button = customtkinter.CTkButton(
            self.btns_frame, text="✎", width=32, height=32, fg_color="transparent",
            text_color=TEXT_PRIMARY, hover_color=SIDEBAR_HOVER, command=self.edit_task, font=("Arial", 16)
        )
        self.edit_button.pack(side="left", padx=2)

        # Delete Button
        self.delete_button = customtkinter.CTkButton(
            self.btns_frame, text="🗑", width=32, height=32, fg_color="transparent",
            text_color="#EF4444", hover_color="#FEE2E2", command=self.delete_task, font=("Arial", 16)
        )
        self.delete_button.pack(side="left", padx=2)

    def toggle_subtasks(self):
        self.subtasks_expanded = not self.subtasks_expanded
        if self.subtasks_expanded:
            self.expand_btn.configure(text="▼ Collapse Checklist")
            self.subtasks_container.grid(row=10, column=0, sticky="ew", pady=(5, 0), padx=10)
            self.render_subtask_checkboxes()
        else:
            self.expand_btn.configure(text="▶ Expand Checklist")
            self.subtasks_container.grid_remove()

    def render_subtask_checkboxes(self):
        for widget in self.subtasks_container.winfo_children():
            widget.destroy()
            
        for i, sub in enumerate(self.subtasks):
            var = customtkinter.BooleanVar(value=sub["done"])
            cb = customtkinter.CTkCheckBox(
                self.subtasks_container, text=sub["text"], variable=var,
                command=lambda s=sub, v=var: self.subtask_toggled(s, v),
                font=("Roboto", 12), fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, border_color=ACCENT_COLOR,
                height=22
            )
            cb.grid(row=i, column=0, sticky="w", pady=2)

    def subtask_toggled(self, sub, var):
        sub["done"] = var.get()
        total_subtasks = len(self.subtasks)
        done_subtasks = sum(1 for s in self.subtasks if s["done"])
        self.progress_lbl.configure(text=f"✓ {done_subtasks}/{total_subtasks} Subtasks")
        if self.on_update:
            self.on_update(self.task_data)

    def status_changed(self):
        new_status = self.checkbox_var.get()
        self.task_data["done"] = new_status
        if new_status:
             self.label.configure(text_color="#94A3B8", font=("Roboto Medium", 14, "overstrike"))
        else:
             self.label.configure(text_color=TEXT_PRIMARY, font=("Roboto Medium", 14))
        
        if self.on_update:
            self.on_update(self.task_data)

    def delete_task(self):
        if self.on_delete:
            self.on_delete(self.task_data)
            
    def edit_task(self):
        if self.on_edit:
            self.on_edit(self.task_data)

class TodoApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Todo Pro")
        self.geometry("980x750")
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tasks = []
        self.current_filter = "All"
        self.current_section_filter = None

        self.create_sidebar()
        self.create_main_view()
        self.load_tasks()

    def create_sidebar(self):
        self.sidebar = customtkinter.CTkFrame(self, width=220, corner_radius=0, fg_color=SIDEBAR_BG, border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        self.app_title = customtkinter.CTkLabel(self.sidebar, text="✨ Todo Pro", font=("Roboto", 22, "bold"), text_color=TEXT_PRIMARY)
        self.app_title.grid(row=0, column=0, padx=20, pady=(25, 20))

        # Menu Frame to hold dynamic lists and filters
        self.sidebar_menu_frame = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_menu_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        self.sidebar_menu_frame.grid_columnconfigure(0, weight=1)

        # Theme Switch for Light/Dark Mode
        self.theme_switch = customtkinter.CTkSwitch(
            self.sidebar, text="Dark Mode", command=self.toggle_theme,
            fg_color=ACCENT_COLOR, progress_color=ACCENT_COLOR, text_color=TEXT_PRIMARY,
            font=("Roboto Medium", 12)
        )
        self.theme_switch.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="ew")

        # Add New Task Button at the bottom
        self.add_btn_sidebar = customtkinter.CTkButton(
            self.sidebar, text="+ New Task", command=self.open_add_dialog,
            fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="white",
            font=("Roboto Medium", 14, "bold"), height=40
        )
        self.add_btn_sidebar.grid(row=4, column=0, padx=20, pady=(10, 25), sticky="ew")

        self.sidebar_buttons = {}
        self.rebuild_sidebar_menu()

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            customtkinter.set_appearance_mode("Dark")
        else:
            customtkinter.set_appearance_mode("Light")

    def add_sidebar_btn(self, key, text, command, row):
        btn = customtkinter.CTkButton(
            self.sidebar_menu_frame, text=text, fg_color="transparent",
            text_color=TEXT_PRIMARY, hover_color=SIDEBAR_HOVER,
            anchor="w", command=command, font=("Roboto Medium", 13),
            height=32, corner_radius=6
        )
        btn.grid(row=row, column=0, padx=5, pady=2, sticky="ew")
        self.sidebar_buttons[key] = btn

    def rebuild_sidebar_menu(self):
        # Clear existing menu widgets
        for widget in self.sidebar_menu_frame.winfo_children():
            widget.destroy()

        self.sidebar_buttons = {}
        row = 0

        # FILTERS label
        lbl_filters = customtkinter.CTkLabel(self.sidebar_menu_frame, text="FILTERS", font=("Roboto", 11, "bold"), text_color=TEXT_SECONDARY, anchor="w")
        lbl_filters.grid(row=row, column=0, padx=15, pady=(10, 5), sticky="w")
        row += 1

        # All Tasks
        self.add_sidebar_btn("All", "📋 All Tasks", lambda: self.set_filter("All"), row)
        row += 1

        # Important
        self.add_sidebar_btn("Urgent", "🔥 Important", lambda: self.set_filter("Urgent"), row)
        row += 1

        # Dashboard
        self.add_sidebar_btn("Dashboard", "📊 Dashboard", lambda: self.set_filter("Dashboard"), row)
        row += 1

        # SECTIONS label
        lbl_sections = customtkinter.CTkLabel(self.sidebar_menu_frame, text="SECTIONS", font=("Roboto", 11, "bold"), text_color=TEXT_SECONDARY, anchor="w")
        lbl_sections.grid(row=row, column=0, padx=15, pady=(20, 5), sticky="w")
        row += 1

        # Collect and display dynamic sections
        sections = {"General", "Work", "Personal"}
        for t in self.tasks:
            sect = t.get("section")
            if sect:
                sections.add(sect.strip().title())

        for sect in sorted(list(sections)):
            btn_key = f"section_{sect}"
            self.add_sidebar_btn(btn_key, f"📁 {sect}", lambda s=sect: self.set_section(s), row)
            row += 1

        # Restore highlight state
        if self.current_filter == "All":
            self.update_sidebar_selection("All")
        elif self.current_filter == "Urgent":
            self.update_sidebar_selection("Urgent")
        elif self.current_filter == "Dashboard":
            self.update_sidebar_selection("Dashboard")
        elif self.current_filter == "Section" and self.current_section_filter:
            self.update_sidebar_selection(f"section_{self.current_section_filter}")

    def update_sidebar_selection(self, active_key):
        for key, btn in self.sidebar_buttons.items():
            if key == active_key:
                btn.configure(fg_color=ACCENT_COLOR, text_color="white", hover_color=ACCENT_HOVER)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY, hover_color=SIDEBAR_HOVER)

    def create_main_view(self):
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.header_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = customtkinter.CTkLabel(self.header_frame, text="All Tasks", font=("Roboto", 24, "bold"), text_color=TEXT_PRIMARY)
        self.header_label.grid(row=0, column=0, sticky="w")

        # Search and Sorting Frame (aligned under header)
        self.controls_frame = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.controls_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = customtkinter.CTkEntry(
            self.controls_frame, placeholder_text="🔍 Search tasks...", font=("Roboto", 13),
            fg_color=CARD_BG, border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=35
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_ui())

        self.sort_var = customtkinter.StringVar(value="Created Date")
        self.sort_menu = customtkinter.CTkOptionMenu(
            self.controls_frame, values=["Created Date", "Priority", "Due Date", "Alphabetical"],
            variable=self.sort_var, command=lambda v: self.refresh_ui(),
            fg_color=ACCENT_COLOR, button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER,
            text_color="white", font=("Roboto Medium", 13), height=35
        )
        self.sort_menu.grid(row=0, column=1, sticky="e")

        # Container for tasks (Scrollable Frame)
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Container for stats dashboard
        self.dashboard_frame = customtkinter.CTkScrollableFrame(self.main_frame, fg_color="transparent")

    def set_filter(self, filter_name):
        self.current_filter = filter_name
        self.current_section_filter = None
        self.header_label.configure(text=f"{filter_name} Tasks" if filter_name not in ("All", "Dashboard") else f"{filter_name}")
        self.refresh_ui()

    def set_section(self, section_name):
        self.current_filter = "Section"
        self.current_section_filter = section_name
        self.header_label.configure(text=section_name)
        self.refresh_ui()

    def open_add_dialog(self):
        AddTaskDialog(self, on_add=self.add_task)
        
    def open_edit_dialog(self, task_data):
        AddTaskDialog(self, on_add=self.edit_task_callback, task_data=task_data)

    def add_task(self, task_data):
        self.tasks.append(task_data)
        self.save_tasks()
        self.refresh_ui()
        
    def edit_task_callback(self, task_data):
        self.save_tasks()
        self.refresh_ui()

    def update_task_callback(self, task_data):
        self.save_tasks()

    def delete_task_callback(self, task_data):
        self.tasks.remove(task_data)
        self.save_tasks()
        self.refresh_ui()

    def refresh_ui(self):
        self.rebuild_sidebar_menu()
        
        if self.current_filter == "Dashboard":
            self.controls_frame.grid_remove()
            self.scrollable_frame.grid_remove()
            self.dashboard_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
            self.render_dashboard()
            return
            
        self.dashboard_frame.grid_remove()
        self.controls_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        filtered_tasks = []
        search_query = self.search_entry.get().strip().lower()

        for task in self.tasks:
            if self.current_filter == "All":
                pass
            elif self.current_filter == "Urgent" and task.get("priority") != "Urgent":
                continue
            elif self.current_filter == "Section":
                t_sect = task.get("section", "").strip().lower()
                f_sect = self.current_section_filter.strip().lower()
                if t_sect != f_sect:
                    continue

            # Search text match
            if search_query:
                title_match = search_query in task.get("text", "").lower()
                desc_match = search_query in task.get("description", "").lower()
                if not (title_match or desc_match):
                    continue

            filtered_tasks.append(task)
        
        # Sort logic
        sort_by = self.sort_var.get()
        if sort_by == "Alphabetical":
            filtered_tasks.sort(key=lambda x: x["text"].lower())
        elif sort_by == "Priority":
            prio_order = {"Urgent": 0, "High": 1, "Medium": 2, "Normal": 3}
            filtered_tasks.sort(key=lambda x: prio_order.get(x.get("priority", "Normal"), 4))
        elif sort_by == "Due Date":
            def due_sort_key(t):
                d = parse_due_date(t.get("due_date", ""))
                return d.timestamp() if d else float('inf')
            filtered_tasks.sort(key=due_sort_key)
        else: # Created Date
            filtered_tasks.sort(key=lambda x: x.get("timestamp", ""))

        filtered_tasks.sort(key=lambda x: x["done"])

        for i, task_data in enumerate(filtered_tasks):
            item = TaskItem(self.scrollable_frame, task_data, 
                            on_update=self.update_task_callback, 
                            on_delete=self.delete_task_callback,
                            on_edit=self.open_edit_dialog)
            item.grid(row=i, column=0, padx=0, pady=5, sticky="ew")

    def render_dashboard(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=1)

        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["done"])
        active = total - completed
        rate = int((completed / total) * 100) if total > 0 else 0

        # Stats Cards Row
        stats_row = customtkinter.CTkFrame(self.dashboard_frame, fg_color="transparent")
        stats_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Total
        c1 = customtkinter.CTkFrame(stats_row, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=BORDER_COLOR, height=100)
        c1.grid(row=0, column=0, padx=10, sticky="nsew")
        c1.grid_propagate(False)
        customtkinter.CTkLabel(c1, text="Total Tasks", font=("Roboto", 13), text_color=TEXT_SECONDARY).pack(pady=(15, 2))
        customtkinter.CTkLabel(c1, text=str(total), font=("Roboto", 28, "bold"), text_color=TEXT_PRIMARY).pack()

        # Card 2: Completed
        c2 = customtkinter.CTkFrame(stats_row, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=BORDER_COLOR, height=100)
        c2.grid(row=0, column=1, padx=10, sticky="nsew")
        c2.grid_propagate(False)
        customtkinter.CTkLabel(c2, text="Completed", font=("Roboto", 13), text_color=TEXT_SECONDARY).pack(pady=(15, 2))
        customtkinter.CTkLabel(c2, text=str(completed), font=("Roboto", 28, "bold"), text_color=("#10B981", "#34D399")).pack()

        # Card 3: Active
        c3 = customtkinter.CTkFrame(stats_row, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=BORDER_COLOR, height=100)
        c3.grid(row=0, column=2, padx=10, sticky="nsew")
        c3.grid_propagate(False)
        customtkinter.CTkLabel(c3, text="Active Tasks", font=("Roboto", 13), text_color=TEXT_SECONDARY).pack(pady=(15, 2))
        customtkinter.CTkLabel(c3, text=str(active), font=("Roboto", 28, "bold"), text_color=ACCENT_COLOR).pack()

        # Completion Rate Progress Frame
        c_rate = customtkinter.CTkFrame(self.dashboard_frame, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=BORDER_COLOR)
        c_rate.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        customtkinter.CTkLabel(c_rate, text="Completion Rate", font=("Roboto Medium", 16, "bold"), text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w", padx=20, pady=(15, 5))
        customtkinter.CTkLabel(c_rate, text=f"{rate}% of all tasks completed", font=("Roboto", 13), text_color=TEXT_SECONDARY, anchor="w").pack(anchor="w", padx=20, pady=(0, 10))
        
        p_bar = customtkinter.CTkProgressBar(c_rate, fg_color=BG_COLOR, progress_color=ACCENT_COLOR, height=12, corner_radius=6)
        p_bar.set(rate / 100.0)
        p_bar.pack(fill="x", padx=20, pady=(0, 20))

        # Sections Breakdown Progress Frame
        c_sect = customtkinter.CTkFrame(self.dashboard_frame, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=BORDER_COLOR)
        c_sect.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        customtkinter.CTkLabel(c_sect, text="Sections Breakdown", font=("Roboto Medium", 16, "bold"), text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w", padx=20, pady=(15, 10))
        
        sect_stats = {}
        for t in self.tasks:
            s = t.get("section", "General")
            if s not in sect_stats:
                sect_stats[s] = {"total": 0, "done": 0}
            sect_stats[s]["total"] += 1
            if t["done"]:
                sect_stats[s]["done"] += 1
                
        sect_container = customtkinter.CTkFrame(c_sect, fg_color="transparent")
        sect_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        sect_container.grid_columnconfigure(0, weight=1)
        
        if not sect_stats:
            customtkinter.CTkLabel(sect_container, text="No sections recorded.", font=("Roboto", 12), text_color=TEXT_SECONDARY).grid(row=0, column=0, pady=10)
        else:
            for idx, (s_name, s_data) in enumerate(sect_stats.items()):
                s_total = s_data["total"]
                s_done = s_data["done"]
                s_rate = int((s_done / s_total) * 100) if s_total > 0 else 0
                
                f_row = customtkinter.CTkFrame(sect_container, fg_color="transparent")
                f_row.grid(row=idx, column=0, sticky="ew", pady=5)
                f_row.grid_columnconfigure(0, weight=1)
                
                customtkinter.CTkLabel(f_row, text=f"📁 {s_name} ({s_done}/{s_total})", font=("Roboto", 12, "bold"), text_color=TEXT_PRIMARY, anchor="w").grid(row=0, column=0, sticky="w")
                customtkinter.CTkLabel(f_row, text=f"{s_rate}%", font=("Roboto Medium", 12, "bold"), text_color=ACCENT_COLOR, anchor="e").grid(row=0, column=1, sticky="e")
                
                ps_bar = customtkinter.CTkProgressBar(f_row, height=8, fg_color=BG_COLOR, progress_color=ACCENT_COLOR)
                ps_bar.set(s_rate / 100.0)
                ps_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        # Overdue Tasks Alert List Frame
        overdue_list = []
        for t in self.tasks:
            if not t["done"]:
                due = parse_due_date(t.get("due_date", ""))
                if due and due < datetime.now():
                    overdue_list.append(t)
                    
        c_overdue = customtkinter.CTkFrame(self.dashboard_frame, corner_radius=12, fg_color=CARD_BG, border_width=2, border_color=BORDER_COLOR)
        c_overdue.grid(row=2, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        
        customtkinter.CTkLabel(c_overdue, text="⚠️ Overdue Tasks Alert List", font=("Roboto Medium", 16, "bold"), text_color=("#DC2626", "#F87171"), anchor="w").pack(anchor="w", padx=20, pady=(15, 10))
        
        overdue_container = customtkinter.CTkFrame(c_overdue, fg_color="transparent")
        overdue_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        overdue_container.grid_columnconfigure(0, weight=1)
        
        if not overdue_list:
            customtkinter.CTkLabel(overdue_container, text="🎉 Great job! No overdue tasks.", font=("Roboto Medium", 13), text_color=TEXT_SECONDARY).grid(row=0, column=0, pady=10)
        else:
            for idx, task_data in enumerate(overdue_list):
                item_f = customtkinter.CTkFrame(overdue_container, fg_color=BG_COLOR, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
                item_f.grid(row=idx, column=0, sticky="ew", pady=4)
                item_f.grid_columnconfigure(0, weight=1)
                
                due_dt = parse_due_date(task_data["due_date"])
                diff = due_dt - datetime.now()
                if abs(diff.days) > 0:
                    time_overdue = f"{abs(diff.days)}d {abs(diff.seconds)//3600}h"
                else:
                    time_overdue = f"{abs(diff.seconds)//3600}h {abs(diff.seconds)%3600//60}m"
                    
                text_info = f"{task_data['text']}  (Overdue by {time_overdue})"
                customtkinter.CTkLabel(item_f, text=text_info, font=("Roboto Medium", 12), text_color=("#DC2626", "#F87171"), anchor="w").pack(anchor="w", padx=15, pady=8)

    def load_tasks(self):
        if not os.path.exists("tasks.json"):
            return
        try:
            with open("tasks.json", "r") as f:
                data = json.load(f)
                migrated_data = []
                for t in data:
                    if "id" not in t: t["id"] = str(uuid.uuid4())
                    if "description" not in t: t["description"] = ""
                    if "priority" not in t: t["priority"] = "Normal"
                    if "section" not in t: t["section"] = "General"
                    if "labels" not in t: t["labels"] = []
                    if "due_date" not in t: t["due_date"] = ""
                    if "subtasks" not in t: t["subtasks"] = []
                    migrated_data.append(t)
                self.tasks = migrated_data
                self.refresh_ui()
        except Exception as e:
            print(f"Error loading tasks: {e}")

    def save_tasks(self):
        try:
            with open("tasks.json", "w") as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {e}")

if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
