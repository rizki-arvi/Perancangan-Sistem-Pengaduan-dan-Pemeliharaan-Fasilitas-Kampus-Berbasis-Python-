"""Menu konsol Sistem Pengaduan dan Pemeliharaan Fasilitas Kampus.
"""
import contextlib
import io
import os
import sys
from abc import ABC, abstractmethod

from fasilitas import Fasilitas
from kategori import KategoriPengaduan
from layanan import LayananPengaduan
from notifikasi import Notifikasi, NotifikasiKonsol, NotifikasiLog
from pengguna import Admin, Pelapor, Teknisi

GALAT_BISNIS = (ValueError,)

DIAJUKAN, DIVERIFIKASI, DITUGASKAN = "Diajukan", "Diverifikasi", "Ditugaskan"
DALAM_PERBAIKAN, SELESAI = "Dalam Perbaikan", "Selesai"


# --------------------------------------------------------------------------
# Data awal (di memori)
# --------------------------------------------------------------------------
class DataAwal:
    def __init__(self):
        self.pelapor = [Pelapor("P001", "Budi Santoso", "Mahasiswa"),
                        Pelapor("P002", "Dewi Lestari", "Dosen")]
        self.admin = [Admin("A001", "Sari Wulandari")]
        self.teknisi = [Teknisi("T001", "Doni Pratama", "Listrik"),
                        Teknisi("T002", "Rudi Hartono", "Jaringan")]
        self.fasilitas = [Fasilitas("F001", "Proyektor R.101", "Gedung A", "Baik"),
                          Fasilitas("F002", "AC Lab Komputasi", "Gedung B", "Baik"),
                          Fasilitas("F003", "Kursi Kelas R.205", "Gedung A", "Baik")]


def buat_layanan(data, kanal):
    layanan = LayananPengaduan(daftar_notifikasi=list(kanal))
    layanan.daftar_fasilitas.extend(data.fasilitas)
    return layanan


# --------------------------------------------------------------------------
# I/O konsol
# --------------------------------------------------------------------------
class Konsol:
    def __init__(self, masukan=input, keluaran=print):
        self._masukan = masukan
        self._keluaran = keluaran

    def tulis(self, teks=""):
        self._keluaran(teks)

    def baca(self, label):
        return self._masukan(label).strip()

    def pilih(self, judul, opsi, label_keluar="Kembali"):
        while True:
            self.tulis(f"\n=== {judul} ===")
            for no, teks in enumerate(opsi, 1):
                self.tulis(f"{no}. {teks}")
            self.tulis(f"0. {label_keluar}")
            jawab = self.baca("Pilihan: ")
            if jawab.isdigit():
                nomor = int(jawab)
                if nomor == 0:
                    return None
                if 1 <= nomor <= len(opsi):
                    return nomor - 1
            self.tulis("[GALAT] Pilihan tidak valid, masukkan nomor yang tersedia.")

    def pilih_objek(self, judul, daftar, format_teks):
        if not daftar:
            self.tulis(f"[INFO] {judul}: tidak ada data.")
            return None
        idx = self.pilih(judul, [format_teks(o) for o in daftar])
        return None if idx is None else daftar[idx]


# --------------------------------------------------------------------------
# Menu per peran
# --------------------------------------------------------------------------
class MenuKonsol(ABC):
    def __init__(self, layanan, data, pengguna, konsol):
        self.layanan = layanan
        self.data = data
        self.pengguna = pengguna
        self.konsol = konsol

    @abstractmethod
    def daftar_menu(self):
        pass

    def jalankan(self):
        while True:
            menu = self.daftar_menu()
            idx = self.konsol.pilih(f"Menu {self.pengguna.peran}: {self.pengguna.nama}",
                                    [label for label, _ in menu])
            if idx is None:
                return
            try:
                menu[idx][1]()
            except GALAT_BISNIS as galat:
                self.konsol.tulis(f"[GALAT] {galat}")

    @staticmethod
    def _teks_pengaduan(p):
        return p.ringkasan()

    def _pilih_pengaduan(self, judul, status=None, daftar=None):
        sumber = self.layanan.daftar_pengaduan if daftar is None else daftar
        if status is not None:
            sumber = [p for p in sumber if p.status == status]
        return self.konsol.pilih_objek(judul, sumber, self._teks_pengaduan)

    def _tampilkan(self, daftar):
        if not daftar:
            self.konsol.tulis("[INFO] Belum ada data.")
        for p in daftar:
            self.konsol.tulis(f"- {p.ringkasan()}")


