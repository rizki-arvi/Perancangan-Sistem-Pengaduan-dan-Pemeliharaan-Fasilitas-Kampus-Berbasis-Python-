from datetime import datetime
from kategori import KategoriPengaduan

class DataTidakValidError(ValueError):
    pass

class StatusTidakValidError(ValueError):
    pass

DIAJUKAN = "Diajukan"
DIVERIFIKASI = "Diverifikasi"
DITOLAK = "Ditolak"
DITUGASKAN = "Ditugaskan"
DALAM_PERBAIKAN = "Dalam Perbaikan"
SELESAI = "Selesai"

ALUR_STATUS = {
    DIAJUKAN: [DIVERIFIKASI, DITOLAK],
    DIVERIFIKASI: [DITUGASKAN],
    DITUGASKAN: [DALAM_PERBAIKAN],
    DALAM_PERBAIKAN: [SELESAI],
    DITOLAK: [],
    SELESAI: [],
}

class Pengaduan:
    def __init__(self, id_pengaduan: str, pelapor, fasilitas, deskripsi: str, kategori: KategoriPengaduan):
        if not id_pengaduan or not str(id_pengaduan).strip():
            raise DataTidakValidError("ID pengaduan tidak boleh kosong.")
        if pelapor is None:
            raise DataTidakValidError("Pelapor harus diisi.")
        if fasilitas is None:
            raise DataTidakValidError("Fasilitas tidak ditemukan.")
        if not deskripsi or not deskripsi.strip():
            raise DataTidakValidError("Deskripsi tidak boleh kosong.")
        if not isinstance(kategori, KategoriPengaduan):
            raise DataTidakValidError("Kategori pengaduan tidak valid.")
            
        self.id_pengaduan = id_pengaduan
        self.pelapor = pelapor
        self.fasilitas = fasilitas
        self.deskripsi = deskripsi.strip()
        self.kategori = kategori
        self.tanggal_lapor = datetime.now()
        self.__status = DIAJUKAN
        self.__riwayat = [(self.tanggal_lapor, DIAJUKAN, "Pengaduan diajukan")]
        self.prioritas = self.tentukan_prioritas()
        self.target_waktu_hari = self.kategori.target_waktu_hari()

    @property
    def status(self) -> str:
        return self.__status

    @property
    def riwayat(self) -> list:
        return list(self.__riwayat)

    def ubah_status(self, status_baru: str, keterangan: str = "") -> None:
        if status_baru not in ALUR_STATUS:
            raise StatusTidakValidError(f"Status {status_baru} tidak dikenal.")
            
        diizinkan = ALUR_STATUS[self.__status]
        if status_baru not in diizinkan:
            raise StatusTidakValidError(
                f"Perubahan status dari {self.__status} ke {status_baru} tidak valid."
            )
            
        self.__status = status_baru
        self.__riwayat.append((datetime.now(), status_baru, keterangan))

    def tentukan_prioritas(self) -> str:
        return self.kategori.tentukan_prioritas()

    def ringkasan(self) -> str:
        return (
            f"[{self.id_pengaduan}] {self.fasilitas.nama} - "
            f"Kategori: {self.kategori.nama} | Prioritas: {self.prioritas} | "
            f"Target: {self.target_waktu_hari} hari | Status: {self.status}\n"
            f"Pelapor : {self.pelapor.nama}\n"
            f"Deskripsi: {self.deskripsi}\n"
            f"Tanggal : {self.tanggal_lapor.strftime('%d-%m-%Y %H:%M')}"
        )

    def __str__(self) -> str:
        return self.ringkasan()
