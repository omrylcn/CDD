---
name: cdd-init
description: CDD Faz 0 başlangıcını yeni veya mevcut bir projede hazırlayın; kullanıcı Canon-Driven Development kurulumu, CANON.md, GUARDIAN.md, AGENTS.md başlangıcı veya bir CDD örneğini projeye uyarlamak istediğinde kullanın. Taslak normları insan kabulünden ayırın ve mevcut dosyaları koruyun.
---

# CDD başlangıcı

1. Hedef projeyi ve mevcut `AGENTS.md` talimatlarını okuyun. Yeni bir ürün mü, mevcut ürüne uyarlama mı olduğunu belirleyin. Ürünün ne olduğunu eldeki kod ve insanın talebinden çıkarın; hayali örnek kuralları başka ürüne taşımayın.
2. `references/bootstrap.md` dosyasını okuyun. Ürün kimliği hakkında eksik bilgi varsa sınırlı bir taslak hazırlayın; bilinmeyeni norm gibi yazmayın.
3. Paket dizinine göre `scripts/init_cdd.py --target HEDEF --dry-run` çalıştırın. Çakışma varsa mevcut dosyaları okuyup birleştirme önerisi hazırlayın; script'in üzerine yazma yasağını aşmayın.
4. Çakışma yoksa aynı komutu `--dry-run` olmadan çalıştırın. Mevcut `AGENTS.md` için gerekirse yalnız başlangıçta `--skip-agents` kullanın ve gerekli CDD talimatlarını mevcut talimatlarla açıkça uzlaştırın. Bu seçenek CDD rol ayrımının kurulduğu anlamına gelmez.
5. `CANON.md` içindeki DRAFT alanlarını ürünün sahibiyle netleştirin. Script çıktısını, commit'i veya `ratified_by` metnini Master onayı saymayın. Kabul edilmeden `ACTIVE` yazmayın; onaylanan içerik sürümünü ve insan kararının doğrulanabilir kaynağını kaydedin.
6. Lead ve Koruyucu değerlendirme rollerini ortamın gerçekten desteklediği biçimde ayırın. Rol ayrımı kurulamadıysa mevcut ajanın ikinci okumasını CDD gate diye sunmayın; öz-denetim olarak etiketleyin.
7. İlk görev için kabul edilmiş base sürümünü, görev metnini ve incelenecek kod sürümünü kaydedin. Ayrı Koruyucu rolü için `cdd-guardian` paketini kullanın. Aynı Koruyucu ilgili geçmişle CONSULT, Kurul ve gate boyunca devam etsin.
8. Oluşan dosyaları, açık ürün kararlarını ve eksik entegrasyonları raporlayın. Bir ilk inceleme örneği hazırlayın; semantik doğruluk veya branch koruması kurulmuş gibi davranmayın.

Script yalnız dosya iskeletini kurar. Ajan çalıştırmaz, norm kabul etmez, PR onaylamaz ve CI engeli oluşturmaz.
