# Canon-Driven Development

### Agentic yazılım geliştirmede kimliğin korunması için bir insan–ajan yönetişim önerisi

*v0.1 — initial proposal*

> Kod ucuzladıkça asıl problem kod yazmak olmaktan çıkar; sistemin binlerce küçük değişiklik boyunca **aynı şey olarak kalması** olur.

---

## 0. Tek paragraf

CDD, bir yazılım sisteminin **kimliğini** — ne olduğu, ne olmadığı, nasıl davrandığı — kodun dışında, kısa ve verbatim bir metinde tutar: **Canon**. Canon'dan türeyen **Alt Kitaplar** ve tek tek vakalarda verilmiş **Ruling**'ler ikinci ve üçüncü katmanı oluşturur. Dört rol vardır: kodu üreten **Lead** ajan, canon'a tek sadakati olan ve yalnızca veto yetkisi taşıyan **Koruyucu** ajan, süreci denetleyip yalnızca rapor yazan **Müfettiş** ajan, ve Canon'un sahibi ve koyucusu olan insan **Master** — Canon'un ne anlama geldiği ve ne zaman değişeceği üzerindeki nihai otorite. Lead inşa eder, Koruyucu korur, Müfettiş denetler; hiçbiri Master'ın yerine Canon yaratamaz. Önerinin çekirdeği canon dosyası değil, yetkilerin ayrılmasıdır: **builder kendi hakemi olamaz.**

---

## 1. Bağlam ve öneri

Bu öneri yeni bir şey keşfettiğini iddia etmiyor; birkaç mevcut fikrin üzerine bir yetki topolojisi kuruyor.

**Üzerine inşa ettiklerimiz:**

- *Architectural fitness functions* — mimariyi CI'da assert edilebilir kurallara indirme fikri.
- *ADR'ler* — kararların gerekçesiyle birlikte kaydedilmesi.
- *DDD ubiquitous language* — sistemin kendi kavramlarıyla çelişmemesi.
- *Spec-Kit constitution* — projeyi yöneten ilkelerin ayrı bir dosyada tutulup spec/plan/implement aşamalarında compliance kontrolü yapılması.
- *Constitutional Spec-Driven Development* (Marri, 2026) — non-negotiable ilkelerin spec katmanına gömülmesi; güvenlik odaklı.
- *Specification Governance Reference Model* (Alenezi, 2026) — stokastik generator'ın deterministik bir validation boundary içine yerleştirilmesi.

Bunların ortak deseni tek bir boru hattıdır: `constitution → generation → compliance`. Compliance'ı çoğunlukla ya mekanik kurallar ya da üreten ajanın kendisi yapar.

**Hedeflediğimiz boşluk** iki tane:

1. Fitness function'lar mekanik olmak zorundaydı. "Bu ekran kullanıcıyı yanlış mental modele götürüyor mu?" sorusu makineleşemiyordu. LLM'ler **semantik fitness function**'ı ucuzlattı; ama bunu üreten ajana sorarsan builder bias'ı cevabı belirler.
2. Constitution'ı *kimin yorumladığı* çoğu yaklaşımda tanımsız. Yorum yetkisi tanımsızsa ya builder kendine hakemlik eder ya da her yorum insana döner.

**Önerdiğimiz şey:** canon'u yorumlama, uygulama ve denetleme yetkilerini ayrı ajanlara vermek; yorum otoritesinin sahibini insan olarak sabitlemek; ve bu yetkilerin hangi durumda kime geçtiğini açık bir haritayla belirlemek.

Korunan invariant tek cümle: **hiçbir ajan hem normu yaratıp, hem uygulayıp, hem kendi uygulamasını onaylayamaz.** "Builder kendi hakemi olamaz" bunun en sık karşılaşılan hali; Koruyucu'nun norm üretememesi ve Müfettiş'in yetkisiz olması aynı invariant'ın diğer yüzleri.

---

## 2. Üç katman

```
CANON             kısa · verbatim · nadir değişir · her context'e girer
  └─ ALT KİTAPLAR    domain bazlı · detaylı · isnad'lı · on-demand yüklenir
       └─ RULINGS      vaka bazlı · kronolojik · terfi edebilir · eskiyebilir
```

Otorite yukarıdan aşağı akar: **canon > alt kitap > ruling, her zaman.** Alt bir katman üst katmanı ne özel olduğu için ne yeni olduğu için ezemez. Terfi aşağıdan yukarı: tekrar eden ruling'ler alt kitaba, nadiren alt kitap maddeleri canon'a yükselir.

### 2.1 Canon

Canon, ürünün kimliğidir: ne olduğu, ne olmadığı, kullanıcıya nasıl davrandığı, hangi trade-off'ta hangi tarafı seçtiği ve asla yapmayacakları. Bir sayfalık, numaralı maddelerden oluşan, ürünün sahibi tarafından yazılmış bir metindir. Feature listelemez; feature'ları sınırlar. "Yetki yalnız sunucu tarafında belirlenir" ya da "günlük kullanıcı yüzeyi ile yönetici yüzeyi ayrıdır" gibi cümleler canon'dur — bir developer bunları ihlal eden temiz, test edilmiş, çalışan kod yazabilir ve ürün yine de kendisi olmaktan çıkar. Canon tam olarak bunu yakalamak için vardır: testlerin göremediği "hâlâ aynı ürün mü?" sorusunun cevabı. Her ajanın context'ine olduğu gibi girer ve nadiren değişir.

Canon bir SPEC değil; ürünün anayasasıdır. İçeriği:

- Ürün nedir / ne değildir
- Değişmez ilkeler — kısa, numaralı (`C-01`, `C-02` …)
- Trade-off'larda hangi taraf seçilir
- Asla yapılmayacaklar
- **Yorum ve değişiklik yetkisinin kimde olduğu** (§4)
- **Alt kitap haritası**: hangi domain'e dokununca hangi kitap yüklenir
- **Apokrif listesi**: canon sanılması muhtemel olduğu için ayrıca işaretlenen belgeler. Normatiflik allow-list'tir: yalnız alt kitap haritasında listelenen dosyalar normatiftir; listede olmayan her şey varsayılan olarak apokriftir

Canon kuralları:

1. **Üründen kopuk yazılmaz.** Asıl hali çekirdekten büyütülen bir `principles.md`'dir: ilke yazılır, ona göre inşa edilir. Olgun bir codebase için fallback, canon'u mevcut üründen çıkarmaktır — hayalden yazmak değil; aksi halde kod ve canon iki ayrı gerçek kaynağına dönüşür. Repo'daki diğer belgeler canon değildir ve apokrif olarak işaretlenir.
2. **İlke lifecycle'ı:** `DRAFT → Master onayı → CANON → implemented/verified`. Bir ilkenin kodda uygulanması onun *uygulandığının* kanıtıdır, *doğru olduğunun* değil. Normatif adım Master'ın onayıdır; tek kişilik projede bu, ilkeyi yazmakla aynı andır — ama Lead'in teklif ettiği bir ilke için ayrı bir adımdır.
3. **Verbatim girer, özetlenmez.** Hiçbir ajan canon'u kendi özetiyle context'ine almaz. Her paraphrase bir kopist hatasıdır.
4. **Canon içi çelişki otomatik çözülmez.** İki madde çelişiyorsa gate kapanır; explicit amendment gerekir. "Geç madde erkeni ezer" kuralı canon içinde **yoktur** — olsaydı dosya sırası anayasal değişiklik mekanizmasına dönüşürdü.
5. **Değişiklik iz bırakır.** Amendment metadata taşır:
   ```
   C-17
     supersedes  : C-04
     ratified_by : Master
     date        : 2026-09-02
   C-04  [SUPERSEDED BY C-17]
   ```
   Eski madde görünür kalır.
