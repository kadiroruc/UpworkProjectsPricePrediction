# UpworkProjectsPricePrediction
## Genel Bakış

Bu projede; veri kazıma ile elde edilen veriler üzerinde veri hazırlama, makine öğrenmesi algoritmalarını uygulama ve sonuçları analiz etme işlemleri gerçekleştirildi. Bu projenin amacı, development alanında sahip olunan yeteneklere ve proje seviyesine göre Upwork sitesi üzerindeki freelance projelerin saatlik ya da sabit ücret kategorisini tahmin etmek.

---

## İçindekiler

1. [Veri Seti](#veri-seti)
2. [Veri Hazırlama](#veri-hazırlama)
3. [Makine Öğrenmesi Modelleri](#makine-öğrenmesi-modelleri)
4. [Sonuçlar ve Analiz](#sonuçlar-ve-analiz)
5. [Video Açıklama](#video-açıklama)
6. [GitHub Deposu](#github-deposu)

---

## Veri Seti

- **Veri Kaynağı**:  
  Veri, [**Upwork**](https://www.upwork.com/nx/find-work/) üzerinden veri kazıma teknikleriyle elde edilmiştir ve makine öğrenmesi modeli için hazırlanmıştır.

- **Veri Seti Detayları**:  
  - Sütunlar: Job Title(Proje Başlığı), Hourly/Fixed(Saatlik ya da Sabit ücrete sahip olduğu), Budget(Sabit ücret ise ücreti), Skills(Gereken yetenekler)     
---

## Veri Hazırlama

### Veri Temizleme
- Veri kazıma yapılırken oluşan tekrarlar `drop_duplicates()` metodu ile kaldırıldı.
- Job Title sütunu kaldırıldı.
- Skills sütununda yeteneklerin sonunda bulunan +1 gibi ifadeler regex kullanımı ile kaldırıldı.
- Skills sütunundaki eksik değerler kaldırıldı.
- Yetenekler encoding yapılmadan önce Skills sütununda virgülle ayrılmış değerler alınarak all_skills serisi oluşturuldu ve en çok geçen yeteneklerden 200 tanesi seçildi.(Genellikle veri sayısının 1/10'u kadar özellik sütunu uygun oluyor.)
- Skills sütununda virgül ile ayrılmış yeteneklerin her biri için one-hot encoding yapıldı. `df["Skills"].str.get_dummies(sep=", ")`. Daha önce sıralayıp seçtiğimiz 200 tanesi ile bu sütunlar filtrelenip oluşturulan dataframe ana datafreme'e birleştirildi. Orjinal Skills sütunu da kaldırıldı.
- Hourly/Fixed sütununda bazı veriler "Hourly: $25.00 - $35.00" şeklindeydi buradan bu sayısal değerler yakalandı ve ortalaması alındı. Budget sütununda ise bazı veriler "Est. budget: $150.00" şeklindeydi. Buradan da sayısal değerler yakalandı. Hourly/Fixed sütunu artık saatlik ücretleri tuttuğu için ismi Hourly, Budget sütunu artık sabit ücretleri tuttuğu için ismi Fixed olarak değiştirildi.
- Hourly ve Fixed sütunlarının ikisinin de NaN olduğu değerler kaldırıldı.
- İlk 200 yetenek arasında bulunan yazılım dilleri&frameworkleri ve projelerin seviye dağılımları bar grafikleri üzerinde gösterildi.
- Dataframe'de hourly ve fixed değerlerden yalnızca biri bulunduğu için Dataframe hourly ve fixed olarak ayrıldı. İki Dataframe'de de ücret sütunları `price_value` olarak değiştirildi. Bu değerler string olduğu için numerik değerlere dönüştürüldü.
- Ücret değerleri boxplot üzerinde gösterildi. Bu sayede min, max ve aykırı değerler görüntülenmiş oldu. Buna ek olarak aralıklar oluşturularak ücret dağılımları bar grafikleri üzerinde gösterildi.
- Aykırı değerler için lower_bound ve upper_bound değerleri hesaplanarak bu aralık dışında olan değerler ortalama ücret değerleri ile değiştirildi.
- Ücret kategorileri için aralıklar belirlendi ve oluşan kategoriler `price_category` sütunu ile Dataframe'e eklendi.
- Verilerde dengesizlik olduğu için azınlık sınıfların sayısını artırarak(`Oversampling`) sınıfları eşitledim. Bu sayede modelin çoğunluk sınıfını tahmin etmesi önlenmiş oldu.


### Veri Bölme
- Veriler, eğitim ve test setlerine %80/20 oranında bölündü.
- Model için `X` değeri encoding yapılmış yetenek ve seviye sütunları, `y` değeri `price_category` olarak belirlendi.

---

## Makine Öğrenmesi Modelleri

### Uygulanan Algoritmalar:
1. **Lojistik Regresyon**:
2. **Destek Vektör Makinesi (SVM)**:
3. **Rastgele Orman (Random Forest)**:

Her bir model, doğruluk, karışıklık matrisi ve sınıflandırma raporları kullanılarak değerlendirildi. 

### Model Değerlendirmesi
- Her bir model, `doğruluk`, `karışıklık matrisi` ve `sınıflandırma raporları(Doğruluk, Precision, Recall, F1-Score)` kullanılarak değerlendirildi.
- Modellerin doğruluk değerleri grafik üzerinde karşılaştırıldı.
- Her bir model için `roc curve` grafiği oluşturuldu ve `auc` değerleri oluşturuldu.
---

## Sonuçlar ve Analiz

### Performans Karşılaştırması

  
#### Anahtar Sonuçlar:


### Sonuç:


---

## Video Açıklama

Analiz ve uyguladığım modellerin detaylı bir anlatımı için aşağıdaki videoya göz atabilirsiniz:

[**Videoyu İzleyin**](video-linki)

---

## GitHub Deposu

Bu projeye ait tüm kod ve dosyalar GitHub reposunda mevcuttur.

[**GitHub Deposu**](repo-linki)

Projeyi kopyalayabilir, çatallayabilir veya katkıda bulunabilirsiniz. Herhangi bir sorunuz veya geri bildiriminiz olursa benimle iletişime geçmekten çekinmeyin.

---
