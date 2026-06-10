import tkinter as tk
from tkinter import ttk, messagebox
from API import ambil_api

from Perhitungan_DBR import hitung_rac_dbr, mengambilDataAngsuran

# ─────────────────────────────────────────────
#  KONSTANTA DATA
# ─────────────────────────────────────────────
CUSTOMER_CATEGORIES = {
    "LIVIN": [
        "LIVINREGCORPORATE1",
        "LIVINEKOSISTEMCORP2",
        "LIVINEKOSISTEMCORP3",
        "LIVINREGPEMANDIRIAN1",
        "LIVINREGPEMANDIRIAN2",
        "LIVINREGMANDIRIAN3",
        "LIVINREGPRIO",
        "LIVINREGPRIVATE",
        "LAINNYA",
    ],
    "BSI": [
        "NASABAH PRIORITAS",
        "NASABAH PRIVATE",
        "NASABAH PAYROLL BSI",
        "LAINNYA",
    ],
}

# ─────────────────────────────────────────────
#  WARNA & FONT
# ─────────────────────────────────────────────
COLOR_BG          = "#F0F4F8"       # latar utama
COLOR_CARD        = "#FFFFFF"       # kartu/frame
COLOR_PRIMARY     = "#003D82"       # biru Mandiri gelap
COLOR_ACCENT      = "#F5A623"       # kuning/emas aksen
COLOR_HEADER_BG   = "#003D82"
COLOR_HEADER_FG   = "#FFFFFF"
COLOR_LABEL       = "#3A3A5C"
COLOR_SUBLABEL    = "#8A8AAA"
COLOR_ENTRY_BG    = "#F7F9FC"
COLOR_ENTRY_FG    = "#1A1A2E"
COLOR_BORDER      = "#D0D8E8"
COLOR_BTN_CALC    = "#003D82"
COLOR_BTN_RESET   = "#E53E3E"
COLOR_BTN_FG      = "#FFFFFF"
COLOR_RESULT_BG   = "#EBF4FF"
COLOR_RESULT_FG   = "#003D82"
COLOR_DISABLED    = "#C8CFD8"

FONT_TITLE   = ("Georgia", 18, "bold")
FONT_HEADING = ("Helvetica", 11, "bold")
FONT_LABEL   = ("Helvetica", 10)
FONT_ENTRY   = ("Courier New", 10)
FONT_RESULT  = ("Helvetica", 12, "bold")
FONT_SMALL   = ("Helvetica", 8)


# ─────────────────────────────────────────────
#  HELPER FORMATTING
# ─────────────────────────────────────────────
def format_rupiah(value: int) -> str:
    """Format integer ke string Rp x.xxx.xxx"""
    return f"Rp {value:,.0f}".replace(",", ".")


def safe_int(text: str) -> int:
    """Konversi string angka ke int, kembalikan 0 jika kosong/gagal."""
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else 0




