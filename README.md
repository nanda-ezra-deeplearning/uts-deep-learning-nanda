# UTS Deep Learning — Google Colab

Repository ini berisi berkas pengumpulan UTS kelompok. Dataset tetap berada di Google Drive dan tidak disertakan di repository.

## Menjalankan ulang di Google Colab

1. Unggah `notebooks/uts_deep_learning.ipynb` ke Google Colab.
2. Pilih **Runtime → Change runtime type** dan aktifkan GPU bila tersedia.
3. Saat diminta, unggah `uts_dl_solution_colab_source.zip` dan izinkan akses ke Google Drive yang berisi `data_uts_dl.zip`.
4. Pilih **Runtime → Run all** untuk melatih ketiga task dan membuat ulang metrik, laporan, grafik, model, dan CSV. Hasil disimpan di `MyDrive/uts_dl_colab/hasil_uts_dl`.

## Reproduksi lokal

Dari root repository, dengan paket pada `kode/requirements.txt` terpasang dan dataset tersedia, satu perintah ini melatih ketiga task serta menghasilkan metrik, model, laporan, dan CSV:

```bash
python -m kode.pipeline --data "path/to/data_uts_dl.zip" --out "path/to/hasil"
```

Detail alur Colab, paket, dan opsi lokal tersedia di `kode/README.md`.

## Komponen wajib pada branch `main`

- `laporan.pdf` — 9 halaman; batas UTS 18 halaman.
- `kode/` — source code, `requirements.txt`, dan README.
- `prediksi_klasifikasi.csv` — header `id_unit,kelas`.
- `prediksi_rul.csv` — header `id_unit,rul`.
- `cluster.csv` — header `id_sampel,cluster`.
- `kontribusi.md` — peran anggota, tautan PR, dan penggunaan serta persetujuan AI.

Notebook, `artifacts/` (termasuk bobot model), laporan Word, dan ZIP source disertakan sebagai bahan pendukung. Jangan unggah arsip dataset. Label hidden test klasifikasi dan label referensi material tidak tersedia bagi kelompok; skor hidden-test dan ARI dinilai oleh pengajar.
