# v0.2 → v0.3 değişiklik özeti

Bu revizyon, birlikte hazırlanan v0.2 Türkçe taslağını temel alır. GitHub `main` dalındaki başlangıç metni hâlâ v0.1 olduğu için PR diff'i v0.1 → v0.3 görünür. Bu tablo yalnız son değerlendirmede sabitlenen v0.2 → v0.3 farkını açıklar.

| Bölüm | Değişiklik | Sonuç |
|---|---|---|
| §0.1 | Okuma yolu, rol tablosu, günlük döngü ve kısa sözlük | Okur ana akışı ayrıntılı kurallardan önce görür |
| §2 ve §2.3 | Katmanlar ile ruling yaşam döngüsü tabloya çevrildi | Otorite ve yürürlük durumu metin ağacı olmadan karşılaştırılır |
| §3.1 ve §8 | Üç parçalı sınır cümlesi başa alındı | Ajanlar üzerindeki sınır ile Master'ın karar sorumluluğu ayrılır |
| §3.1, §4 | Açık PR'a bağlı amendment kaydı ve ayrı kabul | NO-GO öncesi önerilen değişiklik de ilişkilendirilir; yeni norm eski verdict'i taşımaz |
| §3.1.1, §11 | Master iş kuyruğu; sınıf bazında açık iş sayısı ve yaşı | Kayıt üretme ile gerçekten inceleme yapma ayrılır |
| §3.3, §3.4, §3.6 | Yetki ayrımı ile hata bağımsızlığı ayrıldı; kesin korelasyon ifadeleri yumuşatıldı | Aynı Koruyucu ve gerekçeli diyalog korunurken ortak kör nokta sınırı açık kalır |
| §6, §10 | Kapsam seçimi kaydı ve eşleşmeyen / çapraz etkili değişiklik yolu | Yeni dosya mevcut kuralla eşleşebilir; çözülemeyen kapsam GO alamaz |
| §11 | Ortak kaçırma; diyalog öncesi/sonrası ve kaynak/yorum hatası ayrımı | İhlale GO, HOLD ve yanlış gerekçeli NO-GO birbirine karışmaz |
| §10 | Sade kullanımda kalma ve katman geri çekme | Korumanın nerede sürdüğü veya kabul edilen risk kaydedilir |
| §8, Ek A | Tarihsel örnekler eke taşındı; genelleyici kuruluş amacı hükmü kaldırıldı | Ana akışın yükü azalır; analoji doğruluk kanıtı sayılmaz |
| §9.7 | Başlangıç dosyaları sayımı düzeltildi | CANON, GUARDIAN, RULINGS ve gate talimatı tutarlı listelenir |

## Altı diyagram

1. Günlük geliştirme döngüsü (§0.1).
2. Açık PR'a bağlı amendment'ın kabulü ve tekrar gate (§3.1).
3. Aynı Koruyucu ile gerekçeli itiraz (§3.3).
4. Kabul edilmiş kaynak ile PR head arasındaki sınır (§4.2).
5. Bulgulardan GO / NO-GO / HOLD sonucuna geçiş (§6).
6. Normatif soruda kaynak eksiği, norm boşluğu ve yorum belirsizliği (§6).

Markdown'da Mermaid kaynakları bulunur. `docs/cdd-v0.3.tr.html` aynı metni gömülü SVG diyagramlarla, dış servis veya JavaScript gerektirmeden gösterir. Uzun hüküm listelerinde tablolar, prosedürde diyagramlar, veri örneklerinde kod blokları korunur.

## Başlangıç paketi

- Depoyu geliştiren ajanlar için kök `AGENTS.md`; hedef ürüne kopyalanacak ayrı AGENTS şablonu.
- `skills/cdd-init`: çakışmada yazmayan, DRAFT dosyalar üreten başlangıç script'i ve skill.
- `skills/cdd-guardian`: ayrı değerlendirme rolü, aynı Koruyucu geçmişi, kaynak sınırı, diyalog ve verdict sözleşmesi.
- `docs/getting-started.tr.md`: ilk norm kabulünden ilk incelemeye kadar kullanım.
- `examples/coordination`: altı sentetik gate kaydı ve gerekçeli düzeltme senaryosu.
- `tests/test_starter.py`: dosya koruması, tekrar çalıştırma, symlink sınırı ve verdict toplama kontrolleri.

Script ve kayıt kontrolleri bir semantik judge'ın performansını ölçmez. Kimliğe bağlı insan onayı, ajan orkestrasyonu ve gerçek PR enforcement ayrıca kurulmalıdır. İngilizce v0.1 metin korunmuş ve eski sürüm olarak etiketlenmiştir; v0.3 çevirisi tamamlandı iddiası yoktur.