# ─────────────────────────────────────────────
#  APLIKASI UTAMA
# ─────────────────────────────────────────────
class RacDbrApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root()
        self._apply_styles()
        self._build_ui()

    # ── Konfigurasi Window ──────────────────
    def _configure_root(self):
        self.root.title("Simulasi RAC DBR — BSI dan LIVIN")
        self.root.geometry("620x800")
        self.root.resizable(True, True)
        self.root.configure(bg=COLOR_BG)

    # ── Custom ttk Styles ──────────────────
    def _apply_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "Custom.TCombobox",
            fieldbackground=COLOR_ENTRY_BG,
            background=COLOR_ENTRY_BG,
            foreground=COLOR_ENTRY_FG,
            bordercolor=COLOR_BORDER,
            arrowcolor=COLOR_PRIMARY,
            padding=5,
            font=FONT_ENTRY,
        )
        style.map(
            "Custom.TCombobox",
            fieldbackground=[("readonly", COLOR_ENTRY_BG)],
            foreground=[("readonly", COLOR_ENTRY_FG)],
        )

    # ── Bangun Seluruh UI ──────────────────
    def _build_ui(self):
        self._build_header()

        # Scrollable canvas agar muat di layar kecil
        canvas = tk.Canvas(self.root, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(canvas, bg=COLOR_BG)
        window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window_id, width=canvas.winfo_width())

        self.scroll_frame.bind("<Configure>", _on_configure)
        canvas.bind(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

        self._build_form(self.scroll_frame)
        self._build_buttons(self.scroll_frame)
        self._build_result_panel(self.scroll_frame)

    # ── Header ────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLOR_HEADER_BG, pady=0)
        header.pack(fill="x")

        # Stripe aksen kuning
        stripe = tk.Frame(header, bg=COLOR_ACCENT, height=5)
        stripe.pack(fill="x")

        inner = tk.Frame(header, bg=COLOR_HEADER_BG, padx=24, pady=16)
        inner.pack(fill="x")

        tk.Label(
            inner,
            text="⬛ APLIKASI SUPPORT",
            font=("Helvetica", 9, "bold"),
            bg=COLOR_HEADER_BG,
            fg=COLOR_ACCENT,
        ).pack(anchor="w")

        tk.Label(
            inner,
            text="Simulasi Perhitungan RAC DBR",
            font=FONT_TITLE,
            bg=COLOR_HEADER_BG,
            fg=COLOR_HEADER_FG,
        ).pack(anchor="w")

        tk.Label(
            inner,
            text="Repayment Ability Check  ·  Debt Burden Ratio",
            font=FONT_SMALL,
            bg=COLOR_HEADER_BG,
            fg="#7EB5FF",
        ).pack(anchor="w")

    # ── Card Helper ───────────────────────
    def _make_card(self, parent, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg=COLOR_BG, padx=16, pady=8)
        outer.pack(fill="x", padx=16, pady=6)

        # Judul section
        tk.Label(
            outer,
            text=title.upper(),
            font=("Helvetica", 8, "bold"),
            bg=COLOR_BG,
            fg=COLOR_SUBLABEL,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        card = tk.Frame(
            outer,
            bg=COLOR_CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            padx=20,
            pady=14,
        )
        card.pack(fill="x")
        return card

    # ── Row Helper ────────────────────────
    def _make_row(self, parent, row: int, label_text: str):
        tk.Label(
            parent,
            text=label_text,
            font=FONT_LABEL,
            bg=COLOR_CARD,
            fg=COLOR_LABEL,
            anchor="w",
            width=28,
        ).grid(row=row, column=0, padx=(0, 12), pady=6, sticky="w")

    def _make_entry(self, parent, row: int, var: tk.StringVar) -> tk.Entry:
        # Validasi hanya angka
        vcmd = (self.root.register(self._only_digits), "%P")

        entry = tk.Entry(
            parent,
            textvariable=var,
            validate="key",
            validatecommand=vcmd,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
            fg=COLOR_ENTRY_FG,
            insertbackground=COLOR_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_PRIMARY,
            width=24,
        )
        entry.grid(row=row, column=1, padx=0, pady=6, sticky="ew")
        return entry

    # ── Form ──────────────────────────────
    def _build_form(self, parent):
        # StringVars
        self.var_kategori          = tk.StringVar(value="LIVIN")
        self.var_cust_category     = tk.StringVar()
        self.var_punya_pasangan    = tk.StringVar(value="TIDAK")
        self.var_angsuran_lain_deb = tk.StringVar()
        self.var_angsuran_lain_pas = tk.StringVar()
        self.var_angsuran_diajukan = tk.StringVar()
        self.var_angsuran_muf      = tk.StringVar()
        self.var_pendapatan_deb    = tk.StringVar()
        self.var_pendapatan_range  = tk.StringVar()
        self.var_pendapatan_pas     = tk.StringVar()
        self.var_fieldKTP           = tk.StringVar()
        self.var_fieldKTP_pasangan  = tk.StringVar()
        self.var_no_order           = tk.StringVar()



        # ── Kartu 1: Profil Nasabah ──────
        card1 = self._make_card(parent, "Profil Nasabah")
        card1.columnconfigure(1, weight=1)

        self._make_row(card1, 0, "Platform")
        self.combo_platform = ttk.Combobox(
            card1,
            textvariable=self.var_kategori,
            values=list(CUSTOMER_CATEGORIES.keys()),
            state="readonly",
            style="Custom.TCombobox",
            width=22,
        )
        self.combo_platform.grid(row=0, column=1, pady=6, sticky="ew")
        self.combo_platform.bind("<<ComboboxSelected>>", self._on_platform_selected)

        self._make_row(card1, 1, "Customer Category")
        self.combo_category = ttk.Combobox(
            card1,
            textvariable=self.var_cust_category,
            state="readonly",
            style="Custom.TCombobox",
            width=22,
        )
        self.combo_category.grid(row=1, column=1, pady=6, sticky="ew")
        self._refresh_categories()

        self._make_row(card1, 2, "Status Pernikahan")
        self.combo_pasangan = ttk.Combobox(
            card1,
            textvariable=self.var_punya_pasangan,
            values=["YA", "TIDAK"],
            state="readonly",
            style="Custom.TCombobox",
            width=22,
        )
        self.combo_pasangan.grid(row=2, column=1, pady=6, sticky="ew")
        self.combo_pasangan.bind("<<ComboboxSelected>>", self._on_pasangan_changed)

        self._make_row(card1, 3, "No order")
        # vcmd_noOrder = (self.root.register(self._validate_ktp), "%P")
        self.fieldNoOrder = tk.Entry(
            card1,
            textvariable=self.var_no_order,
            validate="key",
            # validatecommand=vcmd_noOrder,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
            fg=COLOR_ENTRY_FG,
            insertbackground=COLOR_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_PRIMARY,
            width=24,
        )
        self.fieldNoOrder.grid(row=3, column=1, padx=0, pady=6, sticky="ew")
        

        self._make_row(card1, 4, "NIK KTP Debitur")
        vcmd_ktp = (self.root.register(self._validate_ktp), "%P")
        self.fieldKTP = tk.Entry(
            card1,
            textvariable=self.var_fieldKTP,
            validate="key",
            validatecommand=vcmd_ktp,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
            fg=COLOR_ENTRY_FG,
            insertbackground=COLOR_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_PRIMARY,
            width=24,
        )
        self.fieldKTP.grid(row=4, column=1, padx=0, pady=6, sticky="ew")

        self._make_row(card1, 5, "NIK KTP Pasangan")
        self.fieldKTP_pasangan = tk.Entry(
            card1,
            textvariable=self.var_fieldKTP_pasangan,
            validate="key",
            validatecommand=vcmd_ktp,
            font=FONT_ENTRY,
            bg=COLOR_ENTRY_BG,
            fg=COLOR_ENTRY_FG,
            insertbackground=COLOR_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_PRIMARY,
            width=24,
        )
        self.fieldKTP_pasangan.grid(row=5, column=1, padx=0, pady=6, sticky="ew")

        # Tombol Cek Angsuran
        btn_cek_angsuran = tk.Button(
            card1,
            text="🔍  Cek Angsuran",
            font=("Helvetica", 10, "bold"),
            bg="#005BAA",
            fg=COLOR_BTN_FG,
            activebackground="#003D82",
            activeforeground=COLOR_BTN_FG,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self._cek_angsuran,
        )
        btn_cek_angsuran.grid(row=6, column=0, columnspan=2, pady=(8, 4), sticky="ew")


        # ── Kartu 2: Data Angsuran ───────
        card2 = self._make_card(parent, "Data Angsuran")
        card2.columnconfigure(1, weight=1)

        fields_angsuran = [
            ("Angsuran Lain Debitur (Rp)", self.var_angsuran_lain_deb),
            ("Angsuran Lain Pasangan (Rp)", self.var_angsuran_lain_pas),
            ("Angsuran Yang Diajukan (Rp)", self.var_angsuran_diajukan),
            ("Angsuran Aktif di MUF (Rp)", self.var_angsuran_muf),
        ]
        self.entries_angsuran = {}
        for idx, (lbl, var) in enumerate(fields_angsuran):
            self._make_row(card2, idx, lbl)
            e = self._make_entry(card2, idx, var)
            self.entries_angsuran[lbl] = e
            var.trace_add("write", lambda *a, v=var, e=e: self._format_on_write(v, e))

        # ── Kartu 3: Data Pendapatan ─────
        card3 = self._make_card(parent, "Data Pendapatan")
        card3.columnconfigure(1, weight=1)

        self._make_row(card3, 0, "Pendapatan Debitur (Rp)")
        self.entry_pendapatan_deb = self._make_entry(card3, 0, self.var_pendapatan_deb)
        self.var_pendapatan_deb.trace_add(
            "write",
            lambda *a: self._format_on_write(self.var_pendapatan_deb, self.entry_pendapatan_deb),
        )

        self._make_row(card3, 1, "Pendapatan Debitur Range (Rp)")
        self.entry_pendapatan_range = self._make_entry(card3, 1, self.var_pendapatan_range)


        self._make_row(card3, 2, "Pendapatan Pasangan (Rp)")
        self.entry_pendapatan_pas = self._make_entry(card3, 2, self.var_pendapatan_pas)
        self.var_pendapatan_pas.trace_add(
            "write",
            lambda *a: self._format_on_write(self.var_pendapatan_pas, self.entry_pendapatan_pas),
        )


        # State awal
        self._on_platform_selected()
        self._on_pasangan_changed()

    # ── Tombol Aksi ──────────────────────
    def _build_buttons(self, parent):
        frame = tk.Frame(parent, bg=COLOR_BG, padx=32, pady=8)
        frame.pack(fill="x")

        btn_hitung = tk.Button(
            frame,
            text="  Hitung RAC / DBR  ",
            font=("Helvetica", 11, "bold"),
            bg=COLOR_BTN_CALC,
            fg=COLOR_BTN_FG,
            activebackground="#002966",
            activeforeground=COLOR_BTN_FG,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self._hitung,
        )
        btn_hitung.pack(side="left", expand=True, fill="x", padx=(0, 8))

        btn_reset = tk.Button(
            frame,
            text="  Reset  ",
            font=("Helvetica", 11, "bold"),
            bg=COLOR_BTN_RESET,
            fg=COLOR_BTN_FG,
            activebackground="#C53030",
            activeforeground=COLOR_BTN_FG,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self._reset,
        )
        btn_reset.pack(side="left", padx=(8, 0))

    # ── Panel Hasil ───────────────────────
    def _build_result_panel(self, parent):
        self.result_card = self._make_card(parent, "Hasil Perhitungan")
        self.result_card.columnconfigure(0, weight=1)

        self.lbl_result_placeholder = tk.Label(
            self.result_card,
            text="— Belum ada perhitungan —",
            font=FONT_LABEL,
            bg=COLOR_CARD,
            fg=COLOR_SUBLABEL,
        )
        self.lbl_result_placeholder.grid(row=0, column=0, columnspan=2, pady=20)

        # Baris hasil (disembunyikan dulu)
        self.result_rows = {}
        result_labels = [
            #total_pendapatan", "Total Pendapatan"),
            #("total_angsuran",   "Total Angsuran"),
            ("dbr_pct",          "DBR (%)"),
            #("batas_dbr",        "Batas DBR (%)"),
            ("status",           "Status"),
        ]
        for i, (key, text) in enumerate(result_labels):
            lbl_key = tk.Label(
                self.result_card,
                text=text,
                font=FONT_LABEL,
                bg=COLOR_CARD,
                fg=COLOR_LABEL,
                anchor="w",
                width=26,
            )
            lbl_val = tk.Label(
                self.result_card,
                text="",
                font=FONT_RESULT,
                bg=COLOR_CARD,
                fg=COLOR_RESULT_FG,
                anchor="e",
            )
            self.result_rows[key] = (lbl_key, lbl_val)

    # ── Event Handlers ────────────────────
    def _on_platform_selected(self, event=None):
        self._refresh_categories()
        platform = self.var_kategori.get()
        if platform == "LIVIN":
            self.entry_pendapatan_deb.config(
                state="normal", highlightbackground=COLOR_BORDER
            )
            self.entry_pendapatan_range.config(
                state="disabled",
                bg=COLOR_DISABLED,
                highlightbackground=COLOR_DISABLED,
            )
            self.var_pendapatan_range.set("")
        else:
            self.entry_pendapatan_range.config(
                state="normal",
                bg=COLOR_ENTRY_BG,
                highlightbackground=COLOR_BORDER,
            )
            self.entry_pendapatan_deb.config(
                state="disabled",
                bg=COLOR_DISABLED,
                highlightbackground=COLOR_DISABLED,
            )


    def _on_pasangan_changed(self, event=None):
        if self.var_punya_pasangan.get() == "YA":
            self.entry_pendapatan_pas.config(
                state="normal",
                bg=COLOR_ENTRY_BG,
                highlightbackground=COLOR_BORDER,
            )
            self.var_angsuran_lain_pas.set("")
            self.entries_angsuran["Angsuran Lain Pasangan (Rp)"].config(state="normal")
            self.fieldKTP_pasangan.config(
                state="normal",
                bg=COLOR_ENTRY_BG,
                highlightbackground=COLOR_BORDER,
            )
        else:
            self.var_pendapatan_pas.set("")
            self.entry_pendapatan_pas.config(
                state="disabled",
                bg=COLOR_DISABLED,
                highlightbackground=COLOR_DISABLED,
            )
            self.var_angsuran_lain_pas.set("")
            self.entries_angsuran["Angsuran Lain Pasangan (Rp)"].config(state="disabled")
            self.var_fieldKTP_pasangan.set("")
            self.fieldKTP_pasangan.config(
                state="disabled",
                bg=COLOR_DISABLED,
                highlightbackground=COLOR_DISABLED,
            )


    def _refresh_categories(self):
        platform = self.var_kategori.get()
        cats = CUSTOMER_CATEGORIES.get(platform, [])
        self.combo_category["values"] = cats
        if cats:
            self.combo_category.current(0)

    # ── Validasi & Format ─────────────────
    @staticmethod
    def _validate_ktp(value: str) -> bool:
        """Hanya angka, maksimal 16 digit."""
        if value == "":
            return True
        return value.isdigit() and len(value) <= 16

    @staticmethod
    def _only_digits(value: str) -> bool:
        return value.isdigit() or value == ""

    def _format_on_write(self, var: tk.StringVar, entry: tk.Entry):
        """Format angka dengan titik ribuan saat mengetik (non-destructive)."""
        raw = re.sub(r"\D", "", var.get())
        if raw:
            formatted = f"{int(raw):,}".replace(",", ".")
            if var.get() != formatted:
                var.set(formatted)
                entry.icursor(tk.END)

    # ── Cek Angsuran via KTP ─────────────
    def _cek_angsuran(self):
        """
        Fetch data angsuran berdasarkan NIK KTP debitur & pasangan,
        lalu isi ke field angsuran lain (field tetap bisa diedit).
        Saat ini menggunakan simulasi data — ganti dengan pemanggilan
        API / database yang sesungguhnya sesuai kebutuhan.
        """
        ktp_deb = self.var_fieldKTP.get().strip()
        ktp_pas = self.var_fieldKTP_pasangan.get().strip()
        noOrder = self.var_no_order.get().strip()

        # ── Validasi panjang ──────────────────
        if ktp_deb and len(ktp_deb) != 16:
            messagebox.showwarning(
                "NIK KTP Tidak Valid",
                f"NIK KTP Debitur harus 16 digit (saat ini {len(ktp_deb)} digit).",
            )
            return
        if ktp_pas and len(ktp_pas) != 16:
            messagebox.showwarning(
                "NIK KTP Tidak Valid",
                f"NIK KTP Pasangan harus 16 digit (saat ini {len(ktp_pas)} digit).",
            )
            return
        if not ktp_deb and not ktp_pas:
            messagebox.showinfo(
                "NIK KTP Kosong",
                "Masukkan minimal satu NIK KTP untuk mengecek angsuran.",
            )
            return

        angsuran_deb,angsuran_pas = mengambilDataAngsuran(ktp_deb, ktp_pas,noOrder)
        AngsuranLainnyaMUF = ambil_api(ktp_deb)

        # ── Simulasi lookup data angsuran ─────
        # TODO: Ganti blok ini dengan panggilan API / query database yang nyata.
        # Contoh: result = api_cek_angsuran(ktp_deb, ktp_pas)
        # Format kembalian: {"angsuran_deb": int, "angsuran_pas": int}
        # def _lookup_angsuran(nik: str) -> int:
        #     """Simulasi: kembalikan angsuran dummy berdasarkan digit terakhir NIK."""
        #     if not nik:
        #         return 0
        #     seed = int(nik[-2:])          # 2 digit terakhir sebagai seed
        #     return seed * 150_000         # dummy: 0 – 14.850.000

        


        
        # ── Isi field (tetap bisa diedit) ─────
        if ktp_deb:
            formatted_deb = f"{angsuran_deb:,}".replace(",", ".")
            self.var_angsuran_lain_deb.set(formatted_deb)
            formatted_deb_angsuran_MUF = f"{AngsuranLainnyaMUF:,}".replace(",", ".")
            self.var_angsuran_muf.set(formatted_deb_angsuran_MUF)

        if ktp_pas and self.var_punya_pasangan.get() == "YA":
            formatted_pas = f"{angsuran_pas:,}".replace(",", ".")
            self.var_angsuran_lain_pas.set(formatted_pas)
        elif ktp_pas and self.var_punya_pasangan.get() != "YA":
            messagebox.showinfo(
                "Info",
                "NIK KTP Pasangan diisi, tetapi status pernikahan belum 'YA'.\n"
                "Angsuran pasangan tidak diisi otomatis.",
            )
            return

        messagebox.showinfo(
            "Cek Angsuran Selesai",
            "Data angsuran berhasil diambil dan sudah diisi.\n"
            "Anda masih bisa mengubah nilainya secara manual.",
        )

    # ── Hitung ───────────────────────────
    def _hitung(self):
        platform = self.var_kategori.get()
        kategori = self.var_cust_category.get()
        onPasangan = self.var_punya_pasangan.get()
        pendapatanDebiturRange = self.var_pendapatan_range.get()


        if not kategori:
            messagebox.showwarning("Perhatian", "Pilih Customer Category terlebih dahulu.")
            return

        pendapatan_deb   = safe_int(self.var_pendapatan_deb.get())
        pendapatan_range = safe_int(self.var_pendapatan_range.get())
        pendapatan_pas   = safe_int(self.var_pendapatan_pas.get())
        angsuran_lain_deb = safe_int(self.var_angsuran_lain_deb.get())
        angsuran_lain_pas = safe_int(self.var_angsuran_lain_pas.get())
        angsuran_diajukan = safe_int(self.var_angsuran_diajukan.get())
        angsuran_muf      = safe_int(self.var_angsuran_muf.get())

        # Gunakan nilai yang aktif
        pendapatan_debitur = pendapatan_deb if platform == "LIVIN" else pendapatan_range

        if pendapatan_debitur == 0:
            messagebox.showwarning("Perhatian", "Pendapatan Debitur tidak boleh nol.")
            return



        result = hitung_rac_dbr(
            kategori=kategori,
            platform=platform,
            onPasangan = onPasangan,
            pendapatan_debitur=pendapatan_debitur,
            pendapatan_pasangan=pendapatan_pas,
            pendapatanDebiturRange = pendapatanDebiturRange,
            angsuran_lain_debitur=angsuran_lain_deb,
            angsuran_lain_pasangan=angsuran_lain_pas,
            angsuran_diajukan=angsuran_diajukan,
            angsuran_muf=angsuran_muf,
        )

        self._tampilkan_hasil(result)






    def _tampilkan_hasil(self, result: dict):
        # Sembunyikan placeholder
        self.lbl_result_placeholder.grid_remove()
        #print(f"ini adalah hasil Result {result['dbr_pct']}" ) 
        values = {
            #"total_pendapatan": format_rupiah(result["total_pendapatan"]),
           # "total_angsuran":   format_rupiah(result["total_angsuran"]),
            "dbr_pct":          f"{result['dbr_pct']:.2f} %",
            #"batas_dbr":        f"{result['batas_dbr']:.0f} %",
            "status":           "✅  LULUS" if result["lulus"] else "❌  TIDAK LULUS",
        }

        status_color = "#2D7D46" if result["lulus"] else "#C53030"

        for i, (key, (lbl_key, lbl_val)) in enumerate(self.result_rows.items()):
            color = status_color if key == "status" else COLOR_RESULT_FG
            lbl_val.config(text=values[key], fg=color)
            lbl_key.grid(row=i, column=0, padx=(0, 12), pady=5, sticky="w")
            lbl_val.grid(row=i, column=1, padx=0,       pady=5, sticky="e")

        # Tambah separator
        sep_color = status_color
        sep = tk.Frame(self.result_card, bg=sep_color, height=3)
        sep.grid(row=len(self.result_rows), column=0, columnspan=2, sticky="ew", pady=(8, 0))

    # ── Reset ─────────────────────────────
    def _reset(self):
        for var in [
            self.var_angsuran_lain_deb,
            self.var_angsuran_lain_pas,
            self.var_angsuran_diajukan,
            self.var_angsuran_muf,
            self.var_pendapatan_deb,
            self.var_fieldKTP,
            self.var_fieldKTP_pasangan,
            self.var_pendapatan_range,
            self.var_pendapatan_pas,
            self.var_no_order
        ]:
            var.set("")

        self.var_kategori.set("LIVIN")
        self.var_punya_pasangan.set("TIDAK")
        self._refresh_categories()
        self._on_platform_selected()
        self._on_pasangan_changed()

        # Sembunyikan hasil
        for _, (lbl_key, lbl_val) in self.result_rows.items():
            lbl_key.grid_remove()
            lbl_val.grid_remove()
        self.lbl_result_placeholder.grid(row=0, column=0, columnspan=2, pady=20)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    app = RacDbrApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
