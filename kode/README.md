# Kode pipeline UTS Deep Learning

## Reproduksi penuh dengan satu perintah

Jalankan dari root repository setelah memasang dependensi pada `requirements.txt` dan menyiapkan arsip dataset:

```bash
python -m kode.pipeline --data "path/to/data_uts_dl.zip" --out "path/to/hasil"
```

Perintah ini melatih ketiga task dengan seed klasifikasi dan RUL `7, 21, 42` (serta seed clustering `7`), lalu menyimpan metrik, grafik, bobot model, laporan PDF dan Word, dan tiga CSV prediksi pada folder output. Opsi jumlah epoch tersedia di `python -m kode.pipeline --help`.

## Alur Google Colab

Notebook utama adalah `notebooks/uts_deep_learning.ipynb`. Unggah notebook ke Colab, unggah `uts_dl_solution_colab_source.zip` ketika diminta, izinkan akses Drive, pastikan `data_uts_dl.zip` tersedia pada folder data kelompok, lalu pilih **Runtime → Run all**. Hasil disimpan ke `MyDrive/uts_dl_colab/hasil_uts_dl`.

## Isi folder

Folder ini berisi pipeline untuk tiga task, audit dataset, pelaporan, requirements, dan skrip pemeriksaan reproduksi ensemble klasifikasi. `kode.reproduce` hanya memeriksa ulang prediksi ensemble klasifikasi dari bobot yang tersimpan; gunakan `kode.pipeline` untuk mereproduksi seluruh metrik dalam laporan.

Dataset tidak disertakan di ZIP source atau GitHub. Label test klasifikasi dan label referensi material tidak tersedia bagi kelompok, sehingga hidden-test macro-F1 dan ARI hanya dapat dinilai oleh pengajar.