class MenuPelapor(MenuKonsol):
    def daftar_menu(self):
        return [("Ajukan pengaduan", self._ajukan),
                ("Lihat status dan riwayat pengaduan saya", self._lihat_status)]

    def _ajukan(self):
        fasilitas = self.konsol.pilih_objek(
            "Pilih fasilitas", self.layanan.daftar_fasilitas,
            lambda f: f"{f.nama} - {f.lokasi} ({f.kondisi})")
        if fasilitas is None:
            return
        kategori = self.konsol.pilih_objek(
            "Pilih kategori kerusakan",
            [kelas() for kelas in KategoriPengaduan.__subclasses__()],
            lambda k: k.nama)
        if kategori is None:
            return
        while True:  # flowchart: data tidak valid -> kembali ke input
            deskripsi = self.konsol.baca("Deskripsi kerusakan (ketik 'batal' untuk kembali): ")
            if deskripsi.lower() == "batal":
                return
            try:
                pengaduan = self.layanan.buat_pengaduan(self.pengguna, fasilitas, kategori, deskripsi)
            except GALAT_BISNIS as galat:
                self.konsol.tulis(f"[GALAT] {galat}")
                continue
            self.konsol.tulis(f"[OK] Pengaduan tersimpan: {pengaduan.ringkasan()}")
            return

    def _lihat_status(self):
        self._tampilkan([p for p in self.layanan.daftar_pengaduan if p.pelapor is self.pengguna])


class MenuAdmin(MenuKonsol):
    def daftar_menu(self):
        return [("Lihat semua pengaduan", lambda: self._tampilkan(self.layanan.daftar_pengaduan)),
                ("Verifikasi pengaduan", self._verifikasi),
                ("Tolak pengaduan", self._tolak),
                ("Tugaskan teknisi", self._tugaskan),
                ("Ubah status manual (uji validasi alur)", self._ubah_manual)]

    def _verifikasi(self):
        p = self._pilih_pengaduan("Pengaduan berstatus Diajukan", DIAJUKAN)
        if p is not None:
            self.layanan.verifikasi(p)
            self.konsol.tulis(f"[OK] {p.ringkasan()}")

    def _tolak(self):
        p = self._pilih_pengaduan("Pengaduan berstatus Diajukan", DIAJUKAN)
        if p is not None:
            self.layanan.tolak(p, self.konsol.baca("Alasan penolakan: "))
            self.konsol.tulis(f"[OK] {p.ringkasan()}")

    def _tugaskan(self):
        p = self._pilih_pengaduan("Pengaduan berstatus Diverifikasi", DIVERIFIKASI)
        if p is None:
            return
        teknisi = self.konsol.pilih_objek("Pilih teknisi", self.data.teknisi,
                                          lambda t: f"{t.nama} ({t.keahlian})")
        if teknisi is not None:
            self.layanan.tugaskan(p, teknisi)
            self.konsol.tulis(f"[OK] {p.ringkasan()}")

    def _ubah_manual(self):
        p = self._pilih_pengaduan("Pilih pengaduan")
        if p is not None:
            p.ubah_status(self.konsol.baca("Status baru: "))
            self.konsol.tulis(f"[OK] {p.ringkasan()}")


class MenuTeknisi(MenuKonsol):
    def daftar_menu(self):
        return [("Lihat tugas saya", lambda: self._tampilkan(self._pengaduan_saya())),
                ("Mulai perbaikan", self._mulai),
                ("Selesaikan perbaikan", self._selesaikan)]

    def _pengaduan_saya(self, status=None):
        hasil = [t.pengaduan for t in self.layanan.daftar_tugas if t.teknisi is self.pengguna]
        return [p for p in hasil if status is None or p.status == status]

    def _mulai(self):
        p = self._pilih_pengaduan("Tugas berstatus Ditugaskan",
                                  daftar=self._pengaduan_saya(DITUGASKAN))
        if p is not None:
            self.layanan.mulai_perbaikan(p)
            self.konsol.tulis(f"[OK] {p.ringkasan()}")

    def _selesaikan(self):
        p = self._pilih_pengaduan("Tugas berstatus Dalam Perbaikan",
                                  daftar=self._pengaduan_saya(DALAM_PERBAIKAN))
        if p is not None:
            self.layanan.selesaikan(p, self.konsol.baca("Catatan perbaikan: "))
            self.konsol.tulis(f"[OK] {p.ringkasan()}")