6. **Kısa kalır.** Bir sayfa hedef. Detay alt kitaba iner.

Örnek — bu dokümandaki bütün örnekler aynı hayali üründen: üyelerin tek bir yönetici altında çalıştığı, günlük kullanım yüzeyi (**Everyday**), talep üzerine açılan yüzey (**On-Demand**) ve yönetim yüzeyi (**Operator**) birbirinden ayrı tutulan bir koordinasyon uygulaması:

> **C-04** — Authority isimden veya client payload'dan türetilemez; yalnızca server-derived'dır.
>
> **C-09** — Everyday, On-Demand ve Operator birbirinden farklı interaction surface'leridir; tek generic dashboard altında birleştirilemez.

### 2.2 Alt Kitaplar

Alt kitaplar, canon'daki bir ilkenin belirli bir domain'de ne anlama geldiğini açan, daha uzun ve daha somut metinlerdir. Canon "authority server-derived'dır" der; auth alt kitabı bunun legacy uyumluluk path'lerinde, token yenilemede, admin bootstrap'inde tek tek ne demek olduğunu yazar. Hâlâ "ne / ne değil" konuşurlar, "nasıl" konuşmazlar: implementasyon seçmezler, sınır çizerler. Domain bazlı bölünürler çünkü canon her context'e girer, alt kitaplar yalnız ilgili domain'e dokunulduğunda yüklenir. Her maddesinin kaynağı bellidir: ya hangi canon ilkesinden türediği (DERIVED) ya da Master'ın onayıyla ve hangi ilkelerle tutarlı olarak girdiği (NEW NORM). Kaynağı gösterilemeyen madde ya oraya ait değildir ya da canon'da eksik vardır. Kurul yazar, yeni normu Master onaylar; canon'un altında dururlar.

Domain bazlı (`auth`, `surfaces`, `data-model` …). Her madde bir **isnad** — türetme zinciri — taşır. Ve her madde iki türden biridir:

```
S-AUTH-12
  tür        : DERIVED
  canon      : C-04
  doğuran    : R-031 (stale client role=master vakası)
  tarih      : 2026-08-14
  madde      : Legacy compatibility path'leri client-originated role hint'i kabul etmez.
```

```
S-SURF-21
  tür              : NEW NORM
  source           : MD-014 (Master kararı)
  ratified_by      : Master
  consistent_with  : C-09
  tarih            : 2026-08-30
  madde            : On-Demand surface'te oturum 30 dakika hareketsizlikten sonra kapanır.
```

| Tür | Tanım | Kim doğrular | Kim onaylar |
|---|---|---|---|
| **DERIVED** | Mevcut bir canon maddesinin operasyonel açılımı; canon'dan cite ile türetilebilir | Koruyucu | Kurul |
| **NEW NORM** | Canon'un söylemediği yeni bir davranış getiriyor | Koruyucu "yeni norm" der | **Master** |

Bu ayrım olmadan alt kitap bir privilege-escalation yoludur: Lead + Koruyucu, canon'un söylemediği bağlayıcı kurallar üretebilir. Ayrımı Koruyucu yapar ve Lead'in "yeni normu türetilmiş gibi yazmayı" öğrenmesi gerçek bir risk olduğu için Müfettiş DERIVED sınıflandırmalarını örnekler. Her maddenin provenance'ı vardır, ama her maddenin canon'dan türetmesi olmak zorunda değildir: NEW NORM'un meşruiyeti türetme değil, Master'ın açık onayıdır — yine de canon'la çelişemez, `consistent_with` bunu cite eder.

İsnad'ın mekanik kontrolü CI'dadır: referans verilen madde var mı, SUPERSEDED değil mi, alıntılanan metin canon'daki metinle birebir aynı mı. NEW NORM için: `ratified_by` dolu mu, `consistent_with` maddeleri var mı. Bu kontrol türetmeyi doğrulamaz — onu kör yeniden türetme yapar (§3.4) — ama uydurma ID'yi ve neshedilmiş maddeye dayanmayı anında yakalar. Vektör benzerliği hiçbirinin yerine geçmez.

Alt kitaplar arası öncelik kuralları baştan yazılır:

- **lex superior** — üst kaynak kazanır; koşulsuz
- **lex specialis** — özel kural genel kuralı ezer; **yalnızca aynı otorite seviyesinde** (alt kitap vs alt kitap, ruling vs ruling)
- **lex posterior** — aynı seviyede yeni eskiyi ezer; canon içinde geçersiz

İsnad iki iş görür: türetilemeyen madde ya canon'da boşluk var demektir ya da madde oraya ait değildir (**boşluk tespiti**); doğuran kaygı ortadan kalktığında madde emekliye ayrılır (**budama**). Alt kitapların canon'dan yüz kat büyük olması sorun değil; isnadsız büyümesi sorundur.

### 2.3 Rulings

Ruling, ilgili bir normun var olduğu ama vakaya nasıl uygulanacağının belirsiz olduğu bir durumda verilmiş tek bir yorum kararının kaydıdır. Lead bir şey yapmak ister, "bu C-09'a uyar mı?" diye sorar; madde vardır ama bu vakayı açıkça kapsamamaktadır; birinin yorumlaması gerekir. O yorum, gerekçesiyle birlikte `RULINGS.md`'ye bir satır olarak yazılır ki aynı soru bir daha sıfırdan yorumlanmasın. Ruling yeni kural koymaz; var olan maddenin bu vakada ne dediğini söyler. Uygulanabilir hiçbir madde yoksa bu ruling'in işi değildir — boşluktur ve Master'a gider. Aynı türden ruling'ler birikince artık tek vaka değil kural demektir ve alt kitaba çıkar; koşulları değişince eskir. En hafif, en hızlı, en geçici katmandır.

İlgili bir norm var ama vakaya nasıl uygulanacağı belirsiz — yorumun yapıldığı yer burasıdır. Ruling bir **Kurul kararıdır**:

1. Lead sorar; Koruyucu "belirsiz" der, belirsiz olan maddeyi cite eder ve durur.
2. Lead bir yorum teklif eder.
3. Koruyucu teklifi cite edilen maddeye karşı kontrol eder: maddenin bir okuması mı, yoksa maddenin söylemediği bir şey mi.
4. Okumaysa ve uzlaşılırsa → ruling, `RULINGS.md`'ye girer. Master'a gitmez; Master log'u görür ve **geri çekme hakkı** vardır.
5. Koruyucu hayır der ve Lead ısrar ederse → Master.
6. Berabere → statüko.

Koruyucu "boşluk" derse — hiçbir madde uygulanmıyorsa — ruling yoktur. Kurul yorumlayacak bir şey bulamaz ve norm yaratamaz. Vaka NEEDS-NORM olarak Master'a gider; Master ya alt kitaba NEW NORM olarak ekler ya da kimlik seviyesindeyse canon amendment açar. Üçlü şudur: **Koruyucu yorumlar, norm üretmez. Kurul yorumlar, norm üretmez. Yalnız Master norm koyar.**

Belirsiz ile boşluğu ayıran şey cite'tır: belirsizlik iddiası bir madde numarası taşımak zorundadır; taşıyamıyorsa boşluktur. Bu, Koruyucu'nun boşluğu belirsizlik gibi sunup vakayı Master yerine Kurul'a yönlendirmesini engeller; Müfettiş NEEDS-RULING'leri örnekler.

Bunun adı **delegated interpretive authority**: Master yorum otoritesinin sahibidir; rutin yorum yetkisini Kurul'a devreder ve her ruling üzerinde geri çekme/nesih yetkisini korur. Master nihai otorite, Kurul birinci derece yorumcudur. Devir örtük değildir — canon'un yetki maddesinde yazılıdır ve amendment'la daraltılabilir. Böylece yorum hafif ve hızlı kalır, otorite yine insanda kalır.

