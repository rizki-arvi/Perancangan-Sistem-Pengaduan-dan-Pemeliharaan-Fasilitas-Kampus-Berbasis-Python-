from pengaduan import Pengaduan, DIVERIFIKASI, DITOLAK, DITUGASKAN
from pengguna import Pelapor
from tugas import TugasPemeliharaan


class LayananPengaduan:
    def __init__(self, daftar_notifikasi=None):
        self.daftar_pengaduan = []
        self.daftar_fasilitas = []
        self.daftar_notifikasi = list(daftar_notifikasi or [])
        self.daftar_tugas = []

    # registrasi 
    def tambah_fasilitas(self, fasilitas):
        if any(f.id_fasilitas == fasilitas.id_fasilitas for f in self.daftar_fasilitas):
            raise ValueError(f"Fasilitas {fasilitas.id_fasilitas} sudah terdaftar.")
        self.daftar_fasilitas.append(fasilitas)

    def tambah_notifikasi(self, notifikasi):
        """Kanal baru cukup didaftarkan di sini (OCP)."""
        self.daftar_notifikasi.append(notifikasi)

    # alur utama 
    def buat_pengaduan(self, pelapor, fasilitas, kategori, deskripsi):
        """F03: status awal Diajukan; prioritas dari kategori."""
        if not isinstance(pelapor, Pelapor):
            raise ValueError("Hanya Pelapor yang dapat mengajukan pengaduan.")
        fasilitas = self._ambil_fasilitas(fasilitas)
        pengaduan = Pengaduan(f"ADU-{len(self.daftar_pengaduan) + 1:03d}",
                              pelapor, fasilitas, deskripsi, kategori)
        self.daftar_pengaduan.append(pengaduan)
        self._notifikasi(pengaduan, f"Pengaduan {pengaduan.id_pengaduan} diajukan "
                                    f"(prioritas {pengaduan.prioritas}, "
                                    f"target {pengaduan.target_waktu_hari} hari).")
        return pengaduan

    def verifikasi(self, pengaduan, diterima=True, alasan=""):
        """F04: terima (Diverifikasi) atau tolak (Ditolak, alasan wajib)."""
        p = self._ambil_pengaduan(pengaduan)
        if diterima:
            p.ubah_status(DIVERIFIKASI, "Diverifikasi admin")
            pesan = f"Pengaduan {p.id_pengaduan} diverifikasi."
        else:
            alasan = (alasan or "").strip()
            if not alasan:
                raise ValueError("Alasan penolakan tidak boleh kosong.")
            p.ubah_status(DITOLAK, alasan)
            pesan = f"Pengaduan {p.id_pengaduan} ditolak. Alasan: {alasan}"
        self._notifikasi(p, pesan)
        return p

    def tolak(self, pengaduan, alasan):
        return self.verifikasi(pengaduan, diterima=False, alasan=alasan)

    def tugaskan(self, pengaduan, teknisi):
        """F06: buat TugasPemeliharaan, status -> Ditugaskan."""
        p = self._ambil_pengaduan(pengaduan)
        tugas = TugasPemeliharaan(p, teknisi)          # validasi teknisi
        p.ubah_status(DITUGASKAN, f"Ditugaskan ke {teknisi.nama}")
        self.daftar_tugas.append(tugas)                # hanya jika status valid
        self._notifikasi(p, f"Pengaduan {p.id_pengaduan} ditugaskan ke {teknisi.nama}.")
        return tugas

    def mulai_perbaikan(self, pengaduan):
        """F07: tugas.mulai() sendiri mengubah status -> Dalam Perbaikan."""
        tugas = self._cari_tugas(pengaduan)
        tugas.mulai()
        self._notifikasi(tugas.pengaduan,
                         f"Pengaduan {tugas.pengaduan.id_pengaduan} sedang dalam perbaikan.")
        return tugas

    def perbarui_progres(self, pengaduan, catatan):
        """F07: catat progres; otomatis memulai tugas bila belum dimulai."""
        tugas = self._cari_tugas(pengaduan)
        if not tugas.sudah_dimulai:
            self.mulai_perbaikan(pengaduan)
        tugas.catat_progres(catatan)
        return tugas

    def selesaikan(self, pengaduan, catatan):
        """F07: tugas.selesai() sendiri mengubah status -> Selesai."""
        tugas = self._cari_tugas(pengaduan)
        tugas.selesai(catatan)
        self._notifikasi(tugas.pengaduan,
                         f"Pengaduan {tugas.pengaduan.id_pengaduan} selesai. "
                         f"Catatan: {tugas.catatan}")
        return tugas

    # pemantauan (F08)
    def pengaduan_milik(self, pelapor):
        return [p for p in self.daftar_pengaduan if p.pelapor is pelapor]

    # helper internal 
    def _notifikasi(self, pengaduan, pesan):
        """F09: kirim ke semua kanal tanpa tahu jenis kanalnya (polimorfisme)."""
        for kanal in self.daftar_notifikasi:
            kanal.kirim(pengaduan.pelapor, pesan)

    def _ambil_fasilitas(self, fasilitas):
        for f in self.daftar_fasilitas:
            if f is fasilitas or f.id_fasilitas == fasilitas:
                return f
        raise ValueError("Fasilitas tidak ditemukan.")

    def _ambil_pengaduan(self, pengaduan):
        for p in self.daftar_pengaduan:
            if p is pengaduan or p.id_pengaduan == pengaduan:
                return p
        raise ValueError("Pengaduan tidak ditemukan.")

    def _cari_tugas(self, pengaduan):
        p = self._ambil_pengaduan(pengaduan)
        for t in self.daftar_tugas:
            if t.pengaduan is p:
                return t
        raise ValueError(f"Pengaduan {p.id_pengaduan} belum ditugaskan ke teknisi.")