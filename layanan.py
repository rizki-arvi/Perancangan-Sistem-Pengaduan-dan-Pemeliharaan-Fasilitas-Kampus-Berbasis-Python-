"""layanan.py - LayananPengaduan: hanya mengoordinasi alur pengaduan (SRP).

Aturan prioritas ada di kategori.py dan aturan alur status ada di
pengaduan.py. Class ini tidak menulis kedua aturan itu.
"""
from pengguna import Pelapor, Admin, Teknisi
from pengaduan import Pengaduan
from tugas import TugasPemeliharaan


class LayananPengaduan:
    def __init__(self, daftar_notifikasi=None):
        self.daftar_pengaduan = []
        self.daftar_fasilitas = []
        self.daftar_notifikasi = list(daftar_notifikasi or [])
        self._daftar_tugas = []
        self._nomor_terakhir = 0

    # ---------- registrasi data ----------
    def tambah_fasilitas(self, fasilitas):
        if self._cari_fasilitas(fasilitas.id_fasilitas, wajib=False):
            raise ValueError(f"Fasilitas {fasilitas.id_fasilitas} sudah terdaftar.")
        self.daftar_fasilitas.append(fasilitas)

    def tambah_notifikasi(self, notifikasi):
        """Kanal baru (mis. NotifikasiEmail) cukup didaftarkan di sini (OCP)."""
        self.daftar_notifikasi.append(notifikasi)

    # ---------- alur utama ----------
    def buat_pengaduan(self, pelapor, id_fasilitas, kategori, deskripsi):
        """F03: pelapor mengajukan pengaduan (status awal: Diajukan)."""
        if not isinstance(pelapor, Pelapor):
            raise PermissionError("Hanya Pelapor yang dapat mengajukan pengaduan.")
        fasilitas = self._cari_fasilitas(id_fasilitas)
        if not deskripsi or not deskripsi.strip():
            raise ValueError("Deskripsi pengaduan tidak boleh kosong.")

        self._nomor_terakhir += 1
        pengaduan = Pengaduan(
            id_pengaduan=f"P{self._nomor_terakhir:03d}",
            pelapor=pelapor,
            fasilitas=fasilitas,
            deskripsi=deskripsi.strip(),
            kategori=kategori,   # prioritas & target waktu dari kategori
        )
        self.daftar_pengaduan.append(pengaduan)
        self._notifikasi(pengaduan, f"Pengaduan {pengaduan.id_pengaduan} diajukan "
                                    f"(status: {pengaduan.status}).")
        return pengaduan

    def verifikasi(self, admin, id_pengaduan, diterima=True, alasan=""):
        """F04: admin memverifikasi atau menolak pengaduan."""
        self._wajib_peran(admin, Admin, "memverifikasi pengaduan")
        pengaduan = self._cari_pengaduan(id_pengaduan)
        if diterima:
            pengaduan.ubah_status("Diverifikasi")
            self._notifikasi(pengaduan, f"Pengaduan {id_pengaduan} diverifikasi.")
        else:
            if not alasan.strip():
                raise ValueError("Alasan penolakan wajib diisi.")
            pengaduan.ubah_status("Ditolak")
            self._notifikasi(pengaduan, f"Pengaduan {id_pengaduan} ditolak. Alasan: {alasan}")
        return pengaduan

    def tugaskan(self, admin, id_pengaduan, teknisi):
        """F06: admin menugaskan teknisi -> TugasPemeliharaan dibuat."""
        self._wajib_peran(admin, Admin, "menugaskan teknisi")
        self._wajib_peran(teknisi, Teknisi, "menerima tugas")
        pengaduan = self._cari_pengaduan(id_pengaduan)
        pengaduan.ubah_status("Ditugaskan")      # gagal dulu bila alur salah
        tugas = TugasPemeliharaan(pengaduan, teknisi)
        self._daftar_tugas.append(tugas)
        self._notifikasi(pengaduan, f"Pengaduan {id_pengaduan} ditugaskan ke {teknisi.nama}.")
        return tugas

    def mulai_perbaikan(self, teknisi, id_pengaduan):
        """F07: teknisi memulai perbaikan (status: Dalam Perbaikan)."""
        tugas = self._cari_tugas(id_pengaduan, teknisi)
        tugas.pengaduan.ubah_status("Dalam Perbaikan")
        tugas.mulai()
        self._notifikasi(tugas.pengaduan,
                         f"Pengaduan {id_pengaduan} sedang dalam perbaikan.")
        return tugas

    def selesaikan(self, teknisi, id_pengaduan, catatan):
        """F07: teknisi menyelesaikan perbaikan (status: Selesai)."""
        tugas = self._cari_tugas(id_pengaduan, teknisi)
        tugas.selesai(catatan)                   # menolak bila belum dimulai
        tugas.pengaduan.ubah_status("Selesai")
        self._notifikasi(tugas.pengaduan,
                         f"Pengaduan {id_pengaduan} selesai. Catatan: {catatan}")
        return tugas

    # ---------- pemantauan (F08) ----------
    def lihat_status(self, pelapor):
        """Riwayat pengaduan milik satu pelapor."""
        return [p for p in self.daftar_pengaduan if p.pelapor is pelapor]

    # ---------- helper internal ----------
    def _notifikasi(self, pengaduan, pesan):
        """F09: kirim ke semua kanal terdaftar tanpa tahu jenis kanalnya."""
        for kanal in self.daftar_notifikasi:
            kanal.kirim(pengaduan.pelapor, pesan)

    @staticmethod
    def _wajib_peran(pengguna, kelas, aksi):
        if not isinstance(pengguna, kelas):
            raise PermissionError(f"Hanya {kelas.__name__} yang dapat {aksi}.")

    def _cari_fasilitas(self, id_fasilitas, wajib=True):
        for f in self.daftar_fasilitas:
            if f.id_fasilitas == id_fasilitas:
                return f
        if wajib:
            raise ValueError(f"Fasilitas '{id_fasilitas}' tidak ditemukan.")
        return None

    def _cari_pengaduan(self, id_pengaduan):
        for p in self.daftar_pengaduan:
            if p.id_pengaduan == id_pengaduan:
                return p
        raise ValueError(f"Pengaduan '{id_pengaduan}' tidak ditemukan.")

    def _cari_tugas(self, id_pengaduan, teknisi):
        self._wajib_peran(teknisi, Teknisi, "memperbarui perbaikan")
        for t in self._daftar_tugas:
            if t.pengaduan.id_pengaduan == id_pengaduan and t.teknisi is teknisi:
                return t
        raise ValueError(f"Tidak ada tugas {id_pengaduan} untuk teknisi ini.")