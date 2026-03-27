import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
from gtts import gTTS

def setup_db():
    conn = sqlite3.connect('bank_database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS queues 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, queue_number TEXT, 
        service_type TEXT, counter_number INTEGER, status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

def play_voice(text):
    try:
        tts = gTTS(text=text, lang='th')
        tts.save("kiosk_voice.mp3")
        os.system("afplay kiosk_voice.mp3 &")
    except: pass

class KioskApp:
    def __init__(self, root):
        self.db = setup_db()
        self.root = root
        self.root.title("ตู้กดรับคิวอัตโนมัติ")
        self.root.geometry("500x500")
        self.root.configure(bg="#1a237e")
        
        tk.Label(root, text="ยินดีต้อนรับสู่ธนาคาร", font=("Tahoma", 24, "bold"), fg="white", bg="#1a237e", pady=40).pack()
        tk.Label(root, text="กรุณาเลือกบริการที่ต้องการ", font=("Tahoma", 14), fg="white", bg="#1a237e").pack(pady=10)

        tk.Button(root, text="ฝาก - ถอน - โอน\n(คิว A)", font=("Tahoma", 18, "bold"), bg="#e3f2fd", height=3, width=20,
                  command=lambda: self.add_q("ฝาก-ถอน", "A")).pack(pady=20)
        
        tk.Button(root, text="เปิดบัญชี / บัตรคิว\n(คิว B)", font=("Tahoma", 18, "bold"), bg="#fff9c4", height=3, width=20,
                  command=lambda: self.add_q("เปิดบัญชี", "B")).pack(pady=10)

    def add_q(self, s_type, prefix):
        cursor = self.db.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM queues WHERE service_type = ? AND created_at LIKE ?", (s_type, f"{today}%"))
        num = cursor.fetchone()[0] + 1
        q_num = f"{prefix}{num:03d}"
        cursor.execute("INSERT INTO queues (queue_number, service_type, status) VALUES (?, ?, 'Waiting')", (q_num, s_type))
        self.db.commit()
        play_voice(f"รับบัตรคิวหมายเลข {q_num} ค่ะ")
        messagebox.showinfo("สำเร็จ", f"คิวของคุณคือ: {q_num}\nกรุณารอสักครู่")

if __name__ == "__main__":
    root = tk.Tk()
    KioskApp(root)
    root.mainloop()
    