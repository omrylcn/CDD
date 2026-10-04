# Canon-Driven Development

> As code gets cheaper, the real problem stops being writing code; it becomes keeping the system the same thing across thousands of small changes.

CDD, ajanlarla geliştirilen bir ürünün kimliğini küçük değişiklikler boyunca korumaya yönelik bir yönetişim önerisidir. Lead uygular, Koruyucu canon'a göre değerlendirir, Müfettiş süreci raporlar; normu insan Master koyar. Aynı Koruyucu gerekçeli diyaloğu sürdürür; çözülemeyen itirazda Lead ısrar ederse Master'a gidilir.

**Güncel sürüm: v0.3 — Türkçe.** Yöntemin faydası henüz doğrulanmış bir sonuç olarak sunulmaz.

| İhtiyaç | Başlangıç |
|---|---|
| Yöntemi ve akışları anlamak | [Türkçe metin, altı Mermaid diyagramıyla](canon-driven-development.md) |
| Tarayıcıda diyagramlı okumak | [Tek dosyalık HTML](docs/cdd-v0.3.tr.html) — indirip tarayıcıda aç |
| Bir projede Faz 0 başlatmak | [Kurulum rehberi](docs/getting-started.tr.md) |
| Skill paketleri | [cdd-init](skills/cdd-init/SKILL.md), [cdd-guardian](skills/cdd-guardian/SKILL.md) |
| İlk gate örneklerini görmek | [Koordinasyon örneği](examples/coordination/README.md) |
| v0.2 → v0.3 değişiklikleri | [Değişiklik özeti](docs/changes-v0.3.tr.md) |
| Eski İngilizce metin | [v0.1 English](canon-driven-development.en.md) — v0.3 ile eşdeğer değildir |

## Hızlı başlangıç

Python 3.10+ yeterlidir; başlangıç araçlarının dış bağımlılığı yoktur.

```bash
python3 skills/cdd-init/scripts/init_cdd.py --target ../benim-urun --dry-run
python3 skills/cdd-init/scripts/init_cdd.py --target ../benim-urun
```

Script DRAFT dosyalar üretir; mevcut dosyaları ezmez. İnsan norm kabulü, ayrı Koruyucu rolü ve platformdaki izin/CI düzeni ayrıca kurulmalıdır. Skill paketleri hedef ajana ayrıca yüklenir; bu repo onları kişisel skill dizinine otomatik kurmaz.

## Kontrol

```bash
python3 -m unittest discover -s tests -v
python3 skills/cdd-guardian/scripts/check_verdict.py examples/coordination/verdicts/block.json
```

İkinci komut kayıt sözleşmesini kontrol eder; örnekte CANON_GATE=NO-GO'dur. Başarılı script çıkışını merge onayı diye kullanma. Sentetik örnekler model performansı veya gerçek ürün sonuçları değildir.
