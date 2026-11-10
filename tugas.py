from datetime import datetime

from pengguna import Teknisi

STATUS_DALAM_PERBAIKAN = "Dalam Perbaikan"
STATUS_SELESAI = "Selesai"

class TugasPemeliharaan:
    def __init__(self, pengaduan, teknisi):
        if pengaduan is None:
            raise ValueError("Pengaduan tidak boleh kosong.")
        if not isinstance(teknisi, Teknisi):
            raise ValueError("Tugas pemeliharaan hanya dapat diberikan kepada Teknisi.")
        self._pengaduan = pengaduan
        self._teknisi = teknisi
        self._tanggal_mulai = None
        self._tanggal_selesai = None
        self._catatan = ""
        self._riwayat_progres = []

    @property
    def pengaduan(self):
        return self._pengaduan

    @property
    def teknisi(self):
        return self._teknisi

    @property
    def tanggal_mulai(self):
        return self._tanggal_mulai

    @property
    def tanggal_selesai(self):
        return self._tanggal_selesai

    @property
    def catatan(self):
        return self._catatan

    @property
    def riwayat_progres(self):
        return list(self._riwayat_progres)

    @property
    def sudah_dimulai(self):
        return self._tanggal_mulai is not None

    @property
    def sudah_selesai(self):
        return self._tanggal_selesai is not None

    def mulai(self):
        if self.sudah_dimulai:
            raise ValueError("Tugas sudah dimulai sebelumnya.")
        self._pengaduan.ubah_status(STATUS_DALAM_PERBAIKAN)
        self._tanggal_mulai = datetime.now()

    def catat_progres(self, catatan_progres):
        if not self.sudah_dimulai:
            raise ValueError("Tugas belum dimulai, progres belum dapat dicatat.")
        if self.sudah_selesai:
            raise ValueError("Tugas sudah selesai, progres tidak dapat ditambah.")
        if not isinstance(catatan_progres, str) or not catatan_progres.strip():
            raise ValueError("Catatan progres tidak boleh kosong.")
        self._riwayat_progres.append((datetime.now(), catatan_progres.strip()))

    def selesai(self, catatan):
        if not self.sudah_dimulai:
            raise ValueError("Tugas tidak dapat diselesaikan sebelum dimulai.")
        if self.sudah_selesai:
            raise ValueError("Tugas sudah diselesaikan sebelumnya.")
        if not isinstance(catatan, str) or not catatan.strip():
            raise ValueError("Catatan penyelesaian tidak boleh kosong.")
        self._pengaduan.ubah_status(STATUS_SELESAI)
        self._tanggal_selesai = datetime.now()
        self._catatan = catatan.strip()

    def __str__(self):
        if self.sudah_selesai:
            keadaan = "Selesai"
        elif self.sudah_dimulai:
            keadaan = "Sedang dikerjakan"
        else:
            keadaan = "Belum dimulai"
        return f"Tugas oleh {self._teknisi.nama}: {keadaan}"
