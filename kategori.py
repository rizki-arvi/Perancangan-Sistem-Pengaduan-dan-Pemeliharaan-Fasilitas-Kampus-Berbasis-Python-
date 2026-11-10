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

class KategoriListrik(KategoriPengaduan):
    def __init__(self):
        super().__init__("Listrik")

    def tentukan_prioritas(self) -> str:
        return "Tinggi"

    def target_waktu_hari(self) -> int:
        return 1

class KategoriSanitasi(KategoriPengaduan):
    def __init__(self):
        super().__init__("Sanitasi")

    def tentukan_prioritas(self) -> str:
        return "Tinggi"

    def target_waktu_hari(self) -> int:
        return 2

class KategoriJaringan(KategoriPengaduan):
    def __init__(self):
        super().__init__("Jaringan")

    def tentukan_prioritas(self) -> str:
        return "Sedang"

    def target_waktu_hari(self) -> int:
        return 3

class KategoriFurnitur(KategoriPengaduan):
    def __init__(self):
        super().__init__("Furnitur")

    def tentukan_prioritas(self) -> str:
        return "Rendah"

    def target_waktu_hari(self) -> int:
        return 7
