from abc import ABC, abstractmethod

class KategoriPengaduan(ABC):
    def __init__(self, nama: str):
        self.nama = nama

    @abstractmethod
    def tentukan_prioritas(self) -> str:
        pass

    @abstractmethod
    def target_waktu_hari(self) -> int:
        pass

    def __str__(self) -> str:
        return self.nama

