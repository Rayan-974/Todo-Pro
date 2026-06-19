# ✨ Todo Pro

**Todo Pro** is a modern, responsive, and visually stunning desktop Todo application built in Python using **CustomTkinter**. It transitions the desktop experience from standard bland interfaces to a premium workspace themed in **Light Lavender** and **Dark Grape** with advanced productivity dashboard metrics, checklist subtasks, and intelligent scheduling.

---

## 🎨 Key Features

### 🌗 Dynamic Light/Dark Mode (Lavender & Grape)
- Switch instantly between a soft, bright **Light Lavender** theme and a deep, immersive **Dark Grape** theme directly from the sidebar.
- Every interface component, card, and button adapts natively.

### 📊 Performance & Analytics Dashboard
- View active productivity stats under the `📊 Dashboard` tab.
- Includes statistics for:
  - **Task Counts**: Total, Completed, and Active tasks.
  - **Completion Rate**: A dynamic progress bar indicating overall progress.
  - **Sections Breakdown**: Graphical completion rates across different project folders (e.g., General, Work, Personal).
  - **⚠️ Overdue Alert List**: A warning pane listing expired tasks and their delay times.

### 📅 Due Dates & Live Countdown Tags
- Set task due dates easily with quick preset selectors (**Today**, **Tomorrow**, **Next Week**).
- Tasks display visual tags indicating deadline proximity:
  - `⚠️ Overdue by X days / Y hours` (Red)
  - `⏰ Due in X hours / Y minutes` (Orange)
  - `📅 Due in X days` (Purple)

### 📋 Collapsible checklist Subtasks
- Break down tasks into minor checkboxes directly.
- Task cards host collapsible checklists (via a `▶ Expand Checklist` accordion button).
- Tick off sub-steps in-place; the card dynamically updates the task progress (e.g. `✓ 2/3 Subtasks`).

### 🔍 Instant Search & Sorting Controls
- A top search bar lets you filter tasks instantly by title or description as you type.
- Sort tasks dynamically by **Created Date**, **Priority**, **Due Date**, or **Alphabetical** order. Completed tasks automatically sink to the bottom.

---

## 🚀 Installation & Setup

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/TodoList.git
cd TodoList
```

### 2. Install dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Todo app:
```bash
python project.py
```
🙋 Authors
Rayan Ahmer

---

## 🛠️ Technology Stack
- **Language**: Python 3.14+
- **GUI Engine**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern Tkinter styling library)
- **Data Persistence**: JSON Local File System (`tasks.json`)
