# Upwork Proje Veri Analizi ve Fiyat Tahmin Modeli
## Genel Bakış

Bu projede; Upwork sitesinden veri kazıma ile elde edilen veriler üzerinde veri ön işleme, veri görselleştirme, makine öğrenmesi modellerini uygulama ve sonuçları analiz etme işlemleri gerçekleştirildi. Bu projenin amacı, sahip olunan yeteneklere ve proje seviyesine göre Upwork sitesi üzerinde yazılım geliştirme alanındaki freelance projelerin saatlik ve sabit ücret kategorisini tahmin etmektir.



## İçindekiler

1. [Veri Seti](#veri-seti)
2. [Veri Hazırlama](#veri-hazırlama)
3. [Makine Öğrenmesi Modelleri](#makine-öğrenmesi-modelleri)
4. [Sonuçlar ve Analiz](#sonuçlar-ve-analiz)
5. [Video Açıklama](#video-açıklama)
6. [GitHub Deposu](#github-deposu)


## Veri Seti

- **Veri Kaynağı**:  
  Veri, [**Upwork**](https://www.upwork.com/nx/find-work/) üzerinden veri kazıma teknikleriyle elde edilmiştir ve makine öğrenmesi modeli için hazırlanmıştır
  [Dosya Adı](https://github.com/kullanıcı-adı/proje-adı/blob/branch-adı/dosya-yolu)

- **Veri Seti Detayları**:  
  - Job Title: Proje Başlığı
  - Hourly/Fixed: Saatlik ya da Sabit ücrete sahip olduğu
  - Budget: Sabit ücret ise ücreti
  - Skills: Gereken yetenekler

## Veri Hazırlama

### Veri Temizleme
- Veri kazıma yapılırken oluşan tekrarlar kaldırıldı.
  ```
  df = df.drop_duplicates()
  print(f'Satır Sayısı: {df.shape[0]}\n')
  ``` 
- Job Title sütunu kaldırıldı.
  ```
  df = df.drop(columns=['Job Title'])
  ```
- Skills sütununda yeteneklerin sonunda bulunan "+1" gibi ifadeler `regex` kullanımı ile kaldırıldı.
  ```
  df['Skills'] = df['Skills'].str.replace(r', \+\d+', '', regex=True)
  ```
- Skills sütunundaki eksik değerler kaldırıldı.
  ```
  df['Skills'] = df['Skills'].str.replace(r', \+\d+', '', regex=True)
  ```
- Yetenekler encoding yapılmadan önce Skills sütununda virgülle ayrılmış değerler alınarak `all_skills` serisi oluşturuldu ve en çok geçen yeteneklerden 200 tanesi seçildi.(Genellikle veri sayısının 1/10'u kadar özellik sütunu uygun oluyor.)
  ```
  all_skills = df['Skills'].str.split(',').explode().str.strip()
  top_200_skills = all_skills.value_counts().head(200).index.to_numpy()
  all_skills.value_counts().to_csv("skills_count.csv")
  ```
- Skills sütununda virgül ile ayrılmış yeteneklerin her biri için one-hot encoding yapıldı. Daha önce sıralayıp seçtiğimiz 200 yetenek ile bu sütunlar filtrelenip ana datafreme'e birleştirildi. Orjinal Skills sütunu da kaldırıldı.
  ```
  encoded_skills = df["Skills"].str.get_dummies(sep=", ")
  filtered_encoded_skills = encoded_skills[top_200_skills]
  df = pd.concat([df, filtered_encoded_skills], axis=1)
  df = df.drop(columns=['Skills'])
  ```

- Hourly/Fixed sütununda bazı veriler "Hourly: $25.00 - $35.00" şeklindeydi buradan bu sayısal değerler yakalandı ve ortalaması alındı. Budget sütununda ise bazı veriler "Est. budget: $150.00" şeklindeydi. Buradan da sayısal değerler yakalandı. Hourly/Fixed sütunu artık saatlik ücretleri tuttuğu için ismi Hourly, Budget sütunu artık sabit ücretleri tuttuğu için ismi Fixed olarak değiştirildi.
  ```
  def extract_hourly_rate(value):
    match = re.match(r'Hourly: \$(\d+\.\d+) - \$(\d+\.\d+)', value)
    if match:
        low = float(match.group(1))
        high = float(match.group(2))
        return (low + high) / 2
    return None 

  df['Hourly/Fixed'] = df['Hourly/Fixed'].apply(extract_hourly_rate)
  df.rename(columns={'Hourly/Fixed': 'Hourly'}, inplace=True)

  df['Budget'] = df['Budget'].str.extract(r'\$(\d+\.\d+)')
  df.rename(columns={'Budget': 'Fixed'}, inplace=True)
  ```

- Hourly ve Fixed sütunlarının ikisinin de NaN olduğu değerler kaldırıldı.
  ```
  both_null_rows = df[df['Hourly'].isnull() & df['Fixed'].isnull()]
  df_cleaned = df.drop(both_null_rows.index)
  ```
- Dataframe'de hourly ve fixed değerlerden yalnızca biri bulunduğu için Dataframe hourly ve fixed olarak ayrıldı. İki Dataframe'de de ücret sütunları `price_value` olarak değiştirildi. Bu değerler string olduğu için numerik değerlere dönüştürüldü.
  ```
  hourly_df = df[df['Hourly'].notnull()].copy()
  fixed_df = df[df['Fixed'].notnull()].copy()

  hourly_df['price_value'] = hourly_df['Hourly']
  fixed_df['price_value'] = fixed_df['Fixed']
  
  hourly_df.drop(['Hourly', 'Fixed'], axis=1, inplace=True)
  fixed_df.drop(['Hourly', 'Fixed'], axis=1, inplace=True)

  fixed_df['price_value'] = pd.to_numeric(fixed_df['price_value'], errors='coerce')
  hourly_df['price_value'] = pd.to_numeric(hourly_df['price_value'], errors='coerce')
  ```

- Aykırı değerler için lower_bound ve upper_bound değerleri hesaplanarak bu aralık dışında olan değerler ortalama ücret değerleri ile değiştirildi (Aynısı `hourly` için de yapıldı.)
  ```
  Q1_fixed = fixed_df['price_value'].quantile(0.25)
  Q3_fixed = fixed_df['price_value'].quantile(0.75)
  IQR = Q3_fixed - Q1_fixed
  
  lower_bound = Q1_fixed - 1.5 * IQR
  upper_bound = Q3_fixed + 1.5 * IQR
  
  mean_value = fixed_df['price_value'].mean()
  fixed_df['price_value'] = fixed_df['price_value'].apply(lambda x: mean_value if (x < lower_bound or x > upper_bound) else x)
  ```

- Ücret kategorileri için aralıklar belirlendi ve oluşan kategoriler `price_category` sütunu ile Dataframe'e eklendi.
  ```
  bins = [0, 15, 50, float('inf')]  # 0-15 düşük, 15-50 orta, 50+ yüksek
  labels = ['Düşük', 'Orta', 'Yüksek']

  hourly_df['price_category'] = pd.cut(hourly_df['price_value'], bins=bins, labels=labels, right=False)  
  
  category, bins = pd.cut(fixed_df['price_value'], 
                          bins=3,  #3 eşit grup
                          labels=['Düşük', 'Orta', 'Yüksek'], 
                          retbins=True)  #Aralık sınırlarını da döndürdüm
  
  fixed_df['price_category'] = category
  
  X = fixed_df.drop(['price_value', 'Level', 'price_category'], axis=1)
  y = fixed_df['price_category']
  ```

- Verilerde dengesizlik olduğu için azınlık sınıfların sayısını artırarak(`Oversampling`) sınıfları eşitledim. Bu sayede modelin çoğunluk sınıfını tahmin etmesi önlenmiş oldu.
  ```
  smote = SMOTE(random_state=42)
  X_resampled, y_resampled = smote.fit_resample(X, y)
  ```

### Veri Bölme
- Veriler, eğitim ve test setlerine %80/20 oranında bölündü.
- Model için `X` değeri encoding yapılmış yetenek ve seviye sütunları, `y` değeri `price_category` olarak belirlendi.
  ```
  X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
  ```

## Veri Görselleştirme
- İlk 200 yetenek arasında bulunan ve en çok bilinen yazılım dilleri & frameworkleri ile projelerin seviye dağılımları bar grafikleri üzerinde gösterildi.
<p align="center">
  <img src="https://github.com/user-attachments/assets/2b8ea95a-f798-42fb-a019-3f581737032a" width="600">
  <img src="https://github.com/user-attachments/assets/d453ab65-778f-4055-a1b6-ac2ffd3c9b9f" width="600">
</p>
<br><br>

- Ücret değerleri boxplot üzerinde gösterildi. Bu sayede min, max ve aykırı değerler görüntülenmiş oldu. Buna ek olarak aralıklar oluşturularak ücret dağılımları bar grafikleri üzerinde gösterildi.
<p align="center">
  <img src="https://github.com/user-attachments/assets/004c624b-6448-47c6-89db-67bbbd30352c" width="600">
  <img src="https://github.com/user-attachments/assets/6e277810-095d-41d3-8b33-e23d32f60bbb" width="600">
  <img src="https://github.com/user-attachments/assets/8d6ab4e0-8723-47d4-bce3-ebf722d0a564" width="600">
  <img src="https://github.com/user-attachments/assets/e8a7ce34-a3b3-4102-8ae6-44cf8c5f261d" width="600">
</p>



## Makine Öğrenimi Modelleri

### Uygulanan Algoritmalar:
1. **Lojistik Regresyon**
2. **Destek Vektör Makinesi (SVM)**
3. **Random Forest**

- 3 adet sınıflandırma algoritmasını içeren `models` isminde bir dictionary oluşturuldu ve bir döngü ile model eğitimlerini ve model değerlendirmeleri yapıldı. Ek olarak modellerin accuracy değerlerini tutmak için `fixed_accuracy` ve `hourly_accuracy` isminde arrayler oluşturuldu. (Aynı döngü hourly için de yapıldı.)
  ```
  models = {
    "Logistic Regression": LogisticRegression(),
    "Support Vector Machine": SVC(kernel='linear',probability=True),
    "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42)
  }
  fixed_accuracy = []
  hourly_accuracy = []
  
  print("\nFIXED PRICE PERFORMANCE METRICS:\n" + "-" * 40)
  for name, model in models.items():
      print(f"Model: {name}\n-----------------------------")
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    fixed_accuracy.append(accuracy)
    print(f"Accuracy for {name}: {accuracy:.2f}")
    
    print(f"Classification Report for {name}:")
    print(classification_report(y_test, y_pred))
    
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred, cmap="Blues")
    plt.title(f"Confusion Matrix for {name} - Fixed")
    plt.show()
    print("\n" + "-"*50 + "\n")
  ```

### Performans Metrikleri
- `Doğruluk (Accuracy)`: Modelin doğru tahmin ettiği örneklerin, toplam tahmin edilen örneklere oranıdır.<br> 
`(TP + TN) / (TP + TN + FP + FN)`
- `Kesinlik (Precision)`: Pozitif olarak tahmin edilen örneklerin ne kadarının gerçekten pozitif olduğunu ölçer. `TP / (TP + FP)`
- `Duyarlılık (Recall)`: Gerçek pozitif sınıfların ne kadarının doğru tahmin edildiğini gösterir. `TP / (TP + FN)`
- `F1 Skoru`: Precision ve Recall’un harmonik ortalamasıdır. `2(Precision X Recall) / (Precision + Recall)`
- `ROC-AUC (Eğri Altındaki Alan)`: ROC eğrisinin altındaki alanı ölçer. Modelin, sınıfları ayırt etme yeteneğini genel olarak değerlendirir. AUC değeri 1’e yaklaştıkça modelin performansı artar.`
- `Confusion Matrix (Karmaşıklık Matrisi)`: Tahmin edilen ve gerçek sınıflar arasındaki dağılımı detaylı olarak gösterir. Her bir hücre, tahmin sonuçlarını ifade eder.
  - TP (True Positive): Doğru şekilde pozitif olarak tahmin edilenler.
  - TN (True Negative): Doğru şekilde negatif olarak tahmin edilenler.
  - FP (False Positive): Yanlış şekilde pozitif olarak tahmin edilenler. 
  - FN (False Negative): Yanlış şekilde negatif olarak tahmin edilenler.
  

## Sonuçlar

### Performans Metrik Değerleri
#### Saatlik Ücret
- `Lojistik Regresyon`:
  - Accuracy: 0.63
  - Sınıflandırma Raporu:
    ```
    Classification Report for Logistic Regression:
                  precision    recall  f1-score   support
    
           Düşük       0.53      0.46      0.49       299
            Orta       0.71      0.61      0.66       322
          Yüksek       0.63      0.80      0.71       310
    
        accuracy                           0.63       931
       macro avg       0.62      0.63      0.62       931
    weighted avg       0.63      0.63      0.62       931
    ```
  - Karışıklık Matrisi:
    <p align="center">
    <img src="https://github.com/user-attachments/assets/46cc6660-40a4-46e6-8586-c8a1542b19a4" width="400">
    </p>

- `Support Vector Machine (SVM)`:
  - Accuracy: 0.62
  - Sınıflandırma Raporu:
    ```
    Classification Report for Support Vector Machine:
                  precision    recall  f1-score   support
    
           Düşük       0.50      0.51      0.50       299
            Orta       0.72      0.57      0.64       322
          Yüksek       0.65      0.77      0.70       310
    
        accuracy                           0.62       931
       macro avg       0.62      0.62      0.62       931
    weighted avg       0.63      0.62      0.62       931
    ```
  - Karışıklık Matrisi:
    <p align="center">
    <img src="https://github.com/user-attachments/assets/efaab68e-61c9-49c1-badc-bb02653d789d" width="400">
    </p>

    
- `Random Forest`:
  - Accuracy: 0.73
  - Sınıflandırma Raporu:
    ```
    Classification Report for Random Forest:
                  precision    recall  f1-score   support
    
           Düşük       0.64      0.66      0.65       299
            Orta       0.82      0.60      0.69       322
          Yüksek       0.74      0.93      0.83       310
    
        accuracy                           0.73       931
       macro avg       0.73      0.73      0.72       931
    weighted avg       0.74      0.73      0.72       931
    ```
  - Karışıklık Matrisi:
    <p align="center">
    <img src="https://github.com/user-attachments/assets/44932343-fb65-4a69-a6ca-5f5df7f9296b" width="400">
    </p>

#### Sabit Ücret
- `Lojistik Regresyon`:
  - Accuracy: 0.56
  - Sınıflandırma Raporu:
    ```
    Classification Report for Logistic Regression:
                  precision    recall  f1-score   support
    
           Düşük       0.67      0.61      0.64       250
            Orta       0.48      0.38      0.42       237
          Yüksek       0.52      0.67      0.59       248
    
        accuracy                           0.56       735
       macro avg       0.56      0.55      0.55       735
    weighted avg       0.56      0.56      0.55       735
    ```
  - Karışıklık Matrisi:
    <p align="center">
    <img src="https://github.com/user-attachments/assets/e2c7cc65-45d6-4e58-bfed-b178e19ce38f" width="400">
    </p>

- `Support Vector Machine (SVM)`:
  - Accuracy: 0.54
  - Sınıflandırma Raporu:
    ```
    Classification Report for Support Vector Machine:
                  precision    recall  f1-score   support
    
           Düşük       0.66      0.52      0.58       250
            Orta       0.48      0.32      0.39       237
          Yüksek       0.50      0.75      0.60       248
    
        accuracy                           0.54       735
       macro avg       0.54      0.53      0.52       735
    weighted avg       0.55      0.54      0.52       735
    ```
  - Karışıklık Matrisi:
    <p align="center">
    <img src="https://github.com/user-attachments/assets/133434b3-fc63-489d-9ff2-0e6e6e289d8c" width="400">
    </p>
    
- `Random Forest`:
  - Accuracy: 0.64
  - Sınıflandırma Raporu:
    ```
    Classification Report for Random Forest:
                  precision    recall  f1-score   support
    
           Düşük       0.70      0.60      0.65       250
            Orta       0.56      0.71      0.63       237
          Yüksek       0.68      0.61      0.64       248
    
        accuracy                           0.64       735
       macro avg       0.65      0.64      0.64       735
    weighted avg       0.65      0.64      0.64       735
    ```
  - Karışıklık Matrisi:
    <p align="center">
    <img src="https://github.com/user-attachments/assets/722a4b20-fc1b-48e6-a89b-9eb3b3f7197e" width="400">
    </p>

<br><br>

### Model Accuracy Değerleri Grafiği
<br>
  <p align="center">
    <img src="https://github.com/user-attachments/assets/67088134-5ad5-4072-b6d9-acb00cc02520" width="800">
  </p>
<br><br>

### Roc Curve Grafikleri(Saatlik Ücretler)
<br>
<p align="center">
  <img src="https://github.com/user-attachments/assets/31f4214a-7393-4045-b0df-af08a5858732" width="400">
  <img src="https://github.com/user-attachments/assets/718f0bb5-8095-4328-8e69-6a57ee230aa7" width="400">
  <img src="https://github.com/user-attachments/assets/737df630-b75b-444c-9c7f-1ef02c0e689d" width="400">
</p>
  


## Analiz:

### Model Değerlendirmeleri

- Random Forest, hem sabit ücret hem de saatlik ücret verilerinde en iyi performansı gösterdi.
  - Daha karmaşık bir yapı ve çok sayıda ağaç kullanarak sınıfları daha iyi ayırabildi.
  - Her iki veri setinde de “Yüksek” sınıfını tespit etmede oldukça başarılıdır.
- Logistic Regression ve Support Vector Machine, özellikle “Orta” sınıfta yetersiz kaldı.
  - Bu modeller, sınıflar arasındaki çizgiyi net bir şekilde ayıramadığı için performansı düşüktür.
- Dengesiz sınıfların etkisi:
  - SMOTE kullanılmış olmasına rağmen düşük ve orta sınıflar üzerinde performans hâlâ yetersizdir. Özellikle daha karmaşık sınıflar (örneğin orta fiyat aralığı) için modele ek özellikler eklemek gerekebilir.
- Aykırı değerlerin kaldırılması accuracy değerlerinde yaklaşık olarak 0.01 - 0.03 arasında artış sağladı.

<br>

### Roc Curve Analizi (Saatlik Ücretler)
AUC (Area Under Curve) değeri, sınıflandırıcının başarısını temsil eder ve genellikle 0.5 ile 1 arasında değişir. Değer ne kadar 1’e yakınsa, model o kadar iyi performans gösteriyor demektir. 

-  `Random Forest`
  - Düşük Sınıf (AUC = 0.81): Düşük sınıf için model oldukça başarılı, çünkü AUC değeri 0.8’in üzerinde. Ancak diğer sınıflara kıyasla biraz daha düşük performans sergiliyor.
 - Orta Sınıf (AUC = 0.87): Orta sınıfta daha iyi bir ayırt ediciliğe sahip.
 - Yüksek Sınıf (AUC = 0.93): Random Forest modeli, yüksek sınıf için çok güçlü bir performans gösteriyor. AUC değeri 0.9’un üzerinde.

Genel olarak, Random Forest modeli tüm sınıflar için dengeli bir şekilde yüksek bir performans sergilemiştir.

- `Support Vector Machine (SVM)`
  - Düşük Sınıf (AUC = 0.67): Düşük sınıfta performansı zayıf, AUC değeri 0.7’nin altında kalıyor. Bu sınıf için model zorluk yaşayabilir.
  - Orta Sınıf (AUC = 0.82): Orta sınıfta performansı daha iyi, AUC değeri 0.8’in üzerinde.
  - Yüksek Sınıfı (AUC = 0.85): Yüksek sınıf için güçlü bir performans sergiliyor, ancak Random Forest ile kıyaslandığında biraz geride kalıyor.

SVM modeli genel olarak iyi bir performansa sahip, ancak düşük sınıf için ayırt etme gücü zayıf.

- `Lojistik Regresyon`
  - Düşük Sınıfı (AUC = 0.68): Düşük sınıfta performansı zayıf, AUC değeri 0.7’nin altında kalıyor.
  - Orta Sınıfı (AUC = 0.82): Orta sınıfta performansı iyi, AUC değeri 0.8’in üzerinde.
  - Yüksek Sınıfı (AUC = 0.85): Yüksek sınıf için güçlü bir performans sergiliyor, ancak Random Forest kadar iyi değil.



## Video Açıklama

Analiz ve uyguladığım modellerin detaylı bir anlatımı için aşağıdaki videoya göz atabilirsiniz:

[**Videoyu İzleyin**](video-linki)


## GitHub Deposu

Bu projeye ait tüm kod ve dosyalar GitHub reposunda mevcuttur.

[**GitHub Deposu**](repo-linki)

---
