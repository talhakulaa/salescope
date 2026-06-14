# PHASE 5: Data Quality & Anomaly Detection

**Yapılan Analiz:**  
Phase 1 ve 2 verileri üzerinden veri kalitesi riskleri ele alındı (Eksik veriler, anomaliler, imkansız veya mantıksız değerler).

**🧠 Bulgular:**  
- Missing Value (Kayıp Değer) oranı %0. Klasik bir imputasyona gerek yoktur.
- Sayısal değişkenlerde (Duration bazlı ve PageValues) ciddi "outlier" yoğunluğu saptanmıştır (Örn: PageValues %22, Duration %8). Bu oranlar teknik olarak aykırı olsa da E-Ticaret sistemlerinin gerçek iş mantığı ile paralellik gösterir.

---

