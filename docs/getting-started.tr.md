# Bir projede CDD'ye başlamak

Bu rehber Faz 0'ı kurar: kısa bir Canon, ayrı bir Koruyucu değerlendirme rolü ve karar kaydı. Script dosyaları hazırlar; ajan orkestrasyonu, insan onayı veya CI enforcement kurmaz.

## 1. Taslak dosyaları oluştur

CDD deposunun kökünden, hedef ürün dizinini açıkça ver:

```bash
python3 skills/cdd-init/scripts/init_cdd.py --target ../benim-urun --dry-run
python3 skills/cdd-init/scripts/init_cdd.py --target ../benim-urun
```

Çıktılar: `AGENTS.md`, `CANON.md`, `GUARDIAN.md`, `RULINGS.md`, `CDD_LOG.md`. Var olan farklı içerik veya symlink bulunursa işlem yazmadan durur. Aynı şablonlarla tekrar çalıştırmak dosyaları değiştirmez. `--skip-agents`, mevcut AGENTS dosyasını koruyarak diğer eksik dosyaları hazırlamak içindir; CDD talimatlarını mevcut AGENTS ile elle uzlaştırmak yine gerekir.

## 2. Ürün kimliğini yaz ve kabul et

`CANON.md` içindeki boşlukları ürüne göre doldur. Hayali koordinasyon uygulamasının ilkelerini otomatik kopyalama. İnsan ürün sahibi ilkeleri ve yetki maddesini kabul etmeden DRAFT durumunu yürürlükte gibi kullanma.

Kabul edilen norm metninin sürümünü veya hash'ini ve insan kararının doğrulanabilir kaynağını `CDD_LOG.md` içinde bağla. Sadece `ratified_by: Master` yazmak veya bir commit oluşturmak bu kabulün doğruluğunu kanıtlamaz. Kabulün ardından oluşan güvenilir kaynak commit'i sonraki incelemelerin base'i olur. Kaydı başka bir commit'te tutarak kendi hash'ini içinde yazmaya çalışan döngüsel bir onay dosyası üretme.

## 3. Rolleri bağla

Lead kodu üretir. Ayrı Koruyucu rolüne kabul edilmiş `GUARDIAN.md`, Canon, ilgili ACTIVE ruling'ler, özgün görev ve incelenecek diff verilir. İki rol aynı modeli kullanabilir; bu hata bağımsızlığı sağlamaz.

CONSULT, Kurul ve gate için aynı Koruyucu rolünü ve ilgili geçmişi sürdür. Lead bir itirazı tartışırken başka bir Koruyucu instance'ı açıp geçmişi silme. Süreç yeniden başlarsa gerekli karar kaydını ve kaynak sürümlerini geri yükle. Ortam ayrı değerlendirme rolünü desteklemiyorsa bunu öz-denetim olarak kullanabilirsin; CDD gate kurulmuş sayılmaz.

Taşınabilir skill paketleri: [cdd-init](../skills/cdd-init/SKILL.md) ve [cdd-guardian](../skills/cdd-guardian/SKILL.md). Hedef ajanın desteklediği skill dizinine **paketin tamamını** yerleştir veya SKILL.md talimatını açıkça yükle. Bu depodaki `skills/` dizini tek başına herhangi bir uygulamaya otomatik kurulum yapmaz. Örnek çağrı: `$cdd-init ile bu üründe Faz 0 taslağını hazırla`; ayrı Koruyucu rolünde `$cdd-guardian ile bu diff'i incele`.

## 4. İlk inceleme paketini hazırla

Tam commit kimliklerini kullan; `BASE` insanın kabul ettiği kaynak commit'idir, otomatik olarak güncel HEAD anlamına gelmez. Aşağıdaki komutlar hedef ürün reposunda çalışır:

```bash
BASE='<kabul-edilmis-tam-commit-sha>'
HEAD_SHA='<incelenecek-tam-commit-sha>'
git show "$BASE:CANON.md"
git show "$BASE:GUARDIAN.md"
git show "$BASE:RULINGS.md"
git diff --name-status "$BASE" "$HEAD_SHA"
git diff "$BASE" "$HEAD_SHA"
```

Gerekirse ek dosyaları salt okunur incele. Kod değişikliği, norm değişikliği ve denetim dosyası değişikliklerini ayır; PR head'deki kuralı kendiliğinden yürürlüğe alma. Faz 0'da küçük corpus'un tamamını yüklemek yeterli olabilir. Kaynak manifest'ini ve seçim gerekçesini, kapsam dışı alanları, özgün görevi, mekanik kontrolleri ve model/prompt sürümünü pakete ekle. Eksikleri açıkça işaretle.

## 5. İlk görüş, diyalog ve karar

Koruyucu önce görüşünü kaydeder. Lead bir karşı örnek veya açıklama sunarsa aynı Koruyucu değerlendirir; ilk ve son görüşün dayanağı saklanır. Çözülemeyen itirazda Lead ısrar ederse Master'a gidilir. INSTABILITY ek ikna turuna açılmaz.

| Sonuç | Yapılacak iş |
|---|---|
| GO | Canon incelemesi tamam; diğer test/review onaylarına devam |
| NO-GO | Düzelt veya gerekçeli itirazı çöz; diğer açık işler kayıtta kalsın |
| HOLD | Kaynak, kapsam veya yetkili kararı tamamla; yalnız yeniden çalıştırarak GO arama |

`references/verdict-template.json` HOLD durumunda bir başlangıç şablonudur. Örnek kaydı gerçek inceleme diye kullanma. JSON sözleşmesini kontrol etmek için:

```bash
python3 skills/cdd-guardian/scripts/check_verdict.py examples/coordination/verdicts/block.json
```

Komutun sıfır çıkış kodu **kaydı tutarlı bulduğu** anlamına gelir; örnekte gate NO-GO'dur. Komutu tek başına GitHub merge kontrolü yapma: semantik doğruluğu, kimliği ve kaynakların kabulünü doğrulamaz.

## 6. Örneği çalış ve otomasyonu sonra bağla

[Koordinasyon örneği](../examples/coordination/README.md), açık ihlal, yumuşak drift, norm boşluğu, eksik kaynak ve gerekçeli düzeltmeyi gösterir. Bunlar sentetik öğretim vakalarıdır; gerçek kullanım sonucu değildir.

Gerçek PR gate'i eklerken değerlendirme çıktısını tam code/base/corpus/evaluator sürümlerine bağla; geçerli çıktıyı kimin üretebildiğini ve insanın kabul yetkisini doğrula. Ajanın yazdığı JSON'un GO olması enforcement değildir. Yeni commit veya kabul edilmiş kaynak değişikliği eski verdict'i geçersiz kılar. Bu başlangıç paketi platform korumalarını otomatik değiştirmez.
