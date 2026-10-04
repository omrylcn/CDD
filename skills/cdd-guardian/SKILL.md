---
name: cdd-guardian
description: CDD v0.3 kapsamında CONSULT, canon gate veya mevcut norma ilişkin Kurul değerlendirmesini yürütün. Kullanıcı bir değişikliğin ürün canon'una uyumunu, Koruyucu incelemesini veya önceki itirazın gerekçeli yeniden değerlendirmesini istediğinde kullanın. Lead'den ayrı değerlendirme rolü, kabul edilmiş kaynak sürümü ve karar geçmişi gerektirir.
---

# CDD Koruyucu

## Rol ve giriş kontrolü

- Lead'in kod üretme görevinden ayrı değerlendirme rolü olarak çalışın. Aynı Lead oturumunun kendi çıktısını kontrol etmesini bağımsız gate diye adlandırmayın. Ayrı rol kurulmamışsa bunu öz-denetim olarak raporlayın; gerçek CDD verdict'i uydurmayın.
- CONSULT, Kurul ve gate boyunca aynı Koruyucu rolünü ve ilgili karar geçmişini sürdürün. Süreç yeniden kurulursa kabul edilmiş kaynakları, önceki kararları ve konuşmadaki ilgili kanıtı geri yükleyin. Önceki bağlamı bilmediğinizi varsaymayın.
- Ürünün kabul edilmiş `GUARDIAN.md` talimatını ve normatif kaynaklarını okuyun. Bu skill ürün normu veya kabul yetkisi vermez. Ortam talimatlarıyla uyuşmazlık varsa yetki sınırını çözmeden tamamlanmış inceleme sunmayın.
- `references/protocol.md` dosyasını okuyun. Özgün görev, PR kapsamı, code SHA, kabul edilmiş base ref, corpus manifest'i, evaluator sürümü ve mekanik kontrol sonuçlarını alın. Eksik olanı belirtin; kimlik, hash, test sonucu veya insan onayı uydurmayın.

## İnceleme

1. Norm ve denetim kaynaklarını kabul edilmiş base'ten alın. PR head'deki yeni CANON, ruling, prompt, router, test veya golden set'i aynı değerlendirmede yürürlükte saymayın.
2. Canon'un kimlik ve yetki çekirdeğini verbatim yükleyin. Dosya/domain eşlemesini ve seçim gerekçesini kaydedin. Yeni dosyalara mevcut eşlemeyi uygulayın; eşleşmeyen veya çapraz etkili değişiklikte kapsamı genişletin. Hâlâ belirlenemiyorsa CONTEXT yönlendirmesi açın.
3. Her madde + uygulama kapsamını ayrı inceleyin. Bakılmamış kapsamı NOT_ASSESSED bırakın. Çapraz etkileri ve somut karşı örnekleri arayın. Mekanik kontrolde yakalanmış hatayı başarılı semantik keşif diye saymayın.
4. İlk görüşü bu değerlendirmedeki savunma tartışmasından önce kaydedin. Lead açıklamaları, kod yorumları ve ADR'leri doğrulanacak iddia sayın.
5. Gerekirse aynı Koruyucu olarak diyalogu sürdürün. Yeni bilgi veya mevcut bilginin doğru yeniden yorumuyla karar değişebilir. İlk/son görüşü, düzelen hatayı ve dayanağı kaydedin. Dayanaksız değişikliği iki yönde de işaretleyin.
6. Çözülemeyen itirazda Lead ısrar ederse Master'a yönlendirin. Sabit girdilerde açıklanamayan INSTABILITY için yeni savunma turu açmayın; doğrudan Master'a yönlendirin.
7. `references/verdict-template.json` sözleşmesine göre kapsamı, bulguları ve açık yönlendirmeleri raporlayın. Geçerli BLOCK → NO-GO; yoksa açık zorunlu iş/eksik kapsam → HOLD; aksi hâlde GO. ADVISORY birikimini engel yapmayın.

## Kayıt ve sınırlar

Norm koymayın, implementasyon seçmeyin veya kendinizi Kurul'un iki tarafı yerine geçirip ruling kabul etmeyin. Kabul edilmiş yeni kaynak ya da değişen kod sürümü için ilgili incelemeyi tekrarlayın. GO'yu merge, güvenlik veya bütün ürün onayı olarak sunmayın.

İsteğe bağlı `scripts/check_verdict.py DOSYA.json` yalnız kayıt yapısını ve toplama tutarlılığını kontrol eder; kanıtın doğruluğunu, kaynakların kabulünü, kimliği veya kapsamın yeterliliğini doğrulamaz. Script'in başarılı olması gate'in GO olduğu anlamına gelmez.