Her ruling bir lifecycle taşır:

```
ACTIVE
  ├── PROMOTED     tekrar etti, alt kitaba yükseldi
  ├── SUPERSEDED   yeni bir ruling ya da madde yerini aldı
  ├── EXPIRED      koşulları değişti, eskidi
  └── ARCHIVED     tekil kaldı, kayıt için tutuluyor
```

Yalnız ACTIVE ruling'ler normatiftir. Aktif bir ruling geçici otoritedir, sonsuza dek donmuş içtihat değil. Lifecycle geçişleri tek tek bürokrasi olmasın diye AUDIT loop'u PROMOTE/EXPIRE adaylarını toplu önerir, Kurul toplu onaylar. Log, "buna daha önce böyle karar verilmişti" makinesine dönüşmemeli — içtihat kapısı kapanırsa sistem donar.

### 2.4 Ne ve nasıl — normatif olan ve olmayan

Üç katmanın tamamı **normatif**tir: ürünün ne olduğunu ve ne olmadığını söyler. **Nasıl** yapılacağını söylemez. "Nasıl" Lead'in işidir; alt kitapta implementasyon ayrıntısı yoksa bu "sessiz" değil, **serbestlik**tir. Her implementasyon detayı için ruling istenirse sistem kilitlenir.

Lead'in uygulayacağı tek test:

> **Bu soruya verilecek cevap ürünün ne olduğunu değiştirir mi?**

```
"Authority'yi hangi middleware'de derive edelim?"            → hayır → Lead karar verir
"Bulk assignment queue ile mi, transaction ile mi?"           → hayır → Lead karar verir
"Operator'a member listesi gösterelim mi?"                    → evet  → CONSULT (C-09)
"Bulk role assignment olsun mu?"                              → evet  → CONSULT
```

Normatif madde implementasyon **uzayını daraltır**, tek bir implementasyon seçmez. "Client-originated role hint hiçbir authority decision path'ine ulaşamaz" normdur; "middleware X kullan" değildir. Compliance condition'ın yalnız hedef durumu söylemesi de bu yüzdendir: yöntem bilinçli olarak Lead'e bırakılır.

"Nasıl"ın yaşadığı yer dördüncü, **normatif olmayan** katmandır:

```
CANON > ALT KİTAP > ACTIVE RULING     normatif — ne / ne değil

TEKNİK DOKÜMANLAR                     normatif değil — nasıl
  ADR'ler, design doc'lar, kod        Lead'in malı; canon açısından apokrif
                                      Koruyucu bağlam için okur, norm olarak cite etmez
```

İki failure mode:

- **Aşırı danışma** — Lead her detayı CONSULT'a taşır, NEEDS-RULING seli olur. Ucuzdur, kendini gösterir.
- **Eksik danışma** — normatif bir karar "teknik tercih" kılığında geçer, kimse sormaz. Tehlikeli olan budur. Breaker pass ve audit yakalar; Müfettiş, Lead'in "operasyonel" diye kendi verdiği kararları örnekler.

Ters yönde de bir drift vardır: alt kitap "nasıl" yazmaya başlarsa spec'e dönüşür. Alt kitap maddesi bir implementasyon seçiyorsa Koruyucu bunu isnad kontrolünde işaretler — canon'dan norm türer, yöntem türemez.

---

## 3. Roller

### 3.1 Master — insan

Canon'un sahibi ve koyucusu. Canon'un ne anlama geldiği ve ne zaman değişeceği üzerindeki nihai otorite. Her PR'ı okumaz; **kimlik kararlarını** verir. Devreye girdiği yerler: canon-tier değişiklik (Kurul uzlaşsa bile), NEW NORM onayı, veto itirazı, Kurul'da beraberlik, audit ve teftiş sonuçları.

Buradaki "Master" teknik anlamda master node/branch değil; canon üzerinde **kurucu iktidara** sahip kişi. Hukuktaki ayrım birebir uyar: Master *kurucu iktidar*dır — canon'u ilk kez koyar ve amendment'ı ratify eder. Lead, Koruyucu ve Müfettiş *kurulmuş iktidar*lardır — canon'un verdiği yetkilerle çalışırlar ve hiçbiri Master'ın yerine canon yaratamaz.

```
MASTER
  │  koyar / yorumlar / değiştirir
  ▼
CANON
  ├── Lead      → uygular
  ├── Koruyucu  → korur
  └── Müfettiş  → süreci denetler
```

**Master Canon'un üstündedir; ajanlar değildir.** Uygulama notu: bazı projelerde "master" aynı zamanda bir domain terimidir (örnek üründeki single-master invariant gibi); agent-facing dosyalarda rol adı ile domain terimi açıkça ayrışmalıdır.

**Master Koruyucu'yu override edebilir; Canon'u ancak değiştirerek aşar.** Bu, önerinin en önemli cümlelerinden biridir ve iki durumu kesin ayırır:

```
Koruyucu yanlış yorumladıysa
  → Master verdict'i override eder, gerekçesi RULINGS'e girer, canon değişmez.
  → Override, Koruyucu'nun precision metriğine ve Müfettiş'in örneklemesine girer.

Koruyucu doğru yorumladıysa ve değişiklik canon'u gerçekten ihlal ediyorsa
  → Master ruling ile merge edemez.
  → Ya implementasyon değişir, ya Master canon'u açık bir egemenlik işlemiyle değiştirir.
```

Somut olarak:

```
Koruyucu:  C-04 ihlali → NO-GO

Master:
  "merge et"                                          ✗  sessiz override; canon delinir
  "C-04'ü değiştiriyorum, amendment aç"               ✓  egemenlik işlemi; canon değişir
  "C-04 için bu vakaya istisna, canon'a yaz"          ✗  canon vaka biriktirmez
  "72 saatlik acil istisna, Ledger'a, audit'i kilitle" ✓  borç; süreli, denetlenir
```

Master canon'u istediği an değiştirebilir; sahibi odur. Kuralı **değiştirmek** yerine tek bir vakada sessizce **delmek** ise canon'u o günkü karara indirger — o an ajanlar için bağlayıcı olan şey artık canon değil, Master'ın son kararıdır ve canon işlevini kaybeder. Egemenlik açık işlemle kullanılır: amendment, nesih. Sahibi kuralı değiştirir, delmez.

**Acil istisna**, amendment ve nesihle aynı sırada bir egemenlik işlemi *değildir*; tek vakayı kuralın dışına çıkarır ve normalleşirse endüljans geri gelir. Bu yüzden yalnız şu koşullarla vardır: human-only, süreli, gerekçeli, `LEDGER.md`'de açık kalem, bir sonraki audit'i kilitler, kapanışı yalnız revert veya amendment'tır, Müfettiş zorunlu denetler. Bir ruling değil, **kimlik borcudur**. Sürtünmesi bilinçlidir.

**Acil istisna normatif kaynak değildir.** Cite edilemez, isnad olamaz, bir ruling'in ya da alt kitap maddesinin gerekçesi olarak kullanılamaz, precedent oluşturmaz. "Daha önce yapılmıştı" bir argüman değildir.

```
CANON > ALT KİTAP > ACTIVE RULING          normatif corpus

LEDGER (istisnalar, tolerated deviations)  ≠ normatif corpus; veri, norm değil
```

### 3.2 Lead — ajan

Kodu tasarlar, üretir, teklif eder. Kurul'da oy sahibidir; canon-tier değişikliği ve yeni normu tek başına yapamaz. Bias'ı işi tamamlamaktır ve bu bilinçli olarak kabul edilir — dengeyi Koruyucu sağlar.

