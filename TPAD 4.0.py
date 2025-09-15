from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, simpledialog, Menu, messagebox
from tkinter import ttk
from PIL import Image, ImageTk

def create_terminal_notepad():
    root = TkinterDnD.Tk()
    root.title("TerminalPad")
    root.geometry("800x600")

    # Theme colors
    bg_color = "#000000"
    fg_color = "#00FF00"
    menu_bg = "#333333"
    menu_fg = "#FFFFFF"

    # Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    editors = []

    def add_new_tab(content=""):
        tab_frame = tk.Frame(notebook, bg=bg_color)

        # Line Numbers
        line_numbers = tk.Text(
            tab_frame,
            width=4,
            bg=bg_color,
            fg=fg_color,
            font=("Courier New", 12),
            padx=5,
            pady=5,
            takefocus=0,
            border=0,
            state="disabled"
        )
        line_numbers.pack(side="left", fill="y")

        # Text Area
        text_area = tk.Text(
            tab_frame,
            bg=bg_color,
            fg=fg_color,
            insertbackground=fg_color,
            font=("Courier New", 12),
            undo=True,
            wrap="word"
        )
        text_area.pack(side="right", expand=True, fill="both")
        text_area.insert("1.0", content)
        text_area.image_references = {}

        # Line number update
        def update_line_numbers_local(event=None):
            line_numbers.config(state="normal")
            line_numbers.delete("1.0", tk.END)
            num_lines = int(text_area.index("end-1c").split('.')[0])
            for i in range(1, num_lines + 1):
                line_numbers.insert(tk.END, f"{i} >\n")
            line_numbers.config(state="disabled")

        text_area.bind("<KeyRelease>", update_line_numbers_local)
        text_area.bind("<MouseWheel>", lambda e: line_numbers.yview_moveto(text_area.yview()[0]))
        text_area.bind("<Button-4>", lambda e: line_numbers.yview_moveto(text_area.yview()[0]))
        text_area.bind("<Button-5>", lambda e: line_numbers.yview_moveto(text_area.yview()[0]))

        # Drag-and-Drop Handler
        def drop(event):
            file_path = event.data.strip().strip('{}')  # Handle paths with spaces
            if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                try:
                    image = Image.open(file_path)
                    image.thumbnail((200, 200))
                    tk_image = ImageTk.PhotoImage(image)
                    img_name = f"img_{len(text_area.image_references)}"
                    text_area.image_references[img_name] = tk_image
                    text_area.image_create(tk.INSERT, image=tk_image)
                    text_area.insert(tk.INSERT, "\n")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to insert image: {e}")
            else:
                messagebox.showwarning("Unsupported File", "Only image files can be dropped.")

        text_area.drop_target_register(DND_FILES)
        text_area.dnd_bind("<<Drop>>", drop)

        update_line_numbers_local()

        editors.append({
            "frame": tab_frame,
            "text_area": text_area,
            "line_numbers": line_numbers
        })

        tab_index = notebook.index("end") - 1
        notebook.insert(tab_index, tab_frame, text=f"Tab {tab_index + 1}")
        notebook.select(tab_index)

    def close_tab_by_index(index):
        notebook.forget(index)
        del editors[index]

    def on_tab_changed(event):
        if notebook.index("current") == notebook.index("end") - 1:
            add_new_tab()

    def show_tab_menu(event):
        x, y = event.x, event.y
        element = notebook.identify(x, y)
        if "label" in element:
            index = notebook.index(f"@{x},{y}")
            if index < notebook.index("end") - 1:
                menu = Menu(root, tearoff=0, bg=menu_bg, fg=menu_fg)
                menu.add_command(label="Close Tab", command=lambda: close_tab_by_index(index))
                menu.post(event.x_root, event.y_root)

    notebook.bind("<Button-3>", show_tab_menu)
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    # "+" tab
    plus_tab = tk.Frame(notebook)
    notebook.add(plus_tab, text="+")

    # --- Menus ---
    menu_bar = Menu(root, bg=menu_bg, fg=menu_fg)

    def get_active_text_area():
        index = notebook.index("current")
        if index >= len(editors):
            return None
        return editors[index]["text_area"]

    def open_file():
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "r") as file:
            content = file.read()
        add_new_tab(content)

    def save_file():
        text_area = get_active_text_area()
        if text_area is None:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            content = text_area.get(1.0, tk.END)
            with open(filepath, "w") as file:
                file.write(content)

    def find_text():
        text_area = get_active_text_area()
        if text_area is None:
            return
        find_string = simpledialog.askstring("Find", "Enter text to find:")
        if find_string:
            start_pos = "1.0"
            text_area.tag_remove("found", "1.0", tk.END)
            while True:
                pos = text_area.search(find_string, start_pos, stopindex=tk.END)
                if not pos:
                    break
                end_pos = f"{pos}+{len(find_string)}c"
                text_area.tag_add("found", pos, end_pos)
                start_pos = end_pos
            text_area.tag_config("found", background="#FFFF00", foreground="#000000")

    def replace_text():
        text_area = get_active_text_area()
        if text_area is None:
            return
        find_string = simpledialog.askstring("Replace", "Enter text to find:")
        if find_string:
            replace_string = simpledialog.askstring("Replace", "Enter replacement text:")
            if replace_string is not None:
                content = text_area.get(1.0, tk.END)
                new_content = content.replace(find_string, replace_string)
                text_area.delete(1.0, tk.END)
                text_area.insert(1.0, new_content)

    def select_all(event=None):
        text_area = get_active_text_area()
        if text_area:
            text_area.tag_add("sel", "1.0", "end")
            return "break"

    def quick_copy():
        text_area = get_active_text_area()
        if text_area:
            try:
                selected_text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                root.clipboard_clear()
                root.clipboard_append(selected_text)
            except tk.TclError:
                pass

    def insert_image():
        text_area = get_active_text_area()
        if text_area is None:
            return
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        try:
            image = Image.open(filepath)
            image.thumbnail((200, 200))
            tk_image = ImageTk.PhotoImage(image)
            img_name = f"img_{len(text_area.image_references)}"
            text_area.image_references[img_name] = tk_image
            text_area.image_create(tk.INSERT, image=tk_image)
            text_area.insert(tk.INSERT, "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert image: {e}")

    # File Menu
    file_menu = Menu(menu_bar, tearoff=0, bg=menu_bg, fg=menu_fg)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Edit Menu
    edit_menu = Menu(menu_bar, tearoff=0, bg=menu_bg, fg=menu_fg)
    edit_menu.add_command(label="Undo", command=lambda: get_active_text_area().edit_undo())
    edit_menu.add_command(label="Redo", command=lambda: get_active_text_area().edit_redo())
    edit_menu.add_separator()
    edit_menu.add_command(label="Find", command=find_text)
    edit_menu.add_command(label="Replace All", command=replace_text)
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=select_all)
    edit_menu.add_command(label="Copy", command=quick_copy)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # Media Menu
    media_menu = Menu(menu_bar, tearoff=0, bg=menu_bg, fg=menu_fg)
    media_menu.add_command(label="Insert Image", command=insert_image)
    menu_bar.add_cascade(label="Media", menu=media_menu)

    root.config(menu=menu_bar)

    # Keyboard Shortcuts
    root.bind("<Control-s>", lambda event: save_file())
    root.bind("<Control-o>", lambda event: open_file())
    root.bind("<Control-f>", lambda event: find_text())
    root.bind("<Control-a>", select_all)

    # Start with one tab
    add_new_tab()

    root.mainloop()

if __name__ == "__main__":
    create_terminal_notepad()