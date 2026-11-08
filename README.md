# Perancangan-Sistem-Pengaduan-dan-Pemeliharaan-Fasilitas-Kampus-Berbasis-Python

Proyek mata kuliah Analisis dan Desain Pemrograman Berorientasi Objek (Python)
Program Studi S1 Sistem Informasi, Fakultas Sains dan Teknologi, Universitas Jambi.

## Deskripsi
Aplikasi berbasis konsol (CLI) untuk mencatat pengaduan kerusakan fasilitas
kampus, mulai dari pelaporan hingga penyelesaian perbaikan. Dibangun dengan
Python menggunakan pendekatan Object-Oriented Programming (OOP) dan prinsip
SOLID (SRP dan OCP).

## Anggota Kelompok 5
| Nama | NIM |
|------|-----|
| Rizki Arvi Passa | F1E125054 |
| Viana Nurlita | F1E125018 |
| Asti Oktapianti | F1E125072 |
| Kayla Inayah | F1E125074 |

Dosen Pengampu: Edi Saputra, S.T., M.Sc.; Pariyadi, S.Kom., M.Kom.;
Hamzah Alghifari, M.Kom.; Muhammad Damas Fatih, S.Kom., M.Kom.

## Fitur
- Pelapor mengajukan pengaduan (fasilitas, kategori, deskripsi)
- Admin memverifikasi/menolak pengaduan dan menugaskan teknisi
- Teknisi memperbarui progres dan menyelesaikan perbaikan
- Prioritas dan target waktu ditentukan otomatis dari kategori
- Notifikasi perubahan status lewat konsol dan berkas log
- Validasi input dan alur status

Alur status: Diajukan → Diverifikasi → Ditugaskan → Dalam Perbaikan → Selesai
(atau Diajukan → Ditolak)

## Struktur File
| File | Keterangan |
|------|-----------|
| main.py | Titik masuk program, menu konsol per peran |
| pengguna.py | Class Pengguna, Pelapor, Admin, Teknisi |
| fasilitas.py | Class Fasilitas |
| kategori.py | KategoriPengaduan dan subclass-nya |
| pengaduan.py | Class Pengaduan dan aturan alur status |
| tugas.py | Class TugasPemeliharaan |
| notifikasi.py | Notifikasi, NotifikasiKonsol, NotifikasiLog |
| layanan.py | LayananPengaduan (koordinator alur) |