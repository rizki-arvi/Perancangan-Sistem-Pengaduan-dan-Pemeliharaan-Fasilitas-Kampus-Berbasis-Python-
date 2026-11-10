from abc import ABC, abstractmethod

def _validasi_teks(nilai, nama_field):
    if not isinstance(nilai, str) or not nilai.strip():
        raise ValueError(f"{nama_field} tidak boleh kosong.")
    return nilai.strip()

class Pengguna(ABC):
    def __init__(self, id_pengguna, nama, peran):
        self._id_pengguna = _validasi_teks(id_pengguna, "ID pengguna")
        self._nama = _validasi_teks(nama, "Nama")
        self._peran = _validasi_teks(peran, "Peran")

    @property
    def id_pengguna(self):
        return self._id_pengguna

    @property
    def nama(self):
        return self._nama

    @nama.setter
    def nama(self, nilai):
        self._nama = _validasi_teks(nilai, "Nama")

    @property
    def peran(self):
        return self._peran

    # --- perilaku ---
    @abstractmethod
    def menu_tersedia(self):
        pass

    def __str__(self):
        return f"{self._nama} ({self._peran}, ID: {self._id_pengguna})"


class Pelapor(Pengguna):
    JENIS_VALID = ("Mahasiswa", "Dosen", "Staf")

    def __init__(self, id_pengguna, nama, jenis_pelapor):
        super().__init__(id_pengguna, nama, "Pelapor")
        self._jenis_pelapor = self._validasi_jenis(jenis_pelapor)

    @classmethod
    def _validasi_jenis(cls, jenis):
        if isinstance(jenis, str):
            for valid in cls.JENIS_VALID:
                if jenis.strip().lower() == valid.lower():
                    return valid
        raise ValueError(
            f"Jenis pelapor '{jenis}' tidak valid. "
            f"Pilihan: {', '.join(cls.JENIS_VALID)}."
        )

    @property
    def jenis_pelapor(self):
        return self._jenis_pelapor

    def menu_tersedia(self):
        return [
            "Ajukan Pengaduan",
            "Lihat Status dan Riwayat Pengaduan",
            "Keluar",
        ]

    def ajukan_pengaduan(self, layanan, fasilitas, kategori, deskripsi):
        return layanan.buat_pengaduan(self, fasilitas, kategori, deskripsi)

    def lihat_status(self, daftar_pengaduan):
        return [p.ringkasan() for p in daftar_pengaduan if p.pelapor is self]

    def __str__(self):
        return f"{self._nama} (Pelapor - {self._jenis_pelapor}, ID: {self._id_pengguna})"


class Admin(Pengguna):
    def __init__(self, id_pengguna, nama):
        super().__init__(id_pengguna, nama, "Admin")

    def menu_tersedia(self):
        return [
            "Kelola Data Pengguna dan Fasilitas",
            "Verifikasi Pengaduan",
            "Tolak Pengaduan",
            "Tugaskan Teknisi",
            "Keluar",
        ]

    def verifikasi(self, layanan, id_pengaduan, diterima=True, alasan=""):
        if not diterima:
            alasan = _validasi_teks(alasan, "Alasan penolakan")
        return layanan.verifikasi(id_pengaduan, diterima, alasan)

    def tugaskan_teknisi(self, layanan, id_pengaduan, teknisi):
        if not isinstance(teknisi, Teknisi):
            raise ValueError("Penugasan hanya dapat diberikan kepada Teknisi.")
        return layanan.tugaskan(id_pengaduan, teknisi)


class Teknisi(Pengguna):
    def __init__(self, id_pengguna, nama, keahlian):
        super().__init__(id_pengguna, nama, "Teknisi")
        self._keahlian = _validasi_teks(keahlian, "Keahlian")

    @property
    def keahlian(self):
        return self._keahlian

    def menu_tersedia(self):
        return [
            "Perbarui Progres Perbaikan",
            "Selesaikan Perbaikan",
            "Keluar",
        ]

    def perbarui_progres(self, layanan, id_pengaduan, catatan):
        catatan = _validasi_teks(catatan, "Catatan progres")
        return layanan.perbarui_progres(id_pengaduan, catatan)

    def selesaikan_tugas(self, layanan, id_pengaduan, catatan):
        catatan = _validasi_teks(catatan, "Catatan penyelesaian")
        return layanan.selesaikan(id_pengaduan, catatan)

    def __str__(self):
        return f"{self._nama} (Teknisi - {self._keahlian}, ID: {self._id_pengguna})"
