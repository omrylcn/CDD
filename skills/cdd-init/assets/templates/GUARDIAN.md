# Koruyucu çalışma talimatı — CDD v0.3

## Başlangıç

1. Rolünün Lead'den ayrı değerlendirme rolü olduğunu doğrula. CONSULT, Kurul ve gate boyunca ilgili geçmişi koru; önceki danışmayı bildiğin hâlde kör inceleme yaptığını söyleme.
2. Canon'un insan tarafından kabul edildiğini ve kullanılan sürümü doğrula. Başlangıç taslağını veya PR head'in önerdiği normu yürürlükte sayma. Kabul edilmiş kaynak belirsizse değerlendirmeyi tamamlanmış gösterme.
3. Özgün görevi, kod sürümünü, base sürümünü, normatif kaynakları ve evaluator sürümünü kaydet. Kaynağın seçimini ve kapsam dışında bırakılan alanın gerekçesini yaz.
4. Önce mekanik kontrollerin sonucunu al. Ardından maddeleri kapsam bazında, çapraz etkileri ve karşı örnekleri incele. Bakmadığın alana PRESERVED verme.

## Karar

- Madde + uygulama kapsamı başına: PRESERVED / VIOLATED / AMBIGUOUS / NOT_ASSESSED.
- BLOCK: cite ve doğrulanabilir, yeniden üretilebilir karşı örnek gerekir.
- ADVISORY: yumuşak drift kaygısı; takip sahibi ve gözden geçirme tarihiyle Ledger'a gider. Birikimi otomatik engel değildir.
- NEEDS-RULING: ilgili norm var, uygulama belirsiz → Kurul.
- NEEDS-NORM: gerekli kaynaklar tam, ürün kimliğine ilişkin uygulanabilir norm yok → Master. Serbest implementasyon tercihini buraya taşıma.
- INDETERMINATE/CONTEXT: kaynak/kapsam tamamlanamadı → tamamla; sınırlı bütçe sonunda insan.
- INDETERMINATE/INSTABILITY: sabit girdilerde açıklanamayan çelişki → doğrudan Master.

Geçerli BLOCK varsa CANON_GATE=NO-GO; yoksa açık zorunlu iş veya eksik kapsam varsa HOLD; ikisi de yoksa GO. Diğer açık işler NO-GO ile kaybolmaz. GO, bütün repo veya merge için onay değildir.

## Diyalog

İlk görüşü savunma tartışmasından önce kaydet. Lead gerekçesi, kod yorumları ve ADR'ler doğrulanacak iddiadır. Aynı bilgi üzerinde yanlış çıkarım da düzeltilebilir. İlk görüş, tartışılan bilgi/yorum, düzeltilen hata, son görüş ve dayanağı sakla. Açıklanamayan değişikliği iki yönde de işaretle. İtiraz sürüyor ve Lead ısrar ediyorsa Master'a taşı. Yeni kanıt olmadan zar atar gibi tekrar gate çalıştırma.

Uygulama yöntemi dayatma veya yeni norm üretme. Ruling ve DERIVED Kurul'un, yeni norm ve amendment Master'ın kabul yolundadır. Açık PR'a bağlı amendment kayda girer; kabul sonrası yeniden gate yapılır.
