# İnceleme protokolü

## Kaynaklar

Kabul edilmiş kaynak sürümü dışarıdan doğrulanmalıdır. `git show <base>:CANON.md` bir sürümün içeriğini gösterir; insanın o sürümü kabul ettiğini kanıtlamaz. PR head'deki norm veya denetim değişiklikleri tekliftir. Yetkili kabul ayrı olaydır; eski verdict yeni kaynağa taşınmaz.

Kaynak seçimini dosya/domain → kural → kitap/ruling biçiminde kaydedin. Faz 0'da tüm küçük corpus yüklenebilir. Gerekli kapsam hâlâ belirlenemiyorsa GO vermeyin. Kaynak haritası doğru görünse bile çapraz etkiyi inceleyin. Kaynak manifest'inin tam olması semantik kapsamın tam olduğunu kanıtlamaz.

## Gate sonucu ve açık işler

| Alan | Anlamı |
|---|---|
| GO | Zorunlu kapsam tamam; geçerli ihlal veya açık zorunlu iş yok |
| NO-GO | En az bir geçerli BLOCK var; diğer açık işler kayıtta kalır |
| HOLD | Geçerli BLOCK yok; zorunlu kapsam veya karar tamamlanmadı |
| NEEDS-RULING | Uygulanabilir norm var, vaka yorumu belirsiz; cite ile Kurul'a |
| NEEDS-NORM | Kaynak tam; ürün kimliğine ilişkin uygulanabilir norm yok; Master'a |
| CONTEXT | Gerekli kaynak veya kapsam kurulamadı; tamamla, çözülemezse insana |
| INSTABILITY | Sabit girdilerde açıklanamayan çelişki; doğrudan Master'a |

BLOCK cite ve yeniden üretilebilir karşı örnek gerektirir. Kararsız BLOCK adayı geçerli BLOCK sayılmaz. Başka doğrulanmış BLOCK varsa NO-GO sürer. AMBIGUOUS ve zorunlu NOT_ASSESSED sessizce geçmez. Serbest implementasyon tercihi NEEDS-NORM değildir.

## Diyalog

İlk hüküm, Lead'in itirazı, tartışılan kanıt/yorum, düzeltilen hata ve son hükmü bağlayın. İlk görüşün önceki CONSULT geçmişinden bağımsız olduğu iddiasında bulunmayın. Kanıtsız baskıyı norm saymayın; yeni kanıt olmadan tekrar gate çağırarak GO aramayın. Aynı bilginin yanlış okunması yeni bilgi gelmeden de düzeltilebilir.

Yetki ayrımı hata bağımsızlığı değildir. Bu paket model korelasyonunu veya Master'ın yanlış kararını ortadan kaldırmaz. Otomatik enforcement için ayrıca sürüme bağlı güvenilir karar üretimi, yetkili onay, branch koruması ve platform izinleri gerekir.
