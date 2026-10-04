# Başlangıç kararları

## Gerekli bilgi

- Ürün hangi işi, kimin için yapıyor? Hangi ürün olmak istemiyor?
- Açık bir trade-off veya korunacak sınır var mı?
- Norm kabul edecek insan kim? Kararı ve kabul edilen içerik sürümü nerede doğrulanacak?
- Kod üreten Lead ile değerlendiren Koruyucu nasıl ayrılacak?
- Kabul edilmiş kaynaklar hangi ref'ten okunacak? Yeni kurulumda henüz böyle bir ref yoksa bunu açık yazın.

## İlk kabul

CANON başlangıçta DRAFT'tır. İnsan taslağı kabul ettiğinde norm metninin sürümünü, kararın kaynağını ve hangi kimliğin yetkili olduğunu ayrıca kaydedin. Metne yalnız bir kullanıcı adı yazmak kimlik doğrulama değildir. Ajanın insanın kabul yetkisini onun adına kullanamadığını ortamın izinleriyle sağlayın. Tek kişinin aynı platform kimliğiyle hem PR açtığı hem onay verdiği akışı otomatik bağımsız onay gibi sunmayın.

Sonraki gate kaynaklarını kabul edilmiş base ref'ten okuyun; PR head'deki CANON, GUARDIAN, ruling veya router değişikliği aynı incelemede kendiliğinden yürürlüğe girmez. Başlangıçta corpus küçükse tüm kabul edilmiş kaynakları yükleyin; domain router eklemek zorunlu değildir.

## Mevcut proje

Mevcut AGENTS veya CANON dosyasını değiştirmeden önce okuyun. Init script'inin çakışma raporunu, silme veya üzerine yazma izni saymayın. Var olan normların içeriğini kaybetmeden önerilen ekleri bir diff olarak hazırlayın. Kurulum talebi, yeni ürün ilkelerinin kabulü değildir.