Lead inşa etmeden önce, ürünün ne olduğunu değiştiren her soru için Koruyucu'ya sorar: *"Bu canon'da var mı? Alt kitapta var mı?"* Cevap "belirsiz"se yorum teklifi hazırlar ve Kurul'a taşır; "boşluk"sa Master'a. Ürünün ne olduğunu değiştirmeyen sorular — "nasıl" soruları — Lead'in kendi kararıdır ve teknik dokümanlara yazılır (§2.4).

**Lead canon'u bilir; sadece kendi uyumuna hükmedemez.** Canon Lead'in context'inde verbatim durur. Lead görevi bölerken alt kitap haritasını kendisi kullanır ve ilgili maddeleri — özetlemeden, kopyalayarak — görevle birlikte subagent'a verir. Uyum büyük ölçüde inşa sırasında sağlanır; gate son hattır, ilk hat değil. Lead kendini kontrol edebilir; kendini onaylayamaz.

**Çıkar çatışması kuralı.** Lead bir feature yaparken canon'a takılırsa aynı oturumda amendment teklif edemez. Teklif kuyruğa girer, PR bekler, Kurul ayrı bir oturumda — o PR'ın baskısı olmadan — bakar.

### 3.3 Koruyucu — ajan

Tek amacı canon'a hizmet etmek. Hiçbir feature'a, deadline'a, sprint hedefine bağlılığı yok. Romantik bir tarif ama işlevsel: persona davranışı yönlendirir ve "tek sadakati canon'a olan" karakter, builder bias'ına karşı iyi bir prompt yardımıdır. Yardımdır, koruma değil: koruma context izolasyonu ve kalibrasyondur (§7). Persona ölçülemez; ikisi ölçülür.

**Bağımsızlık karakter değil, context tasarımıdır.**

```
Koruyucu görür:
  canon · ilgili alt kitaplar · ACTIVE ruling'ler · diff · read-only repo
  normalized intent — tek satır, değişikliğin amacı

Koruyucu görmez:
  deadline · iş değeri · Lead'in gerekçesi · PR description · savunma
  LEDGER — gate'te hiç; audit'te veri olarak, norm olarak değil
```

