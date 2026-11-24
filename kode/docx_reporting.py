"""Create an editable formal DOCX report from the pipeline's metrics."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


NAVY = "000000"
TEAL = "000000"
PALE = "EEF3F8"
INK = "263445"
LABELS = ["normal", "gores", "noda", "retak", "gelembung", "las_dingin", "kontaminasi"]


def _set_cell(cell, value, *, header=False, shade=None):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor
    cell.text = str(value)
    for p in cell.paragraphs:
        p.paragraph_format.space_after = Pt(1)
        for run in p.runs:
            run.font.name = "Aptos"
            run.font.size = Pt(8.5)
            run.bold = header
            if header:
                run.font.color.rgb = RGBColor(255, 255, 255)
    if shade:
        tc_pr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), shade)
        tc_pr.append(shd)


def _table(doc, headers, rows):
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.shared import Pt
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for j, h in enumerate(headers):
        _set_cell(t.rows[0].cells[j], h, header=True, shade=NAVY)
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for j, val in enumerate(row):
            _set_cell(cells[j], val, shade=PALE if i % 2 else None)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t


def _para(doc, text, bold_prefix=None):
    from docx.shared import Pt, RGBColor
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.1
    if bold_prefix and str(text).startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(str(text)[len(bold_prefix):])
    else:
        p.add_run(str(text))
    for r in p.runs:
        r.font.name = "Aptos"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor.from_string(INK)
    return p


def _heading(doc, text, level=1):
    from docx.shared import Pt, RGBColor
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.name = "Aptos Display"
        r.font.color.rgb = RGBColor.from_string(NAVY if level == 1 else TEAL)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    return p


def _add_page_number(paragraph):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    run = paragraph.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)


def _count(n):
    return f"{int(n):,}".replace(",", ".")


def _f(x, digits=3):
    return "n/a" if x is None else f"{float(x):.{digits}f}"


def _figure(doc, path, width=6.25, caption=None):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor
    path = Path(path)
    if not path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(width))
    if caption:
        cp = doc.add_paragraph(caption)
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(5)
        for r in cp.runs:
            r.italic = True
            r.font.size = Pt(8)
            r.font.color.rgb = RGBColor.from_string("64748B")


def write_docx(metrics: dict, path: Path, artifacts: Path):
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    path = Path(path)
    artifacts = Path(artifacts)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(.7)
    sec.bottom_margin = Inches(.65)
    sec.left_margin = Inches(.78)
    sec.right_margin = Inches(.78)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(INK)
    for style_name, size, color in [("Title", 26, NAVY), ("Heading 1", 17, NAVY), ("Heading 2", 12, TEAL)]:
        st = doc.styles[style_name]
        st.font.name = "Aptos Display"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(color)

    # Header and footer.
    hp = sec.header.paragraphs[0]
    hp.text = "UTS Deep Learning | Laporan Kelompok"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in hp.runs:
        r.font.name = "Aptos"; r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string("64748B")
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = fp.add_run("Laporan UTS Deep Learning | Halaman ")
    rr.font.size = Pt(8); rr.font.color.rgb = RGBColor.from_string("64748B")
    _add_page_number(fp)

    ov = metrics["data_overview"]
    cls = metrics["classification"]
    rul = metrics["rul"]
    cl = metrics["clustering"]

    # Cover and abstract.
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(60)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LAPORAN UJIAN TENGAH SEMESTER")
    r.bold = True; r.font.size = Pt(14); r.font.color.rgb = RGBColor.from_string(TEAL)
    p = doc.add_paragraph(style="Title"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Deep Learning")
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Klasifikasi, Regresi Deret Waktu, dan Clustering Multimodal")
    r.font.size = Pt(13); r.font.color.rgb = RGBColor.from_string(INK)
    doc.add_paragraph()
    _heading(doc, "Anggota Kelompok", 2)
    _table(doc, ["Nama", "NIM"], [["Nanda Pratama Itma", "101032330212"], ["Ezra Daiva Keitaro", "1103223200"]])
    _heading(doc, "Abstrak", 2)
    _para(doc, "Laporan ini membahas tiga pipeline deep learning pada dataset inspeksi produk, riwayat mesin, dan sampel material. Klasifikasi menggabungkan citra dan sinyal sensor; regresi memperkirakan remaining useful life (RUL); clustering mengelompokkan sampel tanpa label. Eksperimen membandingkan beberapa arsitektur dan baseline, mengukur kinerja pada validasi, memeriksa missing modality, serta menyajikan ketidakpastian prediksi RUL. Label hidden test klasifikasi dan label referensi material tidak disertakan dalam arsip, sehingga skor hidden-test dan adjusted rand index (ARI) tidak dapat dihitung secara lokal.")
    _heading(doc, "Ringkasan Hasil Validasi", 2)
    _table(doc, ["Task", "Hasil utama"], [
        ["Klasifikasi", f"Late fusion macro-F1 = {_f(cls['validation']['late_fusion']['macro_f1'])}"],
        ["RUL", f"Ensemble GRU RMSE = {_f(rul['validation']['gru_ensemble']['rmse'],2)}"],
        ["Clustering", f"K = {cl['selected_k']}; ARI tidak tersedia tanpa label acuan"],
    ])
    _para(doc, "Sumber data: arsip data_uts_dl.zip dan kamus_data.md yang diberikan untuk tugas.")

    # Dataset and exploration.
    doc.add_page_break()
    _heading(doc, "1. Data dan Ruang Lingkup", 1)
    _para(doc, "Dataset memuat tiga masalah dengan modalitas, target, dan ketersediaan label yang berbeda. Seluruh analisis menggunakan arsip yang diberikan untuk UTS.")
    _table(doc, ["Task", "Ukuran data", "Modalitas"], [
        ["Klasifikasi", f"{_count(ov['classification']['train_n'])} train + {_count(ov['classification']['test_n'])} test", "Citra 64 x 64 dan sinyal 3 x 128"],
        ["RUL", f"{ov['rul']['train_machines']} mesin train + {ov['rul']['test_machines']} mesin test", "Siklus, 3 setting, 21 sensor"],
        ["Clustering", f"{_count(ov['clustering']['n'])} sampel", "Citra mikroskop dan spektrum 128 nilai"],
    ])
    _heading(doc, "Distribusi Kelas dan Pergeseran Lini", 2)
    counts = ov["classification"]["classes"]
    _table(doc, ["Kelas train", "Jumlah"], [[k, _count(counts.get(k,0))] for k in LABELS])
    c = ov["classification"]
    _table(doc, ["Lini", "Porsi train", "Porsi test"], [
        [line, f"{100*c['train_line_fraction'].get(line,0):.2f}%", f"{100*c['test_line_fraction'].get(line,0):.2f}%"]
        for line in ["A", "B"]
    ])
    _para(doc, f"Sinyal klasifikasi memiliki {100*c['signal_nan_fraction']:.2f}% nilai hilang; {100*c['rows_with_missing_signal_fraction']:.2f}% baris memiliki setidaknya satu nilai hilang dan {_count(c['all_signal_missing_rows'])} baris tidak memiliki rekaman sensor sama sekali. Perubahan porsi lini dan distribusi kelas menjadi alasan evaluasi macro-F1 serta hasil per lini.")
    _figure(doc, artifacts / "eda_class_distribution.png", width=5.6, caption="Gambar 1. Distribusi kelas pada data train klasifikasi.")
    _para(doc, f"Data RUL memiliki {rul['validation']['gru_ensemble']['by_rul_range']['0-49']['n'] + rul['validation']['gru_ensemble']['by_rul_range']['50-99']['n'] + rul['validation']['gru_ensemble']['by_rul_range']['100-150']['n']} mesin pada kelompok evaluasi validasi. Nilai sensor hilang pada data train sebesar {100*ov['rul']['train_missing_value_fraction']:.2f}%. Label klasifikasi test dan label material clustering disembunyikan.")

    # Task 1 methods and results.
    doc.add_page_break()
    _heading(doc, "2. Task 1 - Klasifikasi Cacat Multimodal", 1)
    _heading(doc, "2.1 Tujuan dan Metode", 2)
    _para(doc, "Tujuan task ini adalah menetapkan satu dari tujuh kelas cacat untuk setiap unit. CNN mengekstrak pola spasial dari citra, sedangkan 1D-CNN mengekstrak pola temporal dari tiga kanal sinyal. Early fusion menggabungkan sinyal sebagai kanal tambahan sebelum encoder. Late fusion memproses citra dan sensor secara terpisah, lalu menggabungkan embedding sebelum klasifikasi.")
    _para(doc, "Sinyal dinormalisasi per kanal. Nilai NaN diisi nol setelah standardisasi dan mask missing ditambahkan sebagai kanal. Pada validasi, statistik normalisasi dihitung hanya dari bagian train. Untuk model final, statistik dihitung ulang memakai seluruh data train berlabel.")
    val = cls["validation"]
    _heading(doc, "2.2 Perbandingan Eksperimen", 2)
    _table(doc, ["Eksperimen", "Macro-F1", "Akurasi", "F1 lini A", "F1 lini B"], [
        [name.replace("_", " "), _f(v["macro_f1"]), _f(v["accuracy"]),
         _f(v["line_accuracy"].get("A",{}).get("macro_f1")), _f(v["line_accuracy"].get("B",{}).get("macro_f1"))]
        for name,v in val.items()
    ])
    _figure(doc, artifacts / "eda_class_examples.png", width=6.2, caption="Gambar 2. Contoh citra dan sinyal sensor untuk tiap kelas train.")
    _para(doc, f"Late fusion memperoleh macro-F1 {_f(val['late_fusion']['macro_f1'])}. Sampling seimbang lini memperoleh macro-F1 {_f(val['line_balanced']['macro_f1'])}; F1 lini B berubah dari {_f(val['late_fusion']['line_accuracy']['B']['macro_f1'])} menjadi {_f(val['line_balanced']['line_accuracy']['B']['macro_f1'])}. Label smoothing 0,1 menghasilkan macro-F1 {_f(val['label_smoothing']['macro_f1'])}, sehingga tidak meningkatkan nilai agregat pada split ini.")
    doc.add_page_break()
    fig, (ax_loss, ax_f1) = plt.subplots(1, 2, figsize=(10, 3.8))
    for name, history in cls["learning_curves"].items():
        epochs = [q["epoch"] for q in history]
        label = name.replace("_", " ")
        ax_loss.plot(epochs, [q["train_loss"] for q in history], marker=".", linewidth=1.4, label=label)
        ax_f1.plot(epochs, [q["val_macro_f1"] for q in history], marker=".", linewidth=1.4, label=label)
    ax_loss.set(title="Loss pelatihan", xlabel="Epoch", ylabel="Loss")
    ax_f1.set(title="Macro-F1 validasi", xlabel="Epoch", ylabel="Macro-F1", ylim=(0, 1))
    for ax in (ax_loss, ax_f1):
        ax.grid(alpha=.25)
        ax.set_xticks(range(1, 11))
    ax_f1.legend(fontsize=7, ncol=2, loc="lower right")
    fig.suptitle("Kurva pembelajaran klasifikasi", fontsize=13)
    fig.tight_layout()
    curve_path = artifacts / "classification_learning_curves.png"
    fig.savefig(curve_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    _figure(doc, curve_path, width=6.25, caption="Gambar 3. Loss train dan Macro-F1 validasi per epoch pada enam eksperimen klasifikasi.")
    _para(doc, "Kurva berasal dari log eksperimen pada split validasi yang sama. Kurva digunakan untuk melihat perubahan selama pelatihan dan membandingkan eksperimen; hasilnya bukan skor hidden test.")

    doc.add_page_break()
    _heading(doc, "2.3 Analisis Kesalahan dan Prediksi", 2)
    _table(doc, ["Kelas", "Gambar saja", "Sensor saja", "Late fusion"], [
        [label, _f(val["image"]["per_class_f1"][label]), _f(val["sensor"]["per_class_f1"][label]), _f(val["late_fusion"]["per_class_f1"][label])]
        for label in LABELS
    ])
    miss = cls["missing_sensor_validation"]
    _para(doc, f"Untuk {miss['all_missing_rows']} contoh validasi tanpa sensor, macro-F1 adalah {_f(miss['all_missing_macro_f1'])}; untuk contoh dengan sensor tercatat macro-F1 adalah {_f(miss['recorded_rows_macro_f1'])}. Model tetap dapat membuat prediksi dari citra ketika sensor tidak tersedia, tetapi hasil pada kelompok tanpa sensor lebih rendah.")
    _para(doc, f"Sebanyak {len(cls['possible_label_review_cases'])} contoh dengan cross-entropy validasi tertinggi ditandai sebagai kandidat pemeriksaan manual. Kandidat tersebut bukan bukti label salah dan tidak diubah otomatis. Sanity check menghafal satu batch 64 contoh setelah {cls['one_batch_overfit_steps']} update dengan akurasi {_f(cls['one_batch_overfit_accuracy'])}; ini memeriksa jalur training, bukan generalisasi.")
    _para(doc, "Model final menggunakan late fusion dengan sampling seimbang lini, bobot kelas, label smoothing 0,05, dan tiga seed. Logit dari tiga model dirata-ratakan untuk prediksi test.")
    _table(doc, ["Kelas prediksi test", "Jumlah unit"], [[label, _count(cls["final_test_prediction_counts"].get(label,0))] for label in LABELS])
    _para(doc, "Tabel tersebut menunjukkan jumlah tebakan pada test, bukan jumlah jawaban benar. Label test tidak tersedia bagi kelompok.")

    # Task 2.
    doc.add_page_break()
    _heading(doc, "3. Task 2 - Regresi Remaining Useful Life", 1)
    _heading(doc, "3.1 Label dan Pra-pemrosesan", 2)
    _para(doc, "RUL didefinisikan sebagai jumlah siklus tersisa sampai mesin gagal, dibatasi maksimal 150. Untuk siklus akhir T dan waktu pengamatan t, targetnya min(150, max(0, T - t)). Input dibentuk sebagai jendela 32 siklus; jendela yang pendek dipadding di kiri.")
    r = ov["rul"]
    outliers = r["sensor_robust_outlier_fraction_per_channel"]
    corr = max(((abs(v), sensor, setting, v) for sensor, vals in r["setting_sensor_correlations"].items() for setting,v in vals.items()))
    _para(doc, f"Eksplorasi menunjukkan simpangan baku sensor berkisar {min(r['sensor_std'].values()):.2f}-{max(r['sensor_std'].values()):.2f}; tidak ada kanal konstan. Korelasi absolut terbesar antara sensor dan setting adalah {corr[1]} dengan {corr[2]} (r={corr[3]:.2f}). Sensor {max(outliers,key=outliers.get)} memiliki outlier 3 x IQR terbanyak ({100*max(outliers.values()):.2f}%). Fitur dinormalisasi memakai mean dan standar deviasi mesin train; nilai hilang diisi mean train dan indikator missing ditambahkan.")
    _heading(doc, "3.2 Model dan Validasi", 2)
    _table(doc, ["Model", "Peran"], [
        ["GRU", "Model deep learning untuk pola urutan kondisi mesin."],
        ["TCN", "Model deep learning berbasis konvolusi temporal."],
        ["HistGradientBoosting", "Baseline klasik dari ringkasan jendela."],
    ])
    _para(doc, "Pemisahan dilakukan per mesin: 80% mesin untuk train, sementara holdout dibagi menjadi kelompok kalibrasi dan evaluasi. Normalisasi dihitung hanya dari mesin train. Titik akhir riwayat holdout dipotong mengikuti panjang riwayat mesin test; fitur setelah titik prediksi tidak masuk ke input. Kalibrasi dan evaluasi menggunakan mesin yang berbeda.")

    doc.add_page_break()
    _heading(doc, "3.3 Hasil dan Ketidakpastian RUL", 2)
    rv = rul["validation"]
    models = ["gru", "tcn", "hist_gradient_boosting", "gru_ensemble"]
    _table(doc, ["Model", "RMSE", "Skor asimetris"], [
        [name.replace("_", " "), _f(rv[name]["rmse"],2), f"{rv[name]['asymmetric_score']:.1f}"] for name in models
    ])
    _para(doc, "RMSE mengukur besar selisih prediksi dan target; nilai lebih kecil lebih baik. Skor asimetris menghukum lebih berat prediksi yang terlalu optimistis, yaitu saat prediksi RUL melebihi nilai aktual. Ensemble GRU memberi RMSE terendah pada tabel, sementara baseline klasik memperoleh skor asimetris terendah. Kedua hasil dilaporkan apa adanya.")
    _heading(doc, "Evaluasi Berdasarkan Rentang RUL", 2)
    ranges = []
    for name in models:
        b = rv[name]["by_rul_range"]
        ranges.append([name.replace("_", " "), _f(b.get("0-49",{}).get("rmse"),1), _f(b.get("50-99",{}).get("rmse"),1), _f(b.get("100-150",{}).get("rmse"),1),
                       f"{b.get('0-49',{}).get('asymmetric_score',0):.0f}", f"{b.get('50-99',{}).get('asymmetric_score',0):.0f}", f"{b.get('100-150',{}).get('asymmetric_score',0):.0f}"])
    _table(doc, ["Model", "RMSE 0-49", "50-99", "100-150", "Skor 0-49", "50-99", "100-150"], ranges)
    _para(doc, f"Interval ensemble bertarget cakupan 90% mencapai cakupan validasi {100*rul['uncertainty']['validation_90pct_interval_coverage']:.1f}% dan lebar rata-rata {rul['uncertainty']['mean_interval_width']:.1f} siklus. Lebar ini menunjukkan ketidakpastian prediksi masih cukup besar.")
    _heading(doc, "Implikasi untuk perencanaan servis", 2)
    _para(doc, "RUL merupakan perkiraan sisa siklus, bukan diagnosis kerusakan atau jadwal servis yang sudah tervalidasi. Gunakan batas bawah interval prediksi 90% sebagai sinyal konservatif untuk memicu pemeriksaan, bukan hanya nilai tengah prediksi. Tim pemeliharaan perlu menetapkan lead time L berdasarkan waktu inspeksi, persiapan suku cadang, dan pelaksanaan servis. Jika batas bawah interval RUL mencapai atau berada di bawah L, prioritaskan inspeksi dan rencanakan servis sesuai temuan teknisi.")
    _para(doc, "Dataset UTS tidak memuat lead time, biaya kegagalan, maupun catatan keputusan servis, sehingga laporan ini tidak menetapkan ambang siklus tertentu. Aturan tersebut merupakan usulan interpretasi yang masih perlu diuji pada riwayat pemeliharaan nyata sebelum dipakai dalam operasi.")

    # Task 3.
    doc.add_page_break()
    _heading(doc, "4. Task 3 - Clustering Material Multimodal", 1)
    _para(doc, "Task clustering memiliki 36.000 sampel berupa citra mikroskop dan spektrum komposisi tanpa label jenis material. Autoencoder mempelajari embedding citra dan spektrum secara terpisah. Flip horizontal/vertikal diterapkan pada citra; pergeseran kecil dan noise diterapkan pada spektrum. Embedding dinormalisasi, digabungkan, lalu dipakai oleh K-means dan DEC.")
    _heading(doc, "Pemilihan Jumlah Cluster", 2)
    _table(doc, ["K", "Silhouette", "Davies-Bouldin"], [[q["k"], _f(q["silhouette"]), _f(q["davies_bouldin"])] for q in cl["k_criteria"]])
    _table(doc, ["Representasi / metode", "Silhouette"], [
        ["Gambar saja", _f(cl["image_only_silhouette"])],
        ["Spektrum saja", _f(cl["spectrum_only_silhouette"])],
        ["Gabungan K-means", _f(cl["kmeans_silhouette"])],
        ["Gabungan DEC", _f(cl["dec_silhouette"])],
    ])
    _figure(doc, artifacts / "cluster_tsne.png", width=5.5, caption="Gambar 4. Visualisasi t-SNE embedding multimodal dengan label DEC.")
    _para(doc, f"K={cl['selected_k']} dipilih karena memperoleh silhouette tertinggi dan Davies-Bouldin terendah pada rentang yang diuji. Silhouette embedding gabungan masih rendah ({_f(cl['dec_silhouette'])}), dan t-SNE memperlihatkan area sampel yang berdekatan antarkelompok. Ini menunjukkan batas cluster sulit dipisahkan dalam representasi saat ini. Tanpa label material asli, penyebab fisik overlap tidak dapat dipastikan. ARI tidak dapat dihitung; ID mikroskop bukan label material.")

    # Conclusions and reproducibility.
    doc.add_page_break()
    _heading(doc, "5. Kesimpulan dan Reproduksibilitas", 1)
    _para(doc, "Pada klasifikasi, late fusion memberikan macro-F1 validasi tertinggi di antara model fusion utama. Sensor yang hilang menurunkan kinerja dan pergeseran proporsi lini menuntut evaluasi per lini. Pada RUL, GRU memiliki RMSE terbaik, tetapi baseline klasik memberikan skor asimetris yang lebih baik. Pada clustering, K=2 terpilih berdasarkan ukuran internal, tetapi kualitas pemisahan embedding multimodal masih terbatas.")
    _heading(doc, "Batasan", 2)
    _para(doc, "Label klasifikasi test dan label referensi material tidak tersedia di arsip lokal. Karena itu laporan tidak mengklaim skor macro-F1 hidden test atau ARI. Nilai RUL merupakan hasil validasi pada mesin holdout dengan endpoint yang dipotong menyerupai panjang riwayat test.")
    _heading(doc, "Perintah Reproduksi", 2)
    _para(doc, "Notebook utama untuk menjalankan ulang proyek adalah notebooks/uts_deep_learning.ipynb di Google Colab. Unggah notebook, pilih GPU bila tersedia, unggah ZIP source ketika diminta, izinkan akses ke Google Drive yang berisi data_uts_dl.zip, lalu pilih Runtime > Run all. Hasil notebook disimpan di MyDrive/uts_dl_colab/hasil_uts_dl. Dataset tidak disertakan di repository.")
    vers = metrics["runtime"]
    _table(doc, ["Pustaka", "Versi run"], [
        ["Python", vers["python"]], ["PyTorch", vers["torch"]], ["NumPy", vers["numpy"]],
        ["pandas", vers["pandas"]], ["scikit-learn", vers["scikit_learn"]], ["Matplotlib", vers["matplotlib"]],
    ])
    _para(doc, f"Seed yang digunakan: klasifikasi {cls['final_seeds']}, RUL {rul['final_seeds']}, dan clustering 7. Bobot final disertakan pada artifacts/models/. Berkas pengumpulan utama adalah laporan.pdf, folder kode/, prediksi_klasifikasi.csv, prediksi_rul.csv, cluster.csv, dan kontribusi.md. Persetujuan penggunaan AI dan kontribusi tiap anggota dicatat pada kontribusi.md.")

    doc.core_properties.title = "Laporan Ujian Tengah Semester Deep Learning"
    doc.core_properties.subject = "Klasifikasi, regresi RUL, dan clustering multimodal"
    doc.save(path)
    return path
