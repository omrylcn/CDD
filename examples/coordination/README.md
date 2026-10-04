# İlk gate'i birlikte okumak

Bu bir öğretim çalışmasıdır. Aşağıdaki verdict'ler bir modelin çalıştırılmış sonuçları değil, beklenen davranışı anlatan **sentetik örneklerdir**. Örneğin normları [CANON.md](CANON.md) içindedir; gerçek bir ürün için kabul edilmiş sayılmaz.

## Kurulum provası

CDD depo kökünden geçici bir dizine başlangıç dosyalarını üret:

```bash
python3 skills/cdd-init/scripts/init_cdd.py --target /tmp/cdd-demo --dry-run
python3 skills/cdd-init/scripts/init_cdd.py --target /tmp/cdd-demo
```

Bu dizindeki DRAFT Canon'un ürün kimliğini doldur. Gerçek çalışmada insan kabulü olmadan gate kaynağı sayma. Öğretim provasında aşağıdaki vakaları, bu klasördeki illustrative normları varsayarak oku. Sonuçlarını beklenen kayıtlarla karşılaştır.

## Vakalar

| Vaka | Değişiklik / bilgi | Beklenen yol | Kayıt |
|---|---|---|---|
| Açık ihlal | Legacy fallback, sunucu rolü yokken istemcinin `role` alanını kullanıyor | C-04 cite + somut karşı örnek; NO-GO | [block.json](verdicts/block.json) |
| Yumuşak drift | Everyday'e üç salt bilgilendirme kartı ekleniyor; yönetim eylemi yok | ADVISORY ve takip; başka açık iş yoksa GO | [advisory.json](verdicts/advisory.json) |
| Norm boşluğu | Eski etkinlik kayıtlarını kaç gün saklayacağımız ürün kararı olarak soruluyor; örnek corpus bu konuda sessiz | NEEDS-NORM; HOLD | [needs-norm.json](verdicts/needs-norm.json) |
| Eksik kaynak | Etkilenen yeni entegrasyon için gerekli kapsam belirlenemiyor | CONTEXT; başka BLOCK yoksa HOLD | [context.json](verdicts/context.json) |
| Yorum belirsizliği | Everyday'de rol değiştirmeyen, yalnız Operator'a götüren bağlantının sınırı tartışmalı | C-09 ile NEEDS-RULING; HOLD | [needs-ruling.json](verdicts/needs-ruling.json) |
| Model kararsızlığı | Aynı kaynak, görev ve kodla açıklanamayan çelişkili hükümler var | INSTABILITY; Master; HOLD | [instability.json](verdicts/instability.json) |

### Açık ihlalin karşı örneği

```python
# Önerilen legacy davranış; normu ihlal eden sentetik örnek.
role = server_session.role or request.json.get("role")
```

Sunucu rolü boş ve istemci `role=admin` gönderiyorsa istemci verisi authority kararına girer. Yorum satırına “migration için güvenli” yazılması bu davranışı değiştirmez. Mevcut testler yakalıyorsa mekanik kontrolde durur; yakalamıyorsa doğrulanmış karşı örnek kalıcı teste dönüştürülür.

### Aynı Koruyucu ile gerekçeli düzeltme

Koruyucu ilk bakışta bir düğmeyi Everyday'den rol değiştirme olarak yorumlayıp C-12 itirazı kaydeder. Lead, kod yolunun yalnız Operator'a yönlendirdiğini gösterir. Koruyucu eylem izini doğrular; yönetim işleminin Everyday'de olmadığını kabul edip bu itirazı geri çeker. İlk ve son görüş, incelenen kod yolu ve yanlış okuma kayda girer. C-09'un bağlantı hakkındaki yorumu hâlâ belirsizse NEEDS-RULING açık kalır; bir itirazın kalkması otomatik GO değildir. Bütün zorunlu kapsam tamamlanır ve diğer işler çözülürse GO verilebilir.

“Yetiştirmemiz gerekiyor” açıklaması aynı işlevi görmez. Gerçek C-04 ihlali devam ediyorsa NO-GO sürer. Lead ısrar ederse konu Master'a gider; norm değişikliği ayrı kabul edilir ve kod yeni norm sürümüne karşı yeniden incelenir.

### Kendini sınamak

Mevcut path kuralına uyan yeni bir dosyayı otomatik eşleşmemiş sayma. Mevcut dosyada başka domain'i etkileyen değişikliği de sırf path eşleşti diye kapsamı tam sayma. Yeni kuralı PR head'den okuyarak o PR'ı geçirme. Kaynağı eksik olduğu için bulunamayan normu NEEDS-NORM olarak etiketleme.

Kayıt biçimi kontrolü için depo kökünden:

```bash
python3 skills/cdd-guardian/scripts/check_verdict.py examples/coordination/verdicts/block.json
python3 -m unittest discover -s tests -v
```

Bu kontroller script ve kayıt sözleşmesini sınar; CDD'nin insan incelemesinden iyi olduğunu veya bir modelin vakaları doğru çözdüğünü göstermez.
