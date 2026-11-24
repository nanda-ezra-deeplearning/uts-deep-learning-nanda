# Kontribusi Anggota dan Penggunaan AI

Dokumen ini merangkum kontribusi yang tercatat di repository dan bantuan AI yang digunakan. Setiap anggota bertanggung jawab memahami kode, hasil, dan laporan yang dikumpulkan.

## Identitas, kontribusi, dan pull request

| Anggota | NIM | Akun GitHub | Kontribusi yang tercatat | Pull request ke repository kelompok |
|---|---:|---|---|---|
| Nanda Pratama Itma | 101032330212 | `nandapratama823` | Menyiapkan repository kelompok dan alur Google Colab; mengunggah notebook, kode, CSV hasil, dan laporan; memperbarui kontribusi serta laporan, termasuk kurva pembelajaran klasifikasi dan pembahasan implikasi RUL untuk perencanaan servis; serta mengirim undangan organisasi kepada Ezra. | [PR #2](https://github.com/nanda-ezra-deeplearning/uts-deep-learning-nanda/pull/2) dan [PR #3](https://github.com/nanda-ezra-deeplearning/uts-deep-learning-nanda/pull/3) — **keduanya merged**. Keduanya dibuat dari branch repository organisasi, bukan fork pribadi Nanda. |
| Ezra Daiva Keitaro | 1103223200 | `ezradaiva` | Meninjau notebook dan laporan, memeriksa format file hasil, serta menyampaikan usulan perbaikan. | [PR #1](https://github.com/nanda-ezra-deeplearning/uts-deep-learning-nanda/pull/1) — **merged** dari fork Ezra. |

## Penggunaan AI

- **Alat:** OpenAI Codex.
- **Bagian yang dibantu:** membaca instruksi UTS dan datasheet; membantu menyusun pipeline PyTorch untuk klasifikasi multimodal, prediksi Remaining Useful Life (RUL), dan clustering; menyiapkan notebook Colab; serta membantu menyusun README, analisis hasil, dan draf laporan.
- **Pemeriksaan yang tercatat:** memeriksa struktur dan statistik data, nama kolom dan jumlah baris CSV prediksi, serta konsistensi metrik yang tersedia dengan laporan. Pemeriksaan format dan jumlah baris tidak membuktikan skor hidden test.
- **Batas evaluasi:** label hidden test klasifikasi dan label acuan material tidak tersedia dalam arsip yang diperiksa. Karena itu, macro-F1 hidden test dan ARI tidak dapat dihitung oleh kelompok.
- **Tanggung jawab kelompok:** anggota meninjau hasil, memahami metode, dan mampu menjelaskan proyek saat ujian lisan.

## Persetujuan penggunaan AI

Status dan tanggal berikut dicatat untuk masing-masing anggota. Setiap anggota menyatakan persetujuannya sendiri.

| Anggota | Persetujuan penggunaan AI | Tanggal |
|---|---|---|
| Nanda Pratama Itma (101032330212) | Setuju | 20-11-2026 |
| Ezra Daiva Keitaro (1103223200) | Setuju | 20-11-2026 |

## Status pengumpulan

- Berkas utama yang dipersyaratkan tersedia di branch `main`: `laporan.pdf`, folder `kode/`, tiga CSV prediksi, dan `kontribusi.md`.
- PR Ezra #1 serta PR Nanda #2 dan #3 sudah **merged**.
- **Syarat fork individual Nanda belum terpenuhi secara literal:** PR #2 dan #3 berasal dari branch repository organisasi, bukan fork pribadi. Repository kelompok merupakan fork dari repository pribadi Nanda sehingga GitHub membatasi fork dalam jaringan tersebut. Pengecualian dosen diperlukan; persetujuan dosen belum dicatat di sini.
- Jalankan notebook dengan dataset kelompok dan cocokkan hasilnya dengan laporan. Nilai macro-F1 hidden test dan ARI hanya dapat dinilai pengajar yang memiliki label acuan.
