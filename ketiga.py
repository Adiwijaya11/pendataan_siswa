import json
import tkinter as tk
from tkinter import ttk, messagebox
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# ------------------ Struktur Data ------------------
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node

    def to_list(self):
        result = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result

    def from_list(self, data_list):
        self.head = None
        for data in data_list:
            self.append(data)

    def sort_by_rata2(self):
        global merge_steps
        merge_steps = []
        data = self.to_list()
        merge_sort_list(data)
        self.from_list(data)

# ------------------ Merge Sort Versi List ------------------
merge_steps = []

def merge_sort_list(arr):
    def merge_sort(arr, l, r):
        if l < r:
            m = (l + r) // 2
            merge_sort(arr, l, m)
            merge_sort(arr, m + 1, r)
            merge(arr, l, m, r)

    def merge(arr, l, m, r):
        n1 = m - l + 1
        n2 = r - m
        L = arr[l:l+n1]
        R = arr[m+1:m+1+n2]
        i = j = 0
        k = l
        while i < n1 and j < n2:
            if L[i]['rata2'] > R[j]['rata2']:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < n1:
            arr[k] = L[i]
            i += 1
            k += 1
        while j < n2:
            arr[k] = R[j]
            j += 1
            k += 1
        merge_steps.append([d.copy() for d in arr])

    merge_sort(arr, 0, len(arr) - 1)

# ------------------ Data Global ------------------
linked_list = LinkedList()
nama_set = set()
MATA_PELAJARAN = ["Matematika", "IPA", "Bahasa Indonesia", "Bahasa Inggris", "Sejarah", "Seni Budaya", "Pendidikan Agama"]
kelas_valid = frozenset([f"{h}{i}" for h in "ABC" for i in range(1, 11)] + [f"D{i}" for i in range(1, 5)])

# ------------------ Fungsi Utility ------------------
def hitung_rata(nilai_dict):
    valid = [v for v in nilai_dict.values() if isinstance(v, (int, float))]
    return round(sum(valid)/len(valid), 2) if valid else 0

def simpan_ke_file(file="data_siswa.json"):
    with open(file, "w") as f:
        json.dump(linked_list.to_list(), f, indent=4)

def muat_dari_file(file="data_siswa.json"):
    if not os.path.exists(file): return
    with open(file) as f:
        try:
            data = json.load(f)
            linked_list.head = None
            nama_set.clear()
            for s in data:
                if "nilai_mapel" not in s:
                    s["nilai_mapel"] = {}
                for m in MATA_PELAJARAN:
                    s["nilai_mapel"].setdefault(m, 0)
                s["rata2"] = s.get("rata2", hitung_rata(s["nilai_mapel"]))
                linked_list.append(s)
                nama_set.add(s["nama"])
        except json.JSONDecodeError:
            messagebox.showerror("Error", "File rusak atau kosong")

# ------------------ GUI ------------------
def tambah_data(entries, win):
    nama = entries["nama"].get().strip()
    kelas = entries["kelas"].get().strip().upper()
    if not nama:
        messagebox.showerror("Error", "Nama tidak boleh kosong", parent=win)
        return
    if nama.lower() in (n.lower() for n in nama_set):
        messagebox.showerror("Error", "Nama sudah ada", parent=win)
        return
    if kelas not in kelas_valid:
        messagebox.showerror("Error", "Kelas tidak valid", parent=win)
        return
    nilai = {}
    for m in MATA_PELAJARAN:
        k = m.lower().replace(" ", "_")
        try:
            v = int(entries[k].get())
            if not (0 <= v <= 100):
                raise ValueError
            nilai[m] = v
        except:
            messagebox.showerror("Error", f"Nilai {m} harus 0-100", parent=win)
            return
    r = hitung_rata(nilai)
    linked_list.append({"nama": nama, "kelas": kelas, "nilai_mapel": nilai, "rata2": r})
    nama_set.add(nama)
    simpan_ke_file()
    update_treeview()
    messagebox.showinfo("Sukses", f"Data {nama} ditambahkan", parent=win)
    win.destroy()

def update_treeview():
    for i in tree.get_children():
        tree.delete(i)
    for i, s in enumerate(linked_list.to_list()):
        nilai_str = ", ".join([f"{k}: {v}" for k, v in s["nilai_mapel"].items()])
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=(s["nama"], s["kelas"], nilai_str, s["rata2"]), tags=(tag,))

