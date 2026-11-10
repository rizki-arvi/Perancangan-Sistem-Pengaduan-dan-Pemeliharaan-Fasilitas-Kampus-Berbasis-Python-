"""Kanal notifikasi perubahan status pengaduan."""
from abc import ABC, abstractmethod
from datetime import datetime


class Notifikasi(ABC):
    @abstractmethod
    def kirim(self, penerima, pesan):
        pass

    @staticmethod
    def _siapkan(penerima, pesan):
        nama = str(getattr(penerima, "nama", penerima) or "").strip()
        isi = str(pesan or "").strip()
        if not nama:
            raise ValueError("Penerima notifikasi tidak boleh kosong.")
        if not isi:
            raise ValueError("Pesan notifikasi tidak boleh kosong.")
        return nama, isi


class NotifikasiKonsol(Notifikasi):
    def kirim(self, penerima, pesan):
        nama, isi = self._siapkan(penerima, pesan)
        print(f"[NOTIFIKASI] Kepada {nama}: {isi}")


class NotifikasiLog(Notifikasi):
    def __init__(self, path_berkas="notifikasi.log"):
        self._path_berkas = path_berkas

    @property
    def path_berkas(self):
        return self._path_berkas

    def kirim(self, penerima, pesan):
        nama, isi = self._siapkan(penerima, pesan)
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self._path_berkas, "a", encoding="utf-8") as berkas:
            berkas.write(f"{waktu} | {nama} | {isi}\n")
