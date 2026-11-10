def _validasi_teks(nilai, nama_field):
    if not isinstance(nilai, str) or not nilai.strip():
        raise ValueError(f"{nama_field} tidak boleh kosong.")
    return nilai.strip()

class Fasilitas:
    KONDISI_VALID = ("Baik", "Rusak Ringan", "Rusak Berat", "Dalam Perbaikan")

    def __init__(self, id_fasilitas, nama, lokasi, kondisi="Baik"):
        self._id_fasilitas = _validasi_teks(id_fasilitas, "ID fasilitas")
        self._nama = _validasi_teks(nama, "Nama fasilitas")
        self._lokasi = _validasi_teks(lokasi, "Lokasi fasilitas")
        self._kondisi = self._validasi_kondisi(kondisi)

    @classmethod
    def _validasi_kondisi(cls, kondisi):
        if isinstance(kondisi, str):
            for valid in cls.KONDISI_VALID:
                if kondisi.strip().lower() == valid.lower():
                    return valid
        raise ValueError(
            f"Kondisi '{kondisi}' tidak valid. "
            f"Pilihan: {', '.join(cls.KONDISI_VALID)}."
        )

    @property
    def id_fasilitas(self):
        return self._id_fasilitas

    @property
    def nama(self):
        return self._nama

    @property
    def lokasi(self):
        return self._lokasi

    @property
    def kondisi(self):
        return self._kondisi

    def perbarui_kondisi(self, kondisi_baru):
        """Memperbarui kondisi fasilitas setelah divalidasi."""
        self._kondisi = self._validasi_kondisi(kondisi_baru)

    def __str__(self):
        return f"[{self._id_fasilitas}] {self._nama} - {self._lokasi} (Kondisi: {self._kondisi})"
