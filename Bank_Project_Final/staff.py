import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
from gtts import gTTS

# --- [STEP 1] วางฟังก์ชัน Quick Sort ไว้ตรงนี้ (บรรทัดบนสุดหลัง import) ---
def quick_sort(arr):
    """ Algorithm: Quick Sort สำหรับเรียงลำดับข้อมูลคิว """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# ฟังก์ชันเสียง (เหมือนเดิม)
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
        self.root.title("ระบบจัดการคิวพนักงาน (Algorithm Mode)")
        self.root.geometry("450x650")
        self.current_id = None
        
        self.ui_setup()

    def ui_setup(self):
        tk.Label(self.root, text="แผงควบคุมพนักงาน", font=("Tahoma", 18, "bold"), pady=20).pack()

        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)
        tk.Label(frame_top, text="ช่องบริการเลขที่: ").pack(side="left")
        self.counter_num = ttk.Combobox(frame_top, values=[1,2,3,4,5], width=5, state="readonly")
        self.counter_num.current(0)
        self.counter_num.pack(side="left")

        self.lbl_q = tk.Label(self.root, text="รอการเรียกคิว...", font=("Tahoma", 20, "bold"), fg="blue", pady=30)
        self.lbl_q.pack()

        tk.Button(self.root, text="🔊 เรียกคิวถัดไป", font=("Tahoma", 14, "bold"), bg="#4caf50", height=2, width=25, command=self.next_q).pack(pady=10)
        tk.Button(self.root, text="✅ เสร็จสิ้นธุรกรรม", font=("Tahoma", 12), bg="#cfd8dc", width=25, command=self.done_q).pack(pady=5)
        
        # ปุ่มรายงานที่จะใช้ Algorithm
        tk.Button(self.root, text="📊 สรุปรายงาน (Quick Sort)", command=self.report, bg="#90caf9").pack(pady=30)

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

    # --- [STEP 2] ฟังก์ชัน Report ที่ดึง Algorithm มาใช้งานจริง ---
    def report(self):
        cursor = self.db.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # ดึงข้อมูลเลขคิวทั้งหมดของวันนี้มา (ไม่เรียงลำดับจาก SQL เพื่อมาเรียงเอง)
        cursor.execute("SELECT queue_number FROM queues WHERE created_at LIKE ?", (f"{today}%",))
        rows = cursor.fetchall()
        
        if not rows:
            messagebox.showinfo("สรุปยอด", "วันนี้ยังไม่มีข้อมูล")
            return

        # 1. แปลงข้อมูลจาก Database เป็น List ปกติ
        raw_list = [r[0] for r in rows]
        
        # 2. เรียกใช้ Quick Sort Algorithm ที่เราเขียนขึ้นเอง
        sorted_list = quick_sort(raw_list)
        
        # 3. แสดงผล
        msg = f"รายงานสรุปวันที่ {today}\n"
        msg += f"จำนวนลูกค้า: {len(sorted_list)} ท่าน\n"
        msg += "--------------------------\n"
        msg += "ลำดับคิว (เรียงด้วย Quick Sort):\n" + ", ".join(sorted_list)
        
        messagebox.showinfo("Daily Report (Algorithm Optimized)", msg)

if __name__ == "__main__":
    root = tk.Tk()
    StaffApp(root)
    root.mainloop()
    