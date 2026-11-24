"""Generate the formal Indonesian report from reproducible pipeline metrics."""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


NAVY = "#000000"
TEAL = "#000000"
PALE = "#eef3f8"
INK = "#263445"
LABELS = ["normal", "gores", "noda", "retak", "gelembung", "las_dingin", "kontaminasi"]


def page(title: str, number: int):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(.07, .955, title, fontsize=18, weight="bold", color=NAVY, va="top")
    fig.text(.07, .027, f"Laporan UTS Deep Learning | Halaman {number} dari 9", fontsize=8, color="#64748b")
    return fig


def paragraph(fig, text, x=.08, y=.9, width=104, size=9, color=INK, line=1.25):
    wrapped = "\n".join(textwrap.fill(str(part), width=width) for part in str(text).split("\n"))
    fig.text(x, y, wrapped, fontsize=size, color=color, va="top", linespacing=line)


def table(ax, rows, headers, font=8, scale=1.2):
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=headers, cellLoc="left", colLoc="left", loc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(font)
    t.scale(1, scale)
    for (r, c), cell in t.get_celld().items():
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        elif r % 2 == 0:
            cell.set_facecolor(PALE)
        cell.set_edgecolor("#cbd5e1")
    return t


def _f(x, digits=3):
    if x is None:
        return "n/a"
    return f"{float(x):.{digits}f}"


def _fmt_counts(values):
    return f"{int(values):,}".replace(",", ".")


