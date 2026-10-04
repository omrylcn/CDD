# CDD deposunda çalışma

Bu depo CDD yöntemini, başlangıç şablonlarını ve örneklerini içerir. Hayali koordinasyon uygulamasının canon maddeleri bu deponun ürün kuralları değildir.

- Güncel Türkçe kaynak `canon-driven-development.md` (v0.3); İngilizce metin etiketlenmiş v0.1 arşividir. Eşdeğer çeviri olduklarını varsayma.
- Özgün anlatımı ve bölüm numaralarını koru. Protokol değişince ilgili skill, şablon, örnek ve diyagramı birlikte güncelle.
- Aynı Koruyucu rolü CONSULT, Kurul ve gate boyunca ilgili karar geçmişini taşır. Lead gerekçesi doğrulanacak iddiadır; norm veya bağımsız onay değildir.
- `CANON_GATE` ile merge kararını ayır. Geçerli BLOCK → NO-GO; yoksa açık zorunlu iş veya eksik kapsam → HOLD; aksi hâlde GO. ADVISORY birikimi otomatik engel değildir.
- Örnek onayları gerçek Master onayı gibi üretme. Scaffold DRAFT'tır; gerçek kabul, insan kimliği ve içerik sürümüne bağlı ayrı olaydır.
- Skill'ler `skills/` altında taşınabilir paketlerdir. Kullanıcının kişisel skill dizinine otomatik kurulum yapma. Hedef proje talimatı `skills/cdd-init/assets/templates/AGENTS.md` içindedir.
- Başlangıç script'i mevcut dosyaları sessizce ezmemeli; çakışmada yazmadan çıkmalıdır.
- `python3 -m unittest discover -s tests -v` çalıştır. Belgelerdeki göreli bağlantıları ve Mermaid diyagramlarını değişiklik kapsamına göre kontrol et.
- Kullanıcı istemedikçe merge veya release yapma. Çalışmayı branch ve incelenebilir PR olarak hazırla.
