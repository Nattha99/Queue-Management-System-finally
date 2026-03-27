import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
from gtts import gTTS

def play_voice(text):
    try:
        tts = gTTS(text=text, lang='th')
        tts.save("staff_voice.mp3")
        os.system("afplay staff_voice.mp3 &")
    except: pass

class StaffApp:
    def __init__(self, root):
        self.db = sqlite3.connect('bank_database.db')
        self.root = root
        self.root.title("ระบบจัดการคิวพนักงาน")
        self.root.geometry("450x600")
        self.current_id = None
        
        tk.Label(root, text="แผงควบคุมพนักงาน", font=("Tahoma", 18, "bold"), pady=20).pack()

        # เลือกช่องบริการ
        frame_top = tk.Frame(root)
        frame_top.pack(pady=10)
        tk.Label(frame_top, text="ช่องบริการเลขที่: ").pack(side="left")
        self.counter_num = ttk.Combobox(frame_top, values=[1,2,3,4,5], width=5, state="readonly")
        self.counter_num.current(0)
        self.counter_num.pack(side="left")

        # แสดงสถานะ
        self.lbl_q = tk.Label(root, text="รอการเรียกคิว...", font=("Tahoma", 20, "bold"), fg="blue", pady=30)
        self.lbl_q.pack()

        tk.Button(root, text="🔊 เรียกคิวถัดไป", font=("Tahoma", 14, "bold"), bg="#4caf50", height=2, width=25, command=self.next_q).pack(pady=10)
        tk.Button(root, text="✅ เสร็จสิ้นธุรกรรม", font=("Tahoma", 12), bg="#cfd8dc", width=25, command=self.done_q).pack(pady=5)
        tk.Button(root, text="📊 สรุปรายงานวันนี้", command=self.report).pack(pady=30)

    def next_q(self):
        if self.current_id:
            messagebox.showwarning("เตือน", "กรุณาปิดคิวเก่าก่อนค่ะ")
            return
        cursor = self.db.cursor()
        cursor.execute("SELECT id, queue_number FROM queues WHERE status = 'Waiting' ORDER BY id ASC LIMIT 1")
        res = cursor.fetchone()
        if res:
            self.current_id, q_num = res
            cnt = self.counter_num.get()
            cursor.execute("UPDATE queues SET status = 'Calling', counter_number = ? WHERE id = ?", (cnt, self.current_id))
            self.db.commit()
            self.lbl_q.config(text=f"กำลังเรียก: {q_num}")
            play_voice(f"ขอเชิญหมายเลข {' '.join(list(q_num))} ที่ช่องบริการหมายเลข {cnt} ค่ะ")
        else:
            messagebox.showinfo("แจ้งเตือน", "ไม่มีคิวรอ")

    def done_q(self):
        if self.current_id:
            cursor = self.db.cursor()
            cursor.execute("UPDATE queues SET status = 'Finished' WHERE id = ?", (self.current_id,))
            self.db.commit()
            self.current_id = None
            self.lbl_q.config(text="รอการเรียกคิว...")
        else:
            messagebox.showerror("ผิดพลาด", "ไม่มีคิวที่กำลังบริการ")

    def report(self):
        cursor = self.db.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT service_type, COUNT(*) FROM queues WHERE created_at LIKE ? GROUP BY service_type", (f"{today}%",))
        data = cursor.fetchall()
        msg = f"รายงานวันที่ {today}\n" + "\n".join([f"{d[0]}: {d[1]} คน" for d in data])
        messagebox.showinfo("สรุปยอด", msg if data else "ไม่มีข้อมูล")

if __name__ == "__main__":
    root = tk.Tk()
    StaffApp(root)
    root.mainloop()
    