def write_pdf(metrics: dict, path: Path, artifacts: Path):
    path = Path(path)
    artifacts = Path(artifacts)
    path.parent.mkdir(parents=True, exist_ok=True)
    ov = metrics["data_overview"]
    cls = metrics["classification"]
    rul = metrics["rul"]
    cl = metrics["clustering"]
    with PdfPages(path) as pdf:
        # 1 - Cover and executive summary.
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        fig.text(.08, .94, "LAPORAN UJIAN TENGAH SEMESTER", fontsize=13, color=TEAL, weight="bold", va="top")
        fig.text(.08, .89, "Deep Learning", fontsize=29, color=NAVY, weight="bold", va="top")
        fig.text(.08, .84, "Klasifikasi, Regresi Deret Waktu, dan Clustering Multimodal", fontsize=13, color=INK, va="top")
        fig.text(.08, .76, "Kelompok", fontsize=11, color=TEAL, weight="bold")
        table(fig.add_axes([.08, .63, .84, .10]), [
            ["Nanda Pratama Itma", "101032330212"],
            ["Ezra Daiva Keitaro", "1103223200"],
        ], ["Nama anggota", "NIM"], font=10, scale=1.35)
        fig.text(.08, .56, "Abstrak", fontsize=13, color=NAVY, weight="bold")
        paragraph(fig,
            "Laporan ini membahas tiga pipeline deep learning pada dataset inspeksi produk, riwayat mesin, dan sampel material. "
            "Klasifikasi menggabungkan citra dan sinyal sensor; regresi memperkirakan remaining useful life (RUL); "
            "clustering mengelompokkan sampel tanpa label. Eksperimen membandingkan beberapa arsitektur dan baseline, "
            "mengukur kinerja pada validasi, memeriksa missing modality, serta menyajikan ketidakpastian prediksi RUL. "
            "Label hidden test klasifikasi dan label referensi material tidak disertakan dalam arsip, sehingga skor hidden-test "
            "dan adjusted rand index (ARI) tidak dapat dihitung secara lokal.", x=.08, y=.52, width=100, size=10, line=1.35)
        fig.text(.08, .34, "Ringkasan hasil validasi", fontsize=13, color=NAVY, weight="bold")
        summary = [
            ["Klasifikasi", f"Late fusion macro-F1 = {_f(cls['validation']['late_fusion']['macro_f1'])}"],
            ["RUL", f"Ensemble GRU RMSE = {_f(rul['validation']['gru_ensemble']['rmse'], 2)}"],
            ["Clustering", f"K = {cl['selected_k']}; ARI tidak tersedia"],
        ]
        table(fig.add_axes([.08, .18, .84, .13]), summary, ["Task", "Ringkasan"], font=9, scale=1.25)
        fig.text(.08, .09, "Bahasa: Indonesia | Sumber: arsip data_uts_dl.zip dan kamus_data.md", fontsize=8, color="#64748b")
        pdf.savefig(fig); plt.close(fig)

        # 2 - Data and scope.
        fig = page("1. Data dan ruang lingkup", 2)
        paragraph(fig, "Dataset memuat tiga masalah dengan modalitas, target, dan ketersediaan label yang berbeda. "
                  "Seluruh pemeriksaan berikut dilakukan pada arsip yang diberikan untuk tugas.", y=.89)
        facts = [
            ["Klasifikasi", f"{_fmt_counts(ov['classification']['train_n'])} train + {_fmt_counts(ov['classification']['test_n'])} test", "Citra 64 x 64 dan sinyal 3 x 128"],
            ["RUL", f"{ov['rul']['train_machines']} mesin train + {ov['rul']['test_machines']} mesin test", "Siklus, 3 setting, dan 21 sensor"],
            ["Clustering", f"{_fmt_counts(ov['clustering']['n'])} sampel", "Citra mikroskop dan spektrum 128 nilai"],
        ]
        table(fig.add_axes([.08, .72, .84, .13]), facts, ["Task", "Ukuran data", "Modalitas"], font=8.5)
        counts = ov["classification"]["classes"]
        class_rows = [[k, _fmt_counts(counts.get(k, 0))] for k in LABELS]
        table(fig.add_axes([.10, .38, .46, .28]), class_rows, ["Kelas train", "Jumlah"], font=8, scale=1.05)
        c = ov["classification"]
        line_rows = [["A", f"{100*c['train_line_fraction'].get('A', 0):.2f}%", f"{100*c['test_line_fraction'].get('A', 0):.2f}%"],
                     ["B", f"{100*c['train_line_fraction'].get('B', 0):.2f}%", f"{100*c['test_line_fraction'].get('B', 0):.2f}%"]]
        table(fig.add_axes([.60, .45, .32, .16]), line_rows, ["Lini", "Train", "Test"], font=8, scale=1.2)
        paragraph(fig, f"Sinyal klasifikasi mengandung {100*c['signal_nan_fraction']:.2f}% nilai hilang; "
                  f"{100*c['rows_with_missing_signal_fraction']:.2f}% baris memiliki setidaknya satu nilai hilang dan "
                  f"{_fmt_counts(c['all_signal_missing_rows'])} baris tidak memiliki rekaman sensor sama sekali. "
                  f"Proporsi lini berubah nyata antara train dan test. Distribusi kelas tidak seimbang, sehingga macro-F1 "
                  f"dan hasil per lini digunakan sebagai metrik analisis.", x=.08, y=.27, width=100, size=9)
        paragraph(fig, "Pada data RUL, panjang riwayat antar mesin bervariasi dan sekitar "
                  f"{100*ov['rul']['train_missing_value_fraction']:.2f}% nilai train hilang. Label clustering dan label klasifikasi test disembunyikan.",
                  x=.08, y=.17, width=100, size=9)
        pdf.savefig(fig); plt.close(fig)

        # 3 - Classification method and comparative validation.
        fig = page("2. Task 1 - Klasifikasi cacat multimodal", 3)
        paragraph(fig, "Tujuan task ini adalah menetapkan satu dari tujuh kelas cacat untuk setiap unit. CNN mengekstrak "
                  "pola spasial dari citra, sedangkan 1D-CNN mengekstrak pola temporal dari tiga kanal sinyal. "
                  "Pada early fusion, sinyal disusun sebagai kanal tambahan sebelum encoder citra. Pada late fusion, "
                  "kedua encoder menghasilkan embedding terpisah yang digabung sebelum klasifikasi.", y=.89, width=100)
        val = cls["validation"]
        exp_rows = [[name.replace("_", " "), _f(v["macro_f1"]), _f(v["accuracy"]), _f(v["line_accuracy"].get("A", {}).get("macro_f1")), _f(v["line_accuracy"].get("B", {}).get("macro_f1"))]
                    for name, v in val.items()]
        table(fig.add_axes([.08, .61, .84, .20]), exp_rows,
              ["Eksperimen", "Macro-F1", "Akurasi", "F1 lini A", "F1 lini B"], font=7.3, scale=1.12)
        ax_loss = fig.add_axes([.10, .30, .37, .22])
        ax_f1 = fig.add_axes([.53, .30, .37, .22])
        for name, history in cls["learning_curves"].items():
            epochs = [q["epoch"] for q in history]
            label = name.replace("_", " ")
            ax_loss.plot(epochs, [q["train_loss"] for q in history], marker=".", linewidth=1, label=label)
            ax_f1.plot(epochs, [q["val_macro_f1"] for q in history], marker=".", linewidth=1, label=label)
        ax_loss.set(xlabel="Epoch", ylabel="Loss train")
        ax_f1.set(xlabel="Epoch", ylabel="Macro-F1 validasi", ylim=(0, 1))
        for ax in (ax_loss, ax_f1):
            ax.grid(alpha=.25)
        ax_f1.legend(fontsize=5.8, ncol=2, loc="lower right")
        paragraph(fig, "Kurva menunjukkan loss pada data latih dan Macro-F1 pada data validasi per epoch untuk enam eksperimen. "
                  "Nilai ini berasal dari split validasi yang sama dan dipakai untuk membandingkan proses belajar; "
                  "kurva bukan hasil evaluasi hidden test.", x=.09, y=.265, width=108, size=7.4)
        paragraph(fig, "Late fusion mengungguli model satu modalitas dan early fusion pada split validasi ini. "
                  "Sampling seimbang lini meningkatkan F1 lini B dari "
                  f"{_f(val['late_fusion']['line_accuracy']['B']['macro_f1'])} menjadi "
                  f"{_f(val['line_balanced']['line_accuracy']['B']['macro_f1'])}; "
                  "perubahan itu disertai perubahan trade-off pada akurasi keseluruhan.",
                  x=.08, y=.18, width=108, size=8)
        pdf.savefig(fig); plt.close(fig)

        # 4 - Classification diagnostics and final predictions.
        fig = page("2.1. Diagnostik dan keluaran klasifikasi", 4)
        per_class = []
        for label in LABELS:
            per_class.append([label, _f(val["image"]["per_class_f1"][label]),
                              _f(val["sensor"]["per_class_f1"][label]),
                              _f(val["late_fusion"]["per_class_f1"][label])])
        table(fig.add_axes([.09, .61, .82, .25]), per_class,
              ["Kelas", "Gambar", "Sensor", "Late fusion"], font=7.6, scale=1.12)
        miss = cls["missing_sensor_validation"]
        paragraph(fig, f"Nilai sensor diimputasi setelah standardisasi dan mask ketersediaan ditambahkan sebagai kanal. "
                  f"Macro-F1 untuk {miss['all_missing_rows']} contoh validasi tanpa sensor adalah "
                  f"{_f(miss['all_missing_macro_f1'])}; untuk contoh dengan rekaman sensor adalah "
                  f"{_f(miss['recorded_rows_macro_f1'])}. Model tetap dapat menggunakan citra ketika sinyal tidak tercatat, "
                  "tetapi kinerja kelompok tanpa sensor lebih rendah. Statistik standardisasi validasi dihitung dari bagian train saja.", y=.53, width=105, size=8.5)
        paragraph(fig, f"Label smoothing (0,1) diuji sebagai teknik untuk label yang tidak pasti; macro-F1 berubah dari "
                  f"{_f(val['late_fusion']['macro_f1'])} menjadi {_f(val['label_smoothing']['macro_f1'])}. "
                  f"Sebanyak {len(cls['possible_label_review_cases'])} contoh dengan cross-entropy validasi tertinggi "
                  "ditandai untuk pemeriksaan manusia. Kandidat ini tidak dianggap pasti salah dan tidak diubah otomatis. "
                  f"Sanity check menghafal satu batch setelah {cls['one_batch_overfit_steps']} update dengan akurasi "
                  f"{_f(cls['one_batch_overfit_accuracy'])}; pemeriksaan ini memastikan training dapat belajar dari batch kecil, "
                  "bukan generalisasi.", y=.38, width=105, size=8.5)
        count_rows = [[label, _fmt_counts(cls["final_test_prediction_counts"].get(label, 0))] for label in LABELS]
        table(fig.add_axes([.20, .10, .60, .20]), count_rows, ["Prediksi kelas test", "Jumlah unit"], font=8, scale=1.05)
        paragraph(fig, "Model akhir memakai tiga seed, sampling seimbang lini, bobot kelas, dan label smoothing ringan (0,05). "
                  "Angka pada tabel terakhir adalah jumlah prediksi, bukan jumlah jawaban benar; label test tidak tersedia.",
                  x=.08, y=.07, width=105, size=7.5)
        pdf.savefig(fig); plt.close(fig)

        # 5 - RUL data exploration and design.
        fig = page("3. Task 2 - Regresi remaining useful life", 5)
        r = ov["rul"]
        paragraph(fig, "RUL didefinisikan sebagai jumlah siklus sampai gagal, dibatasi maksimum 150. "
                  "Untuk mesin dengan siklus akhir T dan waktu pengamatan t, targetnya adalah min(150, max(0, T - t)). "
                  "Pelatihan menggunakan jendela 32 siklus; jendela awal yang lebih pendek diberi padding di kiri.", y=.89, width=102)
        sensor_std = r["sensor_std"]
        outliers = r["sensor_robust_outlier_fraction_per_channel"]
        corr = max(((abs(v), sensor, setting, v) for sensor, vals in r["setting_sensor_correlations"].items() for setting, v in vals.items()))
        paragraph(fig, f"Eksplorasi menemukan simpangan baku sensor berkisar {min(sensor_std.values()):.2f}-{max(sensor_std.values()):.2f}; "
                  "tidak ada kanal konstan. Korelasi absolut terbesar antara sensor dan setting adalah "
                  f"{corr[1]} dengan {corr[2]} (r={corr[3]:.2f}). Sensor {max(outliers, key=outliers.get)} memiliki proporsi "
                  f"outlier 3 x IQR tertinggi ({100*max(outliers.values()):.2f}%). Fitur dinormalisasi dengan statistik mesin train; "
                  "nilai hilang diisi mean train dan mask missing ditambahkan.", y=.75, width=102, size=9)
        table(fig.add_axes([.12, .50, .76, .15]), [
            ["GRU", "Dua lapis GRU untuk pola berurutan"],
            ["TCN", "Konvolusi temporal untuk pola lokal"],
            ["HistGradientBoosting", "Baseline klasik dari ringkasan jendela"],
        ], ["Model", "Peran"], font=9, scale=1.2)
        paragraph(fig, "Pemisahan dilakukan berdasarkan mesin: sekitar 80% mesin untuk train, lalu kelompok holdout dipisah "
                  "untuk kalibrasi dan evaluasi. Normalisasi hanya dipelajari dari mesin train. Titik akhir mesin holdout "
                  "dipotong mengikuti panjang riwayat test; fitur sesudah waktu prediksi tidak menjadi input. "
                  "Mesin kalibrasi dan evaluasi tidak tumpang tindih.", y=.40, width=103, size=9)
        paragraph(fig, "Split conformal menggunakan residual mesin kalibrasi untuk membentuk interval prediksi. "
                  "Aturan skor asimetris memberi penalti lebih besar ketika prediksi RUL terlalu tinggi daripada nilai aktual.",
                  x=.08, y=.23, width=105, size=9)
        pdf.savefig(fig); plt.close(fig)

        # 6 - RUL outcomes.
        fig = page("3.1. Hasil validasi dan ketidakpastian RUL", 6)
        rv = rul["validation"]
        models = ["gru", "tcn", "hist_gradient_boosting", "gru_ensemble"]
        overall = [[name.replace("_", " "), _f(rv[name]["rmse"], 2), f"{rv[name]['asymmetric_score']:.1f}"] for name in models]
        table(fig.add_axes([.10, .75, .80, .14]), overall, ["Model", "RMSE", "Skor asimetris"], font=8.5, scale=1.15)
        ranges = []
        for name in models:
            b = rv[name]["by_rul_range"]
            ranges.append([name.replace("_", " "), _f(b.get("0-49", {}).get("rmse"), 1),
                           _f(b.get("50-99", {}).get("rmse"), 1), _f(b.get("100-150", {}).get("rmse"), 1)])
        table(fig.add_axes([.08, .57, .84, .14]), ranges,
              ["Model", "RMSE 0-49", "RMSE 50-99", "RMSE 100-150"], font=7.3, scale=1.1)
        score_ranges = []
        for name in models:
            b = rv[name]["by_rul_range"]
            score_ranges.append([name.replace("_", " "), f"{b.get('0-49', {}).get('asymmetric_score', 0):.0f}",
                                 f"{b.get('50-99', {}).get('asymmetric_score', 0):.0f}",
                                 f"{b.get('100-150', {}).get('asymmetric_score', 0):.0f}"])
        table(fig.add_axes([.08, .39, .84, .14]), score_ranges,
              ["Model", "Score 0-49", "Score 50-99", "Score 100-150"], font=7.3, scale=1.1)
        ax = fig.add_axes([.12, .17, .76, .17])
        for name, history in rul["learning_curves"].items():
            ax.plot([q["epoch"] for q in history], [q["val_rmse"] for q in history], marker=".", linewidth=1, label=name.upper())
        ax.set(xlabel="Epoch", ylabel="RMSE validasi"); ax.grid(alpha=.25); ax.legend(fontsize=8)
        u = rul["uncertainty"]
        paragraph(fig, f"Interval ensemble bertarget cakupan 90% mencapai cakupan validasi "
                  f"{100*u['validation_90pct_interval_coverage']:.1f}% dengan lebar rata-rata {u['mean_interval_width']:.1f} siklus. "
                  "Lebar interval menunjukkan ketidakpastian yang masih cukup besar. GRU memiliki RMSE terendah, "
                  "sedangkan baseline klasik memiliki skor asimetris terendah; kedua metrik dipertahankan dalam pelaporan.",
                  x=.08, y=.095, width=108, size=8)
        pdf.savefig(fig); plt.close(fig)

        # 7 - RUL maintenance implications.
        fig = page("3.2. Implikasi RUL untuk perencanaan servis", 7)
        paragraph(fig, "Model RUL memberi perkiraan siklus tersisa, bukan diagnosis kerusakan atau jadwal servis yang sudah tervalidasi. "
                  "Karena itu, hasil perlu dipakai sebagai pemicu pemeriksaan dan perencanaan, bersama inspeksi teknisi serta "
                  "prosedur keselamatan yang berlaku.", y=.89, width=102, size=10)
        u = rul["uncertainty"]
        paragraph(fig, f"Pada validasi, interval prediksi ensemble dengan target cakupan 90% mencakup {100*u['validation_90pct_interval_coverage']:.1f}% target. "
                  f"Lebar rata-ratanya {u['mean_interval_width']:.1f} siklus, sehingga ketidakpastian masih besar. "
                  "Titik prediksi tunggal tidak cukup untuk menetapkan waktu servis.", y=.73, width=102, size=10)
        fig.text(.10, .61, "Aturan operasional yang disarankan untuk diuji", fontsize=12, weight="bold", color=TEAL, va="top")
        table(fig.add_axes([.10, .38, .80, .18]), [
            ["1. Tetapkan lead time", "Tim pemeliharaan menentukan L: siklus untuk inspeksi, menyiapkan suku cadang, dan melakukan servis."],
            ["2. Pantau batas bawah", "Gunakan batas bawah interval RUL 90% sebagai sinyal konservatif, bukan hanya nilai tengah prediksi."],
            ["3. Jadwalkan pemeriksaan", "Jika batas bawah ≤ L, prioritaskan inspeksi dan rencanakan servis sesuai hasil pemeriksaan teknisi."],
            ["4. Tinjau ulang", "Perbarui prediksi saat data baru masuk; uji aturan ini pada riwayat servis sebelum dipakai operasional."],
        ], ["Langkah", "Penerapan"], font=8, scale=1.25)
        paragraph(fig, "Nilai L tidak ditentukan dalam dataset UTS. Kelompok tidak menetapkan ambang siklus tertentu karena arsip tidak memuat "
                  "lead time, biaya kegagalan, atau catatan keputusan servis. Aturan ini merupakan usulan interpretasi hasil model, "
                  "bukan kebijakan pemeliharaan yang telah diuji.", x=.08, y=.27, width=103, size=9)
        pdf.savefig(fig); plt.close(fig)

        # 8 - Clustering.
        fig = page("4. Task 3 - Clustering material multimodal", 8)
        paragraph(fig, "Autoencoder mempelajari embedding citra mikroskop dan spektrum secara terpisah. "
                  "Augmentasi yang digunakan adalah flip horizontal/vertikal untuk citra dan pergeseran kecil serta noise "
                  "untuk spektrum. Kedua embedding dinormalisasi dan digabungkan. K-means menjadi pembanding klasik dan "
                  "DEC menjadi metode deep clustering.", y=.89, width=102)
        crit = [[q["k"], _f(q["silhouette"]), _f(q["davies_bouldin"])] for q in cl["k_criteria"]]
        table(fig.add_axes([.09, .61, .46, .22]), crit, ["K", "Silhouette", "Davies-Bouldin"], font=7.3, scale=1.05)
        comparisons = [["Gambar saja", _f(cl["image_only_silhouette"])],
                       ["Spektrum saja", _f(cl["spectrum_only_silhouette"])],
                       ["Gabungan K-means", _f(cl["kmeans_silhouette"])],
                       ["Gabungan DEC", _f(cl["dec_silhouette"])]]
        table(fig.add_axes([.59, .65, .33, .17]), comparisons, ["Metode", "Silhouette"], font=7.2, scale=1.1)
        img = plt.imread(artifacts / "cluster_tsne.png")
        ax = fig.add_axes([.13, .22, .74, .34]); ax.imshow(img); ax.axis("off")
        paragraph(fig, f"K terpilih adalah {cl['selected_k']} berdasarkan silhouette tertinggi dan Davies-Bouldin terendah "
                  "pada rentang K yang diuji. Silhouette gabungan yang rendah menunjukkan pemisahan representasi masih "
                  "lemah; t-SNE memperlihatkan area antarkelompok yang berdekatan. Silhouette internal tidak membuktikan "
                  "jumlah jenis material sebenarnya. ARI tidak dapat dihitung karena label referensi tidak dibagikan; "
                  "ID mikroskop bukan label material.", x=.08, y=.15, width=104, size=8.5)
        pdf.savefig(fig); plt.close(fig)

        # 9 - Conclusions and reproducibility.
        fig = page("5. Kesimpulan, batasan, dan reproduksibilitas", 9)
        paragraph(fig, "Pada klasifikasi, late fusion memberi macro-F1 validasi tertinggi di antara model fusion utama; "
                  "sensor hilang menurunkan kinerja dan pergeseran proporsi lini menuntut evaluasi per lini. "
                  "Pada RUL, GRU memberi RMSE terbaik, tetapi baseline klasik memberi skor asimetris lebih baik. "
                  "Pada clustering, K=2 dipilih secara internal, namun kualitas embedding gabungan terbatas dan ARI tidak tersedia.", y=.89, width=102)
        paragraph(fig, "Batas evaluasi: label klasifikasi test serta label referensi material tidak ada di arsip lokal. "
                  "Dengan demikian, laporan ini tidak mengklaim skor macro-F1 hidden test atau ARI. Hasil RUL adalah validasi "
                  "pada mesin holdout dengan endpoint yang disesuaikan terhadap distribusi panjang riwayat test.",
                  x=.08, y=.75, width=102, size=9)
        paragraph(fig, "Reproduksi penuh dilakukan dari root repository dengan perintah berikut:", x=.08, y=.64, width=100, size=9)
        fig.text(.10, .60, 'python -m kode.pipeline --data "D:\\Kuliah\\DL\\uts\\data_uts_dl.zip"',
                 fontsize=9, family="monospace", color=NAVY, va="top")
        paragraph(fig, "Notebook utama untuk menjalankan ulang proyek adalah notebooks/uts_deep_learning.ipynb di Google Colab. "
                  "Unggah notebook, pilih GPU bila tersedia, unggah ZIP source ketika diminta, izinkan akses ke Google Drive "
                  "yang berisi data_uts_dl.zip, lalu pilih Runtime > Run all. Hasil notebook disimpan di "
                  "MyDrive/uts_dl_colab/hasil_uts_dl. Dataset tidak disertakan di repository. Versi pustaka dan seed "
                  f"dicatat di artifacts/metrics.json. Seed klasifikasi: {cls['final_seeds']}; seed RUL: {rul['final_seeds']}; "
                  "seed clustering: 7. Bobot model final disertakan di artifacts/models/.", x=.08, y=.54, width=104, size=9)
        versions = metrics["runtime"]
        version_rows = [["Python", versions["python"]], ["PyTorch", versions["torch"]],
                        ["NumPy", versions["numpy"]], ["pandas", versions["pandas"]],
                        ["scikit-learn", versions["scikit_learn"]], ["Matplotlib", versions["matplotlib"]]]
        table(fig.add_axes([.15, .24, .70, .24]), version_rows, ["Pustaka", "Versi saat run"], font=8, scale=1.1)
        paragraph(fig, "Berkas submission: laporan.pdf, folder kode/, prediksi_klasifikasi.csv, prediksi_rul.csv, "
                  "cluster.csv, dan kontribusi.md. Rincian peran anggota, tautan PR, dan persetujuan penggunaan AI "
                  "dicatat pada kontribusi.md; pastikan semua bagian itu telah dikonfirmasi sebelum pengumpulan.",
                  x=.08, y=.16, width=104, size=8.5)
        pdf.savefig(fig); plt.close(fig)

    return path