Intent gereklidir: sadece diff görmek bir davranışın amaç mı yan etki mi olduğunu ayırt etmeyi zorlaştırır. Ama intent'i **Lead yazmaz** — Lead yazarsa persuasion kanalı geri döner. Intent, Lead'den önce gelen atamadan (Master'ın verdiği görev, ticket) türer; gerekçe alanı yoktur.

**Yetkisi asimetriktir: yalnızca veto.** Durdurabilir, yönlendiremez. Canon'a madde ekleyemez, alt kitaba tek başına ekleyemez, ruling'i tek başına veremez. Tutkulu bir ajanın initiative'siz olması onu güvenli kılar — engizisyon initiative'le başlar.

**Yorumlar, ama norm üretmez.** Bu sınırın kesin hali şudur:

```
izinli   — norm interpretation:
  "C-09'un 'ayrık interaction surface' ilkesine göre bu değişiklik
   Everyday ile Operator arasındaki sınırı bulanıklaştırıyor."

yasak    — norm creation:
  "C-09'dan dolayı Everyday surface'te en fazla üç buton olabilir."
```

Birincisi var olan bir maddeyi cite ederek yorumlar. İkincisi olmayan bir maddeyi oldurur. Kendi okumasının yorum mu yaratma mı olduğundan emin değilse default yorum yapmamaktır: NEEDS-RULING, Kurul'a.

**Tutku canon'a olmalı, yasağa değil.** Canon ürünün ne *olduğunu* da söyler. Sadece "hayır" diyen koruyucu canon'a değil yasağa hizmet eder. Koruyucu, hiçbir maddeyi ihlal etmeyen ama ürünün karakterini eksilten değişikliği de işaretler — ancak bunu **yalnız ADVISORY** olarak; cite edilemeyen his BLOCK olamaz.

**Dört cevap kuralı.** "Canon'da var mı" sorusuna dört cevap vardır: **var** (cite), **aykırı** (cite), **belirsiz** (cite — madde var, bu vakaya uygulanması belirsiz → NEEDS-RULING, Kurul), **boşluk** (cite yok — uygulanabilir madde yok → NEEDS-NORM, Master). Cite edilemeyen madde yoktur; hallucinated clause en tehlikeli hatadır çünkü Lead uydurma bir maddeye göre inşa eder. "Belirsiz" ve "boşluk" yalnızca ilgili domain'lerin alt kitapları ve aktif ruling'leri **tam yüklüyse** söylenebilir; aksi halde cevap "belirlenemedi"dir (§6).

**İki pass.** Aynı ajan, iki ayrı soru:

- **Guardian pass** — alignment arar: canon'a sadık mı? Bütünsel okumaz: önce dokunulan maddeleri tek tek listeler, sonra her birini ayrı değerlendirir. Uzun context'te ortada kalan madde gözden kaçar; listeleme bunu kırar. Verdict'teki PRESERVED bölümü bu listenin çıktısıdır. Madde madde değerlendirmeden sonra bir **cross-clause pass** gelir: tek tek korunan maddeler birlikte ihlal üretebilir — C-04 ve C-09 ayrı ayrı temiz görünürken bileşimleri yeni bir authority/surface problemi yaratabilir. Bütünsel okuma kaldırılmaz; madde madde değerlendirmeden *sonra* yapılır. Sıra: madde listesi → madde madde → çapraz etkileşim → Breaker.
- **Breaker pass** — counterexample arar: sadık görünmesine rağmen nasıl bozarım? Authority modelini bypass edebilir miyim? UI yanlış mental model kuruyor mu? Bu abstraction ileride canon dışı davranışı kolaylaştırıyor mu?

Breaker'ın doğrulanmış her counterexample'ı **kalıcı bir regression artefact'ına** dönüşür: unit/integration test, golden semantic case, UI eval fixture, senaryo testi, snapshot + rubric. Hepsi executable test olamaz; hepsi kalıcı olur (somut örnek: §9.6). Böylece hard invariant'lar zamanla mekanik kontrole iner ve Koruyucu'nun yükü asıl işine — soft kimlik ilkelerine — daralır.

### 3.4 Müfettiş — ajan

Koruyucu'yu kim korur? Master'a bağlı, Lead ve Koruyucu'nun yaptıklarını denetleyen bir ajan. Habersiz gelir, denetler, gider.

**İçeriği değil süreci denetler.** Koruyucu'nun AUDIT loop'u ürünü canon'a karşı denetler; Müfettiş ajanları **yetki haritasına** karşı denetler. "Bu PR C-04'ü ihlal ediyor" demez — dediği an ikinci bir Koruyucu'dur ve korele görüş üretir. Dediği şey: "Koruyucu bu PR'ı Breaker pass yapmadan geçirmiş." Internal audit ile line management ayrımı.

**Sıfır yetki, tek çıktı: rapor.** Veto yok, edit yok, Kurul'da oy yok. "Müfettişi kim denetler" regress'i ancak Müfettiş'in hiçbir şey üzerinde yetkisi olmadığında durur.

**Master'a bağlıdır ama Master'ı da raporlar.** "Master üç override'ı gerekçesiz yapmış" diyebilmelidir. Bağlılık sadakat değil, raporlama hattıdır.

**Bağımsızlığı context'ten gelir.** Lead ve Koruyucu ile aynı oturumda hiç bulunmaz; artefact'lara bakar: verdict'ler, `RULINGS.md`, `LEDGER.md`, oturum transcript'leri, Koruyucu'nun aldığı input'lar. Farklı model ailesi bağımsızlık *sağlamaz*; korele blind spot riskini azaltmak için bir diversity heuristic'idir.

**Teftiş listesi:**

- Her BLOCK'ta cite + counterexample var mı
- "Var" cevapları örneklenir: cite edilen madde gerçekten onu söylüyor mu
- DERIVED sınıflandırmaları örneklenir: gerçekten türetilebilir mi, yoksa gizli yeni norm mu. Yöntem **kör yeniden türetme**: temiz bir Koruyucu instance'ına yalnız canon maddesi + alt kitap maddesi verilir, isnad metni verilmez; "bu bundan çıkar mı?" Argümanı görmeden türetilemiyorsa DERIVED değildir
- Amendment teklifi tetikleyen PR'la aynı oturumda mı açılmış
- Her override gerekçeli ve loglu mu; override'lar canon'u fiilen deliyor mu
- Lead'in "operasyonel" diye kendi verdiği kararlar örneklenir: gerçekten ürünün ne olduğunu değiştirmiyor mu
- Acil istisnalar süresinde kapanmış mı
- Koruyucu'nun context'ine gerekçe, PR description, deadline sızmış mı
- Aynı PR tekrar çalıştırılınca aynı verdict mi
- Ledger birikip audit gecikiyor mu
- Golden set precision'ı düşüyor, override oranı yükseliyor mu
- İsnadsız alt kitap maddesi, terfi etmemiş tekrar eden ruling, eskimemiş stale ruling var mı

**Habersiz ve örneklemeli.** Rastgele örnek + periyodik. Vergi denetimi mantığı.

Asıl tespit ettiği şey **capture**dır: Koruyucu'nun ikna edilmesi, yumuşaması, ya da Lead'in "compliant görünen" PR yazmayı öğrenmesi. Bunları Koruyucu kendisi göremez.

### 3.5 Kurul

Lead + Koruyucu; Master gerektiğinde. Kurul üç işlem yapar: DERIVED alt kitap maddesi, yorum ruling'i, boşluk tespiti. Beraberlik → statüko.

### 3.6 Ajan ekleme

Lead çalışırken yeni bir ajana ihtiyaç bulabilir. İki tür vardır ve yolları farklıdır.

**Araç ajan** — bir rolün kendi işini bölmek için açtığı subagent: test yazıcı, refactor edici, domain bazlı inceleyici. Bunu ilgili rol serbestçe açar; bu bir rol değil, o rolün kendi elidir. Tek kural:

> **Yetki devredilebilir, büyütülemez.** Subagent'ın yetkisi parent'ının altkümesidir.

Somut olarak: Lead'in subagent'ı veto edemez, Koruyucu ile doğrudan konuşamaz, çıktısı Lead'in çıktısı sayılır ve gate'e ayrı bir "onay" olarak giremez — "X ajanı onayladı" bir kanıt değil, Lead'in argümanıdır ve Koruyucu zaten görmez. Koruyucu'nun domain yardımcısı norm üretemez, verdict Koruyucu'nundur. Müfettiş'in yardımcıları sıfır yetkilidir.

**Yetkili ajan** — yetki haritasında yeni satır açan bir rol: ayrı bir security reviewer, belirli bir alt kitap için ayrı bir koruyucu, ikinci bir lead. Yetki maddesi canon'un içinde olduğu için bu **canon-tier** bir değişikliktir:

1. Lead ayrı oturumda teklif eder — çıkar çatışması kuralı aynen geçerli; "bu PR'da lazım oldu" oturumunda değil.
2. Kurul teklifi invariant'a karşı test eder:
   - Yeni ajan *yarat / uygula / onayla* üçlüsünden ikisini tek elde topluyor mu?
   - Koruyucu'yu kopyalıyor mu? İkinci koruyucu ikinci görüş değil, korele görüştür.
   - Context isolation'ı deliyor mu — Lead'den Koruyucu'ya ulaşan yeni bir kanal açıyor mu?
3. Master onaylar.
4. Canon'a yetki maddesi, ajana kendi persona dosyası, Müfettiş'in teftiş listesine yeni satır eklenir.

Eksik olan ajan değil de **ayrıntı** ise yol zaten tanımlı: DERIVED → Kurul, NEW NORM → Master.

---

## 4. Yetki haritası

| İşlem | Teklif | Karar | Onay | Kayıt |
|---|---|---|---|---|
| Feature / PR | Lead | Koruyucu gate: canon itirazı var / yok | — | PR |
| Ruling — belirsiz norm | Lead | Kurul yorumlar (cite zorunlu) | Master geri çekebilir | `RULINGS.md` |
| Boşluk — norm yok | Koruyucu "boşluk" der | — | **Master**: alt kitaba NEW NORM ya da amendment | Alt kitap / `CANON.md` |
| Alt kitap — DERIVED | Lead | Koruyucu isnad'ı doğrular | — | Alt kitap + isnad |
| Alt kitap — NEW NORM | Lead | Kurul | **Master** | Alt kitap + isnad |
| Canon amendment | Lead (ayrı oturum) | Kurul uzlaşır | **Master** | `CANON.md` (supersedes) |
| Veto override — yorum hatası | Koruyucu veto eder | — | **Master** (gerekçeli) | `RULINGS.md` |
| Veto — gerçek ihlal | Koruyucu veto eder | — | override yok; amendment veya acil istisna | `CANON.md` / `LEDGER.md` |
| Acil istisna | Master | — | Master | `LEDGER.md` (süreli, audit'i kilitler) |
| Apokrif ilanı | Herhangi | Kurul | Master | Canon haritası |
| Araç ajan açma | İlgili rol | — (yetki ≤ parent) | — | Oturum log'u |
| Yeni yetkili ajan / rol | Lead (ayrı oturum) | Kurul invariant'a karşı test eder | **Master** | `CANON.md` yetki maddesi + persona dosyası |
| Teftiş | Master / periyodik | Müfettiş raporlar (yetki yok) | — | `INSPECTIONS.md` |

İki kritik satır: canon amendment'ta Kurul **uzlaşsa bile** Master onaylar — iki ajanın anlaşması anlaşamamasından tehlikelidir, anlaşmazlık kendini işaretler, anlaşma sessizdir. Ve veto override'ı Koruyucu'yu override eder; canon yalnız amendment ile değişir.

### 4.1 İki sık itiraz

**"Master darboğaz olur."** Master her kararı vermez; yalnız yeni norm, canon-tier değişiklik ve itirazda girer. Yorum ruling'leri Kurul'da kalır, Master geri çekme hakkını tutar (§2.3). ADVISORY merge'i durdurmaz. Kalan bekleme bilinçlidir: kimlik kararı nadirdir ve beklemeye değer. Sık geliyorsa bu Master'ın değil canon'un sorunudur — boşluk var demektir ve override oranı bunu ölçer (§7). Hedef metrik: Master'ın baktığı PR sayısı değil, verdiği kimlik kararı sayısı (§11).

**"İsnad uydurulur."** Üç savunma, üç ayrı seviyede: mekanik — referans verilen madde var mı, neshedilmiş mi, metin birebir mi (CI); semantik — kör yeniden türetme, argümanı görmeden türetilemeyen madde DERIVED değildir (§3.4); otorite — türetilemeyen madde NEW NORM'dur ve Master'a gider (§2.2). Uydurma isnad'ın kazancı, ancak üçünü birden geçerse vardır.

---

## 5. Beş loop

```
1. CONSULT   build-time     Lead → Koruyucu: "var mı?"       → var / aykırı / belirsiz → Kurul / boşluk → Master
2. GATE      PR-time        Koruyucu → verdict                → GO / NO-GO / NEEDS-RULING / INDETERMINATE
3. AUDIT     periyodik      Koruyucu → tüm sistem vs canon    → drift raporu
4. COUNCIL   ayrı oturum    Kurul → ruling / alt kitap / amendment
5. INSPECT   habersiz       Müfettiş → ajanlar vs yetki haritası → teftiş raporu
```

Gate diff görür, trajectory görmez; audit trajectory'ye bakar. Audit ürünü, inspect ajanları denetler. Üçü ayrı loop'tur.

---

## 6. Verdict formatı

**Verdict** dört değerden biridir; **finding**'lerin ayrıca severity'si vardır. İkisi karıştırılmaz.

```
Verdict
  GO              ihlal yok
  NO-GO           cite edilebilir bir madde ihlal edildi (en az bir BLOCK)
  NEEDS-RULING    norm var, bu vakaya uygulanması belirsiz; cite zorunlu → Kurul
  NEEDS-NORM      corpus tam yüklü, uygulanabilir norm yok → Master
  INDETERMINATE   gerekli corpus/context kurulamadı — "boşluk" değil, "bakamadım" → context tamamla, tekrar gate

Severity
  BLOCK           cite + reproducible counterexample zorunlu
  ADVISORY        drift, karakter, yorum — LEDGER'a gider, merge'i durdurmaz
  OBSERVATION     bilgi; aksiyon yok
```

`NEEDS-RULING`, `NEEDS-NORM` ve `INDETERMINATE` üç ayrı şeydir: birincisi Kurul'a gider, ikincisi Master'a, üçüncüsü kimseye gitmez — Koruyucu kendi context'ini tamamlar ve tekrar çalışır. Bu ayrımlar olmadan retrieval failure "canon sessiz" kılığına, boşluk da "belirsizlik" kılığına girer.

`GO` bir code review ya da ürün onayı değildir; yalnız incelenen normatif kapsamda canon itirazı bulunmadığı anlamına gelir. Security, test ve normal code review CDD'nin dışında kendi gate'lerini korur; Koruyucu feature'ı onaylayan makam değil, itiraz eden makamdır.

Örnek:

```
CANON REVIEW · PR #412

Verdict: NO-GO

PRESERVED
  ✓ C-04   operator authority server-derived kalıyor
  ✓ C-11   single-master invariant korunuyor

FINDINGS
  ✗ BLOCK       C-04     `is_admin_req` fallback client-originated authority hint kabul ediyor
                         counterexample : stale client role=master → legacy path X
                         reproducible   : evet — tests/canon/test_no_client_role_fallback.py
  ⚠ ADVISORY    S-SURF-03  member-management ekranı Operator sorumluluğunu Everyday'e taşıyor
                         → LEDGER
  ⚠ ADVISORY    C-09 (yorum)  Everyday'in ayrık karakteri üç yeni notification ile bulanıklaşıyor
                         → LEDGER
  · OBSERVATION  "bulk role assignment": C-09 uygulanır (yönetim işi Operator surface'inde)
                         ama toplu atamanın sınırı belirsiz → NEEDS-RULING, Kurul, R-047

COMPLIANCE CONDITION
  Hiçbir client-originated authority hint bir authority decision path'ine ulaşamaz.
  Nasıl sağlanacağı Lead'in kararıdır.
  Sağlanamıyorsa: ayrı oturumda C-04 amendment kuyruğu — Master onayı gerekir.
```

`COMPLIANCE CONDITION`, eski "REQUIRED" alanının yerine geçer. Koruyucu nasıl implement edileceğini söylemez; **compliant state'in ne olduğunu** söyler. Veto-only ilkesi ancak böyle temiz kalır.

---

## 7. Koruyucu'nun kalibrasyonu

"Bozmak için sebep ara" objective'i verilen bir LLM sebep uydurur. Bu sycophancy'nin tersidir ve aynı derecede gerçektir. Koruyucu her PR'a ADVISORY yapıştırırsa üç haftada herkes onu linter gibi kapatır.

- **Golden set.** Bilinen violation / non-violation PR'lardan bir set; precision ve recall ölçülür. Koruyucu bir judge'dır ve judge'lar meta-evaluate edilir.
- **Override oranı canon sinyalidir, Koruyucu hatası değil.** Master sık override ediyorsa canon'da boşluk vardır. Koruyucu override'lardan "veto etmemeyi" öğrenmez; canon'a kalibre kalır. Canon değişince Koruyucu değişir — ısrar değil, sadakat.
- **Persuasion testi.** Ölçülen şey "PR description verilince verdict değişiyor mu" değil; verdict daha fazla gerçek bilgiyle haklı olarak da değişebilir. Ölçülen: **nötr intent vs persuasive framing** aynı diff'te farklı verdict üretiyor mu.
- **Nondeterminism policy.** LLM verdict'i stokastiktir; CI gate'i öyle olamaz. Üç kanıt türü karıştırılmaz: **grounding** (cite + reproducible counterexample) doğruluk kanıtıdır; **N-run** stabilite kanıtıdır — 3/3 aynı yanlış yorum mümkündür; **golden set** judge kalitesi kanıtıdır. Self-reported confidence bunlardan hiçbiri değildir ve zorunlu alan yapılmaz.

  ```
  deterministik ihlal            → test; Koruyucu'ya sorulmaz
  explicit semantik ihlal        → BLOCK için cite + reproducible counterexample zorunlu;
                                   N çalıştırma yalnız stabiliteyi ölçer, tutarsızsa INDETERMINATE
  karakter / drift               → ADVISORY + LEDGER; asla BLOCK
  model instability              → INDETERMINATE; yazı-tura ile merge durmaz
  ```

- **Severity disiplini.** BLOCK insan zamanı harcar; ADVISORY ledger'a gider. İkisini karıştıran Koruyucu güvenilirliğini kaybeder.
- **Gate iki aşamalıdır.** Mekanik gate önce: `tests/canon/`, lint, ArchUnit tarzı kurallar. Mekanik BLOCK varsa Koruyucu hiç çalışmaz. Koruyucu yalnız mekanik gate'i geçen diff'e ve yalnız mekanikleşemeyen ilkelere bakar. Token maliyeti ve tutarsızlık yüzeyi birlikte küçülür.

---

## 8. Kurumsal failure mode'lar

> Aşağıdaki eşleştirmeler tarihsel olayların nedenlerini açıklama iddiası taşımaz. Yorum otoritesi etrafında kurulmuş eski kurumlar — hukuk, din, anayasa — burada bir **governance stress-test kütüphanesi** olarak kullanılıyor: aynı yapı yüzyıllar boyunca nasıl bozuldu, CDD'de aynı bozulma nereden girer.

| Kurumsal failure pattern | CDD failure mode | Savunma |
|---|---|---|
| Dağınık yorum otoritesi | Her ajan canon'u kendi yorumlar; paralel yorum gelenekleri oluşur | Alt kitaplar + ACTIVE ruling: yorum paylaşılır |
| Yorum otoritesinin capture'ı | Kurumsallaşmış yorumcu kendi otoritesini büyütür; Koruyucu fiilen yasa koyucu olur | Veto-only; norm üretemez; Kurul; Master geri çekme hakkı |
| Yetkisiz amendment | Ortak normatif metin, değişiklik yetkisi üzerinde uzlaşılmadan değişir; implicit lex posterior | Explicit supersedes + Master onayı; canon içi çelişki gate'i kapatır |
| Kaynak sahibinin normu vaka vaka delmesi | Master ruling'le canon'u aşar; canon bağlayıcılığını kaybeder | Master canon'u amendment/nesih ile değiştirir, ruling ile delmez |
| İstisnanın normalleşmesi | Sürtünmesiz waiver canon'u fiilen deler | Süreli kimlik borcu; cite edilemez; audit'i kilitler |
| Yorum katmanının kaynak normu gölgelemesi | Alt kitap canon'un söylemediği normu üretir; lex specialis ile canon'u ezer | DERIVED / NEW NORM; lex specialis yalnız aynı seviyede |
| Precedent'in donması | Ruling log'u immutable yasa kitabına dönüşür | Lifecycle; terfi / eskime; ACTIVE ruling geçici otoritedir |
| İletim hatası | Ajan canon'u özetleyerek context'e alır; varyantlar çoğalır | Verbatim kuralı |
| Enforcement aşırılığı | Aşırı gayretli Koruyucu sahte violation üretir; "compliant görünen" PR yazmak öğrenilir | Counterexample zorunluluğu, severity, kalibrasyon |
| Lafzın korunup ruhun kaybı | Alt kitap canon'la çelişmeden onu başka şeye yorumlar | Karakter kontrolü, cross-clause pass, ADVISORY |
| Yorumcuların sessiz uzlaşısı | Lead + Koruyucu korele blind spot | Canon-tier ve yeni normda Master onayı; kör yeniden türetme |
| Kaynak normun gerçeklikten kopması | Kod X diyor, canon Y diyor | Draft → Master onayı → canon → verified; apokrif ilanı |

**Tarihsel örnekler** — analoji olarak, nedensellik iddiası olmadan:

- *Yetkisiz amendment:* Filioque tartışması. Batı'da yüzyıllar boyunca yerel olarak kullanılan bir ekleme, ortak creed üzerinde kimin değişiklik yetkisi olduğu uzlaşılmadan evrensel metne girdi; tartışmanın bir tarafı metin, diğer tarafı yetkiydi.
- *İstisnanın normalleşmesi:* endüljans. Tek tek istisnalar kurumsal pratiğe dönüşünce satılan şey normun kendisi değil, istisnası oldu.
- *Precedent'in donması:* "içtihat kapısının kapandığı" anlatısı. Tarihsel olarak gerçekten kapanıp kapanmadığı tartışmalıdır — Hallaq bu anlatıyı sorgular — ama anlatının kendisi failure mode'u iyi tarif eder: yorumun durması, taklidin başlaması.
- *Dağınık yorum otoritesi:* Reform sonrası merkezi yorum otoritesinin yokluğunda paralel yorum geleneklerinin çoğalması. Tek nedeni tek bir doktrin değildir; yapısal sonucu budur.
- *Yorum otoritesinin capture'ı:* kurumsallaşmış her yorum makamının — kendini kaynağın hizmetinde tanımlasa bile — zamanla kendi otoritesini büyütme eğilimi.
- *İletim hatası:* el yazması aktarımında çoğalan varyantlar ve bunları ayıklamak için doğan textual criticism disiplini.
- *Enforcement aşırılığı:* engizisyon — koruma aygıtının korunan şeyden bağımsız bir güce dönüşmesi.

En genel ders: bu kurumların hiçbiri metni korumak için kurulmadı; **yorumlama otoritesinin kimde olacağını** belirlemek için kuruldu. Asıl sorun metnin varlığı değil — metni kimin yorumlayacağı, yorumun ne zaman yeni norma dönüştüğü ve bu dönüşümü kimin onaylayacağıdır. CDD'nin dört rolü tam olarak bu üç soruya cevaptır; asıl tasarım kararı `CANON.md`'nin içeriği değil, §4'teki yetki haritasıdır.

---

## 9. CDD pratikleri

Yukarısı yönetişim; burası günlük iş. Zamanın büyük kısmı tek bir döngüdür; geri kalan bölümler o döngünün istisna yollarıdır.

### 9.1 Günlük döngü

```
Master    → görev verir (spec / ticket)
Lead      → böler, subagent'lara dağıtır, yapar
Lead      → /gate: diff Koruyucu'ya
Koruyucu  → GO / NO-GO / NEEDS-RULING / NEEDS-NORM / INDETERMINATE
GO        → merge (canon itirazı yok; diğer gate'ler ayrı)
NO-GO     → Lead compliance condition'a göre revize eder ya da Master'a itiraz; tekrar /gate
NEEDS-RULING  → Kurul (Faz 0'da Lead + Koruyucu'nun aynı oturumda kısa bir turu; Master log'u görür)
NEEDS-NORM    → Master'a tek satırlık soru; cevap alt kitaba ya da canon'a bir satır
INDETERMINATE → context tamamlanır, tekrar /gate; kimseye gitmez
```

### 9.2 Üç eksik, üç kapı

Ajan "açıklama yok" dediğinde işi bitmemiştir; hangi eksiğin söz konusu olduğunu söylemesi gerekir:

```
"Undo olsun mu?"                            spec boşluğu   → görevi verene (Master)
"Everyday kullanıcısı bunu görebilir mi?"   norm sorusu    → önce Koruyucu (cite); belirsizse Kurul, boşluksa Master
"Hangi transaction stratejisi?"             nasıl boşluğu  → Lead karar verir, kimseye sormaz
```

Test tek: cevap ürünün ne olduğunu değiştirir mi? (§2.4)

### 9.3 Görev devri

Lead canon'u bilir. Subagent'a görev verirken ilgili maddeleri kopyalar, özetlemez:

```
Görev:      Operator surface'e bulk role assignment ekle
Spec:       <ticket>
Canon:      C-04 (verbatim) · C-09 (verbatim)
Alt kitap:  S-AUTH-12 (verbatim)
Sınır:      client-originated hint authority path'e ulaşmayacak; Everyday'e hiçbir şey sızmayacak
```

Uyum inşa sırasında sağlanır; gate son hattır. NO-GO sık geliyorsa ya Lead maddeleri yönlendirmiyor ya canon net değil — ikisi de Master'ın sinyalidir.

### 9.4 NO-GO sonrası

```
düzelt         compliance condition'ı sağla, tekrar gate; Breaker'ın testi tests/canon/'da kalır
itiraz         Koruyucu'yla tartışma yok, kanal yok — Master'a; Koruyucu yanılmışsa override + RULINGS
amendment      ayrı oturum, kuyruğa, PR bekler; Master supersedes ile onaylar; PR yeni canon'a karşı tekrar gate
acil istisna   yalnız Master; süreli, LEDGER, audit kilitlenir; cite edilemez
```

Lead'in yapamayacakları: aynı diff'i tekrar gönderip farklı zar beklemek; compliant *görünen* hale getirmek; amendment'ı aynı oturumda açmak.

### 9.5 Canon yazma

- Bir sayfa. Aşarsa alt kitaba in.
- Numaralı maddeler; her madde tek cümle, tek iddia.
- Yasaklar kadar tanımlar. "Bu ürün şudur" maddeleri olmadan Koruyucu yalnız "hayır" der.
- Feature yok. "Bulk assignment var" canon değildir; "authority server-derived" canon'dur.
- Yetki maddesi: kim yorumlar, kim değiştirir, Kurul'a ne devredilmiştir.
- Alt kitap haritası ve apokrif listesi.
- Lead'in teklif ettiği madde DRAFT'tır; Master onaylamadan canon değildir.

### 9.6 Soft ilkeler için artefact

Her counterexample test olmaz. "Bu ekran yanlış mental model kuruyor" için **golden semantic case**:

```
GSC-007
  madde      : C-09
  durum      : Everyday ekranında member-management girişi (screenshot ya da state dump)
  soru       : Bu ekran Everyday'i Operator'a dönüştürüyor mu?
  beklenen   : ADVISORY — C-09 ruhu; sınır bulanıklaşıyor
  gerekçe    : C-09 (surface'ler ayrıdır) + S-SURF-03 (üye yönetimi Operator sorumluluğudur) — yalnız aktif corpus'a cite
```

Audit'te Koruyucu bu vakaları yeniden değerlendirir; beklenen verdict'ten sapma kalibrasyon sinyalidir. Golden set'in soft yarısı budur; UI eval fixture aynı şeyin senaryo + rubric halidir.

**Golden artefact'lar normatif değildir.** Beklenen verdict ve gerekçe yalnız aktif normatif corpus'a cite edebilir; cite edemeyen gerekçe golden case'e giremez — aksi halde golden set fark edilmeden dördüncü bir canon olur. Kaynak madde supersede edilirse ilgili golden case otomatik invalidate edilir. Yön tektir: canon → golden oracle; hiçbir zaman golden oracle → canon yorumu.

### 9.7 Claude Code kurulumu

```
CANON.md      → CLAUDE.md verbatim içerir; her oturum onunla başlar
GUARDIAN.md   → Koruyucu subagent prompt'u; aldığı şey: canon + ilgili kitaplar + diff + intent
/consult      → inşa etmeden önce; yalnız kimliğe dokunan sorular
/gate         → diff üzerinde; mekanik gate önce, sonra Koruyucu
RULINGS.md    → bir karar verdiğinde bir satır
/council      → Faz 1;  /inspect → Faz 2
```

Üç dosya ve bir komutla başlanır: `CANON.md`, `GUARDIAN.md`, `/gate`.

### 9.8 Maliyet

**Token.** PR başına bir Koruyucu çağrısı, küçük context: bir sayfa canon + ilgili kitap + diff. Bir code review çağrısıyla aynı mertebe. N-run yalnız BLOCK adayı bulgular için, her PR için değil; farklı model ailesiyle koşulursa tek Koruyucu'nun blind spot'una karşı da bir örnek verir. Audit periyodik, teftiş örneklemeli. Üretim maliyetinin yanında küçüktür.

**İnsan.** Asıl maliyet budur ve ölçülen şey de budur (§11). Faz 0'da Master'ın maliyeti yalnız NO-GO itirazları ve "yok" cevaplarıdır; canon olgunlaştıkça ikisi de azalır.

---

## 10. Kademeli açılım

Bunların hepsi ilk gün kurulmaz. Yöntemin kendi ilkesi: ruling ve drift biriktikçe katman açılır.

**Faz 0'dan önce — sadece `CANON.md`.** Lead'in context'inde, Koruyucu yok. Bu CDD değildir; Spec-Kit constitution'ıdır. Ama canon yazmayı öğretir ve ilk drift'i hissettirir — Koruyucu'ya ihtiyacın olduğunu anladığın an Faz 0 başlar.

**Faz 0 — ilk gün.** Minimum uygulanabilir çekirdek.

```
CANON.md          bir sayfa · numaralı maddeler · yetki maddesi · apokrif listesi
GUARDIAN.md       persona · context kuralları · dört cevap · verdict formatı
RULINGS.md        kronolojik
canon-gate        PR'da Koruyucu subagent'ı, verdict yorum olarak, BLOCK merge'i durdurur
```

Master manuel. Alt kitap yok; canon her şeyi taşır çünkü henüz küçük.

**Faz 1 — aynı domain'de tekrar eden normatif tema oluşunca.** Varsayılan operasyonel eşik üç ACTIVE ruling, ama bu bir heuristic: iki ruling aynı problemi tekrar ediyorsa alt kitap çoktan gerekir, üç ilgisiz ruling gerektirmez. Tetik takvim değil, sayaç da değil, sinyaldir: o domain'in alt kitabı açılır, ruling'ler oraya terfi eder.

```
docs/canon/*.md   domain bazlı alt kitaplar · isnad · DERIVED / NEW NORM
LEDGER.md         tolerated deviations · acil istisnalar
/council          ayrı oturum · amendment kuyruğu
tests/canon/      Breaker artefact'ları
```

**Faz 2 — drift görünür olunca.**

```
INSPECTOR.md + INSPECTIONS.md    Müfettiş
golden set                       Koruyucu precision / recall
domain router                    dosya → alt kitap + aktif ruling yükleme; "belirsiz/boşluk" ancak tam yüklüyse
                                 deterministik eşleme (path/tag → kitap); normatif corpus için semantik
                                 retrieval hiç kullanılmaz. Çapraz etki için Koruyucu ek kitap isteyebilir;
                                 yüklenene kadar INDETERMINATE
ruling lifecycle                 ACTIVE / PROMOTED / SUPERSEDED / EXPIRED / ARCHIVED
CI policy                        N çalıştırma, INDETERMINATE
metrikler                        §11
```

Claude Code karşılığı: Lead ana ajan. Koruyucu, context'i sınırlanmış bir subagent — PR description'a ve Lead'in gerekçesine erişimi yok, intent'i atamadan alır. Canon-gate, CI'da aynı subagent. `/council` ayrı komut. `/inspect` ayrı komut, tercihen farklı model, yalnız log ve transcript'lere bakar.

---

## 11. Deney protokolü

Bu bir yöntem iddiası değil, bir öneri ve onu test etme planıdır. Sonuç metriklerle raporlanır.

**Dört ana eksen:**

1. **Drift yakalama** — Koruyucu, insanın yakaladığı kimlik drift'inin ne kadarını yakalıyor?
2. **False-block oranı** — compliant değişiklikleri ne kadar gereksiz durduruyor?
3. **İnsan dikkati sıkışması** — Master'ın okuduğu PR sayısı / verdiği kimlik kararı sayısı düşüyor mu?
4. **Boylamsal tutarlılık** — 100–500 değişiklik sonra canon'a uyum başlangıca göre korunuyor mu?

**İkincil metrikler:** Koruyucu precision / recall, override oranı, verdict stabilitesi, belirsiz-vaka ve boşluk oranı, ruling terfi oranı, stale ruling sayısı, amendment oranı, acil istisna sayısı ve kapanma süresi.

Bu metriklerin veri üretmesi için en az ~100 değişiklik gerekir; Faz 0'da ölçülecek bir şey yoktur.

**Test ortamı.** Öneri ilk üründe, pratiğin geriye dönük formalize edilmesiyle ortaya çıktı. İkinci bir üründe bilinçli olarak baştan uygulanıyor. İkinci ürünün ilkinden **farklı karakterde** olması şarttır; aynı karakterde ikinci uygulama genelleme değil tekrardır.

Beklediğimiz sonuç şu: soft kimlik ilkelerinde bir LLM Koruyucu'nun precision'ı kabul edilebilir çıkarsa, yetki ayrımı LLM'in semantik kapasitesini builder bias'ından koruyan pratik bir yol demektir. Çıkmazsa, mekanik fitness function'lara geri dönülür ve bu öneri onların üzerine pahalı bir katman olarak kalır. Her iki sonuç da raporlanır.

---

## Referanslar

- Ford, N., Parsons, R., Kua, P. *Building Evolutionary Architectures*. O'Reilly, 2017 — architectural fitness functions.
- Nygard, M. "Documenting Architecture Decisions", 2011 — ADR.
- Evans, E. *Domain-Driven Design*. Addison-Wesley, 2003 — ubiquitous language.
- GitHub Spec Kit — constitution artifact. https://github.com/github/spec-kit
- Marri, S. R. "Constitutional Spec-Driven Development: Enforcing Security by Construction in AI-Assisted Code Generation". arXiv:2602.02584, Ocak 2026.
- Alenezi, M. "Specification-Driven Development as the Foundation of AI-Native Enterprise Software Engineering". arXiv:2607.16680, Temmuz 2026 — Specification Governance Reference Model.