MENU_PER_PERAN = {Pelapor: MenuPelapor, Admin: MenuAdmin, Teknisi: MenuTeknisi}


class AplikasiKonsol:
    def __init__(self, layanan, data, konsol):
        self.layanan, self.data, self.konsol = layanan, data, konsol

    def jalankan(self):
        peran = [("Pelapor", self.data.pelapor), ("Admin", self.data.admin),
                 ("Teknisi", self.data.teknisi)]
        while True:
            idx = self.konsol.pilih("SISTEM PENGADUAN FASILITAS KAMPUS - Masuk sebagai",
                                    [nama for nama, _ in peran], "Keluar")
            if idx is None:
                self.konsol.tulis("Sampai jumpa.")
                return
            akun = self.konsol.pilih_objek(f"Pilih akun {peran[idx][0]}", peran[idx][1],
                                           lambda a: f"{a.nama} ({a.id_pengguna})")
            if akun is not None:
                MENU_PER_PERAN[type(akun)](self.layanan, self.data, akun, self.konsol).jalankan()


# --------------------------------------------------------------------------
# Skenario uji (Bagian 8.3 proposal)
# --------------------------------------------------------------------------
class SkenarioUji:
    def __init__(self, path_log="uji_notifikasi.log"):
        self.path_log = path_log
        self.hasil = []

    def _cek(self, nama, kondisi):
        self.hasil.append((nama, bool(kondisi)))
        print(f"  [{'LULUS' if kondisi else 'GAGAL'}] {nama}", file=sys.__stdout__)

    @staticmethod
    def _galat(fungsi, *args):
        try:
            fungsi(*args)
        except GALAT_BISNIS:
            return True
        return False

    def _siapkan(self, kanal_tambahan=()):
        data = DataAwal()
        kanal = [NotifikasiKonsol(), NotifikasiLog(self.path_log), *kanal_tambahan]
        return data, buat_layanan(data, kanal)

    @staticmethod
    def _kategori():
        return KategoriPengaduan.__subclasses__()[0]()

    def jalankan(self):
        if os.path.exists(self.path_log):
            os.remove(self.path_log)
        print("== SKENARIO UJI ==")
        self._alur_normal()
        self._input_tidak_valid()
        self._tolak()
        self._status_di_luar_alur()
        self._kanal_baru_ocp()
        self._menu_per_peran()
        lulus = sum(1 for _, ok in self.hasil if ok)
        print(f"\nHasil: {lulus}/{len(self.hasil)} pengecekan lulus")
        return lulus == len(self.hasil)

    def _alur_normal(self):
        print("\n[1] Alur normal Pelapor -> Admin -> Teknisi")
        data, layanan = self._siapkan()
        pelapor, admin, teknisi = data.pelapor[0], data.admin[0], data.teknisi[0]
        with contextlib.redirect_stdout(io.StringIO()) as layar:
            p = layanan.buat_pengaduan(pelapor, data.fasilitas[0], self._kategori(), "Proyektor mati")
        self._cek("Pengaduan tersimpan berstatus Diajukan", p.status == DIAJUKAN)
        self._cek("Prioritas terisi dari kategori", bool(p.prioritas))
        self._cek("Notifikasi konsol tampil", pelapor.nama in layar.getvalue())
        self._cek("Pelapor melihat riwayat pengaduannya",
                  p in [x for x in layanan.daftar_pengaduan if x.pelapor is pelapor])
        with contextlib.redirect_stdout(io.StringIO()):
            layanan.verifikasi(p)
            self._cek("Admin verifikasi -> Diverifikasi", p.status == DIVERIFIKASI)
            tugas = layanan.tugaskan(p, teknisi)
            self._cek("Penugasan -> Ditugaskan + TugasPemeliharaan dibuat",
                      p.status == DITUGASKAN and tugas in layanan.daftar_tugas)
            layanan.mulai_perbaikan(p)
            self._cek("Teknisi mulai -> Dalam Perbaikan", p.status == DALAM_PERBAIKAN)
            layanan.selesaikan(p, "Kabel diganti")
        self._cek("Teknisi selesai -> Selesai + tanggal selesai tercatat",
                  p.status == SELESAI and tugas.tanggal_selesai is not None)
        with open(self.path_log, encoding="utf-8") as berkas:
            baris = [b for b in berkas if pelapor.nama in b]
        self._cek("Notifikasi log tercatat untuk tiap perubahan status (>=5 baris)", len(baris) >= 5)

    def _input_tidak_valid(self):
        print("\n[2] Input tidak valid")
        data, layanan = self._siapkan()
        pelapor, kategori = data.pelapor[0], self._kategori()
        with contextlib.redirect_stdout(io.StringIO()):
            self._cek("Deskripsi kosong ditolak",
                      self._galat(layanan.buat_pengaduan, pelapor, data.fasilitas[0], kategori, "   "))
            self._cek("Fasilitas tidak ditemukan ditolak",
                      self._galat(layanan.buat_pengaduan, pelapor, None, kategori, "Rusak"))
        self._cek("Tidak ada pengaduan tersimpan dari input tidak valid", not layanan.daftar_pengaduan)

    def _tolak(self):
        print("\n[3] Admin menolak pengaduan")
        data, layanan = self._siapkan()
        with contextlib.redirect_stdout(io.StringIO()):
            p = layanan.buat_pengaduan(data.pelapor[0], data.fasilitas[1], self._kategori(), "Duplikat")
            layanan.tolak(p, "Laporan ganda")
        self._cek("Status menjadi Ditolak", p.status == "Ditolak")
        with open(self.path_log, encoding="utf-8") as berkas:
            self._cek("Alasan penolakan masuk log", "Laporan ganda" in berkas.read())

    def _status_di_luar_alur(self):
        print("\n[4] Perubahan status di luar alur")
        data, layanan = self._siapkan()
        with contextlib.redirect_stdout(io.StringIO()):
            p = layanan.buat_pengaduan(data.pelapor[0], data.fasilitas[2], self._kategori(), "Kursi patah")
        self._cek("Diajukan -> Selesai ditolak", self._galat(p.ubah_status, SELESAI))
        self._cek("Status tetap Diajukan setelah penolakan", p.status == DIAJUKAN)
        self._cek("Status tidak dikenal ditolak", self._galat(p.ubah_status, "Asal"))

    def _kanal_baru_ocp(self):
        print("\n[5] Kanal notifikasi baru tanpa mengubah kode lama (OCP)")

        class NotifikasiEmail(Notifikasi):
            def __init__(self):
                self.terkirim = []

            def kirim(self, penerima, pesan):
                self.terkirim.append((penerima.nama, pesan))

        email = NotifikasiEmail()
        data, layanan = self._siapkan([email])
        with contextlib.redirect_stdout(io.StringIO()):
            layanan.buat_pengaduan(data.pelapor[0], data.fasilitas[0], self._kategori(), "AC panas")
        self._cek("Subclass baru ikut menerima notifikasi", len(email.terkirim) == 1)

    def _menu_per_peran(self):
        print("\n[6] Menu konsol per peran (input terskrip)")
        data, layanan = self._siapkan()
        skrip = iter([
            "1", "1", "1", "1", "1", "", "AC bocor", "0",              # Pelapor: ajukan (deskripsi kosong dulu)
            "2", "1", "2", "1", "4", "1", "1", "5", "1", "Selesai", "0",  # Admin: verifikasi, tugaskan, status ilegal
            "3", "1", "2", "1", "3", "1", "Sudah diganti", "0",     # Teknisi: mulai, selesai
            "0"])                                                   # keluar
        keluaran = []
        konsol = Konsol(masukan=lambda _label: next(skrip), keluaran=keluaran.append)
        with contextlib.redirect_stdout(io.StringIO()):
            AplikasiKonsol(layanan, data, konsol).jalankan()
        teks = "\n".join(keluaran)
        self._cek("Menu Pelapor: deskripsi kosong ditolak lalu pengaduan tersimpan",
                  "[GALAT]" in teks and len(layanan.daftar_pengaduan) == 1)
        self._cek("Menu Admin: verifikasi, tugaskan, dan status ilegal ditolak (total 2 galat)",
                  teks.count("[GALAT]") == 2)
        self._cek("Menu Teknisi: pengaduan berakhir Selesai",
                  layanan.daftar_pengaduan[0].status == SELESAI)


def main(argumen):
    if "--uji" in argumen:
        return 0 if SkenarioUji().jalankan() else 1
    data = DataAwal()
    layanan = buat_layanan(data, [NotifikasiKonsol(), NotifikasiLog("notifikasi.log")])
    try:
        AplikasiKonsol(layanan, data, Konsol()).jalankan()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram dihentikan.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
