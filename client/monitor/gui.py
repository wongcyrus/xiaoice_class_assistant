from typing import Dict


def run_preview(controller):
    try:
        import tkinter as tk
        from PIL import ImageTk
    except ImportError as e:
        print("Preview mode requires Tkinter support (ImageTk).", e)
        print("Falling back to headless mode.")
        return controller.run_headless()

    root = tk.Tk()
    root.title("Window Monitor Preview")

    running: Dict[str, bool] = {"val": True, "selecting": False}

    controls = tk.Frame(root)
    controls.pack(padx=10, pady=(10, 0), fill="x")

    def on_change_monitor_btn():
        running["selecting"] = True
        try:
            controller.capture.ensure_monitor_selected(gui=True, parent=root)
        finally:
            running["selecting"] = False

    tk.Button(controls, text="Change Monitor", command=on_change_monitor_btn).pack(
        side="left"
    )

    img_label = tk.Label(root)
    img_label.pack(padx=10, pady=10)

    text_var = tk.StringVar(value="OCR text will appear here…")
    tk.Label(root, textvariable=text_var, wraplength=800, justify="left").pack(
        padx=10, pady=(0, 10)
    )

    status_var = tk.StringVar(value=controller.ocr.status_message or "")
    tk.Label(root, textvariable=status_var, fg="gray").pack(padx=10, pady=(0, 10))

    photo_ref: Dict[str, object] = {"img": None}

    def on_close():
        running["val"] = False
        try:
            root.destroy()
        except tk.TclError:
            pass

    root.protocol("WM_DELETE_WINDOW", on_close)

    controller.capture.ensure_monitor_selected(gui=True, parent=root)

    def update_loop():
        try:
            if not running["val"] or running.get("selecting") or not root.winfo_exists():
                return
            screenshot, text, _ = controller.process_once()
            disp = screenshot.resize(
                (int(screenshot.width * 0.5), int(screenshot.height * 0.5))
            )
            photo = ImageTk.PhotoImage(disp, master=root)
            photo_ref["img"] = photo
            try:
                img_label.configure(image=photo)
            except tk.TclError:
                return
            text_var.set(text if text else "<no text detected>")
            status_var.set(controller.ocr.status_message)
        except Exception as e:
            text_var.set(f"Error: {e}")
        finally:
            if running["val"] and root.winfo_exists():
                root.after(int(controller.interval * 1000), update_loop)

    update_loop()
    print("Preview window open. Close it to stop.")
    root.mainloop()