def cari_siswa():
    nama = search_entry.get().strip()
    found = [s for s in linked_list.to_list() if nama.lower() in s["nama"].lower()]
    for i in tree.get_children():
        tree.delete(i)
    for s in found:
        nilai_str = ", ".join([f"{k}: {v}" for k, v in s["nilai_mapel"].items()])
        tree.insert("", "end", values=(s["nama"], s["kelas"], nilai_str, s["rata2"]))

def open_add_window():
    win = tk.Toplevel(root)
    win.title("Tambah Siswa")
    frame = ttk.Frame(win)
    frame.pack(padx=10, pady=10)
    fields = [("Nama", "nama"), ("Kelas (A1-D4)", "kelas")]
    for m in MATA_PELAJARAN:
        fields.append((f"Nilai {m}", m.lower().replace(" ", "_")))
    entries = {}
    for i, (lbl, key) in enumerate(fields):
        ttk.Label(frame, text=lbl).grid(row=i, column=0, sticky="w", pady=3)
        e = ttk.Entry(frame)
        e.grid(row=i, column=1)
        entries[key] = e
    ttk.Button(frame, text="Tambah", command=lambda: tambah_data(entries, win)).grid(columnspan=2, pady=10)

# ------------------ ANIMASI SORTING ------------------
def animasi_sorting():
    linked_list.sort_by_rata2()
    fig, ax = plt.subplots(figsize=(10, 5))
    canvas_plot = FigureCanvasTkAgg(fig, master=root)
    canvas_plot.get_tk_widget().pack(pady=10)

    bar_container = ax.bar(range(len(merge_steps[0])), [d["rata2"] for d in merge_steps[0]], color="skyblue")
    ax.set_title("Animasi Merge Sort berdasarkan Rata-rata")
    ax.set_xlabel("Index")
    ax.set_ylabel("Rata-rata Nilai")

    def update(frame):
        data = merge_steps[frame]
        for rect, d in zip(bar_container, data):
            rect.set_height(d["rata2"])
        linked_list.from_list(data)
        update_treeview()

    total_duration_ms = 10000
    interval = max(50, int(total_duration_ms / len(merge_steps)))
    ani = animation.FuncAnimation(fig, update, frames=len(merge_steps), interval=interval, repeat=False)
    canvas_plot.draw()

# ------------------ MAIN GUI ------------------
root = tk.Tk()
root.title("Aplikasi Manajemen Data Siswa")
root.geometry("1024x700")

style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
style.configure("Treeview.Heading", background="#4CAF50", foreground="white", font=("Segoe UI", 10, "bold"))
style.map("Treeview", background=[("selected", "#90ee90")])

style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#4CAF50", foreground="white", padding=6)
style.map("TButton", background=[("active", "#45a049")])

ttk.Label(root, text="Aplikasi Manajemen Data Siswa", font=("Segoe UI", 20, "bold")).pack(pady=15)

control = ttk.Frame(root)
control.pack(pady=5)
ttk.Button(control, text="➕ Tambah Data Siswa", command=open_add_window).pack(side="left", padx=5)
ttk.Button(control, text="📊 Urutkan Data + Animasi", command=animasi_sorting).pack(side="left", padx=5)
ttk.Button(control, text="🔄 Refresh Data", command=update_treeview).pack(side="left", padx=5)

search_frame = ttk.Frame(root)
search_frame.pack(pady=5)
ttk.Label(search_frame, text="Cari Nama:").pack(side="left")
search_entry = ttk.Entry(search_frame)
search_entry.pack(side="left", padx=5)
ttk.Button(search_frame, text="🔍 Cari", command=cari_siswa).pack(side="left")
ttk.Button(search_frame, text="Tampilkan Semua", command=update_treeview).pack(side="left", padx=5)

columns = ("nama", "kelas", "nilai_mapel", "rata2")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col.replace("_", " ").title())
    tree.column(col, width=200 if col == "nilai_mapel" else 100)
tree.pack(fill="both", expand=True, padx=10, pady=10)

tree.tag_configure('oddrow', background='white')
tree.tag_configure('evenrow', background='#f2f2f2')

muat_dari_file()
update_treeview()
root.mainloop()
