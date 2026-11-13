# Tarih Hassasiyeti – Plan ve Durum

Yönetici: Tarih Orkestratörü (Claude Code alt ajanı, Opus 5.5; Kütüphaneci başlattı, 13 Kasım 2026).
Amaç: Osmanlı konulu dizi ve filmlere tarihçilerin yönelttiği bariz hataları toplayıp 1798–1800 dönemi için doğrulanmış bir kılavuza çevirmek. Hedef ilk sürüm: 100–150 doğrulanmış madde.

## Araç keşfi (13 Kasım 2026)

FreeLLMAPI, OmniRoute ve 9Router bu bilgisayarda kurulu ya da çalışır değil (npm global listesinde yoklar, localhost'ta açık bir yönlendirici /v1 adresi yok). Kurulmadı: üçü de ücretsiz sağlayıcılar için hesap ve API anahtarı istiyor, bu iş Yavuz'a ait.

Bunun yerine zaten kurulu olan OpenCode CLI (v2.0.19, npm global `@opencode/cli`) kullanıldı. OpenCode Zen'in adı `-free` ile biten modelleri yeni hesap ya da anahtar girmeden çalışıyor; bu modellerin `webfetch` ve `websearch` araçları da var, yani ham sayfaları ücretsiz modeller kendileri arayıp okuyor. TDV İslam Ansiklopedisi düz `curl` isteğine 403 veriyor, ama OpenCode `webfetch` ile açılıyor (deneme: kapıkulu maddesi).

Yerelde Ollama (127.0.0.1:11434) üzerinde `qwen3.5:4b` var; çok küçük olduğu için kullanılmadı.

Codex: kullanılmadı (betikleri orkestratör kendisi yazdı; operatörlük işi küçük kaldı).

## Akış

1. Kaynak toplama: kişi ve yapım başına ücretsiz ajan web'de arar, sayfaları okur, şikâyet edilen hataları kaynaklı çıkarır → `ham/kaynak-*.json`, `kaynaklar/`.
1b. Video kaynakları (Yavuz'un 13 Kasım talimatı, Kütüphaneci aracılığıyla): YouTube'da yt-dlp (kurulu, 2026.08.19) ile kişi ve yapım adlarıyla arama → başlığa göre süzme → otomatik Türkçe altyazı (vtt) çekme → 30 saniyelik zaman damgalı düz metin → ücretsiz model transkriptten madde çıkarır, her madde video adresini (`youtu.be/<id>?t=<sn>`) ve yaklaşık zamanı taşır → `ham/video-*.json`, `kaynaklar/video-listesi.md`. Ham transkriptler `ham-sayfalar/video/` altında, git dışı. Otomatik altyazı terimleri bozabilir; çıkarıcıya terimi bağlamdan düzeltmesi, emin değilse yazmaması söylendi. Video maddeleri de diğerleri gibi iki modelle TDV'ye karşı doğrulanır. Betik: `betikler/video.py`.
2. Konu taraması: konu başına ücretsiz ajan 1798 için sık yapılan hataları TDV maddelerine dayanarak önerir → `ham/konu-*.json`.
3. Birleştirme: konu başına tekilleştirme.
4. Doğrulama: her madde iki farklı ücretsiz modelle, birbirinden bağımsız olarak TDV (öncelikli) ve başka başvuru kaynaklarına karşı denetlenir. İkisi de onaylarsa doğrulanmış; çelişirlerse tartışmalı; ikisi de reddederse elenir.
5. Orkestratör örnekleme ile kalite denetimi yapar.
6. Kılavuz: `Tarih Hassasiyet Kılavuzu.md`.

Betikler: `betikler/`. Ham sayfa dökümleri ve iş klasörleri `ham-sayfalar/` altında, git dışı.

## Durum

- [x] Araç keşfi
- [~] Kaynak toplama: 24 iş (12 kişi + 12 yapım), deepseek-v4.1-flash-free. Deneme işi (Bardakçı) 8 kaynak, 20 madde verdi; örnekleme denetiminde maddeler somut ve kaynaklı.
- [~] Video kaynakları: yt-dlp ile 35 sorgu → 101 aday; başlığa göre 48 video seçildi (`ham-sayfalar/video/secilen.json`), 42'sinin Türkçe altyazısı çekildi, 6'sında altyazı yok. Uzun transkriptler 35 bin karakterlik parçalara bölündü: 61 çıkarım işi.
- [~] Konu taraması: 14 konu işi.
  Üç aşama tek kuyrukta, 8 paralel işle 13 Kasım 15:05'te başlatıldı (`ham-sayfalar/isler-asama1.json`, günlük `ham-sayfalar/asama1.log`). Betik kaldığı yerden devam eder: çıktısı olan işi atlar.
- [ ] Birleştirme
- [ ] Doğrulama
- [ ] Kalite denetimi
- [ ] Kılavuz

## Sorunlar ve notlar

- İlk deneme işi takıldı: Python'dan başlatılan `opencode run` standart girdiyi bekliyordu. `stdin=DEVNULL` ile düzeltildi (13 Kasım 14:57).
- OpenCode, iş klasörü yerine git kökünü (Ateş Mavisi) proje dizini olarak görüyor. İstemler dosya yazdırmıyor; yine de her aşama sonunda `git status` ile kitap dosyalarına dokunulmadığı denetleniyor.

- Pakalın'ın sözlüğü çevrimiçi serbest erişimde değil; doğrulamada pratikte TDV İslam Ansiklopedisi birincil başvuru oldu.

## Durum notu – 13 Kasım 2026, 15:50 (orkestratör erken rapor vermek zorunda kaldı)

- OpenCode Zen ücretsiz kotası 15:10–15:40 arasında bütün "-free" modellerde doldu ("Free usage limit reached"). O ana kadar 67 çıkarım işi bitti: 486 ham madde (iceman-free 385, deepseek-v4.1-flash-free 101), 97 web kaynağı (`kaynaklar/kaynak-listesi.md`).
- Yavuz'un ücretsiz Gemini anahtarı (kullanıcı ortam değişkeni GEMINI_API_KEY; değer hiçbir yere yazılmıyor) çalışıyor. Ücretsiz katmanda gemini-3.5-flash ve gemini-3.1-flash-lite yanıt veriyor; gemini-3.8-flash ve Google Search aracı 429 veriyor. url_context ile TDV sayfaları açılıyor ve hangi adresin okunduğu yanıtta kanıtlanıyor.
- Kalan 32 çıkarım işi (27 video parçası, 5 konu) `betikler/gemini.py isler ham-sayfalar/isler-kalan1.json 3` ile Gemini'de çalışıyordu; günlük `ham-sayfalar/asama1-gemini.log`. Betik kaldığı yerden devam eder.
- Doğrulama henüz BAŞLAMADI. Hazır: `dogrula.py` iki doğrulayıcı tanımlı (A gemini-3.5-flash, B gemini-3.1-flash-lite); kaynağı gerçekten okunmamış onaylar otomatik olarak belirsize iniyor.

## Devir – 13 Kasım 2026, 15:50: Tarih Orkestratörü II

İşi "Tarih Orkestratörü II" devraldı (Claude Code alt ajanı, Opus 5.5; Kütüphaneci başlattı; önceki orkestratörün bağlamı doldu).
- 15:50 OpenCode deneme çağrısı (mimo-v2.6, glm-5.3, deepseek-v4.1 free): kota hâlâ dolu.
- `dogrula.py` değişti: istemde Gemini'nin arama aracı olmadığı için TDV adresini tahmin etme yönergesi; her kayda `saman_adam` (kimsenin yapmadığı yapay yanlış mı) alanı; B doğrulayıcısı `DOG_B` ortam değişkeniyle seçilebilir; OpenCode çıktılarında "kaynak gerçekten okundu mu" denetimi günlükteki `% WebFetch <adres>` satırlarından yapılıyor.
- 16:24 Gemini çıkarım süreci işlerin çoğunda "deneme sınırı aşıldı" verdi. Neden: gemini-3.5-flash'ın ücretsiz katmanda GÜNLÜK sınırı 20 istek (API yanıtı: GenerateRequestsPerDayPerProjectPerModel-FreeTier, 20; yenilenmesine ~18,5 saat). Süreç durduruldu. `gemini.py` artık günlük kota hatasında boşuna beklemiyor; gemma modellerine araç (url_context) göndermiyor.
- Model taraması (16:30): çalışan ücretsiz modeller gemini-3-flash-preview (url_context kullanmadı), gemini-3.5-flash-lite ve gemini-3.1-flash-lite (url_context ile TDV okuyor), gemma-4-31b-it (araçsız). gemini-2.5-* yeni kullanıcıya kapalı.
- 16:35 kalan 19 video çıkarım işi gemini-3-flash-preview ile bitti. Çıkarım tamam: ham 724 madde (247'si video), 97 web kaynağı. `birlestir.py topla` çalıştı; tekilleştirme 15 iş gemini-3-flash-preview ile başladı (`ham-sayfalar/tekil.log`).
- TDV sayfaları tarayıcı kimliğiyle (User-Agent) düz curl'e 200 veriyor; örnekleme denetiminde kaynak okumak için kullanılabilir.
- 16:36 gemini-3-flash-preview'ın da günlük sınırı 20 çıktı (tekilleştirmede doldu). Tekilleştirme gemma-4-31b-it (ve ters sıradan gemma-4-26b-a4b-it) ile sürdürüldü; Gemma'nın günlük kotası geniş görünüyor ama yavaş (iş başına 3-5 dk).
- Doğrulama yolu değişti (Orkestratör II kararı, 16:45): url_context ile madde başına kaynak aramak 20 istek/gün kotasına sığmıyor. `dogrula2.py` + `tdv.py`: Gemma her madde için TDV slug'ı önerir, TDV sayfasını betik kendisi indirir (`ham-sayfalar/tdv/` önbelleği) ve iddiaya ilgili paragrafları seçer (`ham-sayfalar/kanit.json`); iki doğrulayıcı aynı kanıtı bağımsız okur. A = gemma-4-31b-it, B = gemini-3.1-flash-lite (kota dolarsa gemini-3.5-flash-lite). Betiğin indirdiği adresler "okunmuş" sayılır; başka adrese dayanan onay yalnız url_context okuması kanıtlanırsa geçer. Sınırlılık: iki doğrulayıcı da Google ailesinden.
- Yavuz'un kuralı (Kütüphaneci aracılığıyla, 13 Kasım ~17:20): TDV'de karşılığı olmayan maddeler (gündelik dil, hitap, sokak sözü, gündelik hayat) "kanıt yok" diye elenmez; "belirsiz / kaynakta karşılığı yok" kümesinde tutulur ve kılavuzda ayrı bölüm olur. Eleme yalnız iki doğrulayıcı da kanıtla yalanladığında ya da madde saman adamsa. Uygulama: `dogrula2.py` istemi kanıt yokluğunu red sebebi saymıyor (`kanit_kapsiyor` alanı); `kilavuz.py` bu maddeleri Ek 2'ye koyuyor.
- 17:54 Tekilleştirme bitti: 724 ham → 543 tekil (`ham-sayfalar/birlesik.json`). saray-devlet Gemma'da iki kez zaman aşımına düştü, onun için yerel kelime benzerliğiyle (Jaccard ≥ 0,29) gruplandı; öteki 14 konu Gemma/Gemini ile. Çıkarıcıya göre 1798'e uymayan 189 madde yalnız A doğrulayıcısına gidecek (B kotası için).
- 17:55 TDV slug önerisi başladı (19 iş, gemma-4-31b-it; deneme: 12 maddede 21 önerinin 19'u TDV'de bulundu).
- 19:05 Kanıt hazır: 543 maddenin 353'ünde TDV kanıtı var, 190'ında yok (bunlar "belirsiz / kaynakta karşılığı yok" kümesine düşecek; elenmeyecek). TDV önbelleği `ham-sayfalar/tdv/`.
- 19:09 Doğrulama başladı: A gemma-4-31b-it 68 iş (8'lik; günlük `ham-sayfalar/dogA.log`), B gemini-3.1-flash-lite → kota dolunca gemini-3.5-flash-lite, 23 iş (16'lık, yalnız 1798 adayları; `ham-sayfalar/dogB.log`). Günlüğün sonunda BITTI satırı yoksa iş sürüyor ya da yarıda kaldı; aynı komutlar kaldığı yerden devam eder.
- 19:25 Hata bulundu ve düzeltildi: 19 TDV adresi (cariye, asker, bab-i-ali, deli, donanma…) gövdesi olmayan yönlendirme sayfasıymış; betik bunların yerine site arayüz yazısını "kanıt" diye veriyordu (58 madde etkilendi). `tdv.py` artık 300 karakterden kısa gövdeyi madde saymıyor; kanıt yeniden üretildi (543'ün 341'inde kanıt var, 202'sinde yok). A'nın etkilenen 3 işi yeniden kuyruğa alındı (eski çıktılar `log/*.eski-kanit.json`); B'nin etkilenen 42 maddesi gemini-3.5-flash-lite ile `dogB-duz-*` işlerinde yeniden doğrulandı (glob sırasında sonra okunduğu için eskisinin yerine geçer). Ayrıca kanıtta olmayan bir adrese dayanan onaylar `dogrula.py sonuc`'ta belirsize iner.
- 19:37 B bitti (23 + 3 düzeltme işi, gemini-3.1-flash-lite ve 3.5-flash-lite; 3.1-lite'ın günlük sınırı 20'den yüksekmiş). A gemma-4-31b-it ile sürüyor (68 iş, tahmini bitiş ~21:00).
- Ara örnekleme (orkestratör, 19:40): B'nin rastgele 8 onayı kanıt metniyle karşılaştırıldı. 5'i kanıtla destekli; 1'i kanıtta olmayan adrese dayanıyor (sonuç aşamasında otomatik belirsize iniyor); 2'sinde kanıt iddiayı desteklemiyor (M0529 "esâme" kanıtta yok; M0029 tokat sahnesi). B (lite) gevşek onaylıyor; "doğrulandı" için A'nın da onayı şart olduğundan bu süzülüyor, ama son örneklemede ayrıca bakılacak.
- Üçüncü doğrulayıcı (Kütüphaneci'nin önerisi, Yavuz'un OpenRouter anahtarı): `ucuncu.py`, nvidia/nemotron-3-ultra-550b-a55b:free, Google dışı aile, aynı TDV kanıtıyla; A/B bittikten sonra örneklemde (ayrışan maddeler + onaylılardan rastgele pay, en çok ~40 istek): `python ucuncu.py isler 12 40` → `python ucuncu.py calistir` → `python ucuncu.py sonuc` (dogrula.py sonuc'tan SONRA).
- `kilavuz.py` değişti: eleştiri kaynağı olmayan ve doğrulayıcılardan birinin saman adam dediği maddeler kılavuza girmiyor; kılavuzdaki video ve eleştiri kaynaklı madde sayısı yazılıyor.

## Sonuç – 13 Kasım 2026, ~21:50 (Orkestratör II)

- [x] Çıkarım, tekilleştirme, kanıt, doğrulama (A, B, C), kılavuz, örnekleme denetimi.
- A gemma-4-31b-it 68 iş bitti (20:58); B bitti; C (nvidia/nemotron-3-ultra-550b-a55b:free, OpenRouter) 20 iş / 233 madde bitti. C, A+B onaylı 124 maddenin 120'sine onay, 1'ine red (M0267 Rüstem Paşa pîşkeş), 3'üne belirsiz verdi; tek onaylı 93 maddenin 49'una onay verdi.
- Hata ve düzeltme: B düzeltme dosyaları (`dogB-duz-*`) Windows'ta glob sırasında eskilerden ÖNCE okunuyordu; `dogrula.py sonuc` artık düzeltmeleri en sona sıralıyor.
- Nihai durum kuralı (`kilavuz.py nihai`): A+B onayına C red → tartışmalı; tek onaya C onay → doğrulandı; tek redde C red → elendi; orkestratör denetim dosyası (`orkestrator-denetim.json`) her şeyin önünde.
- Sayılar: ham 724, tekil 543. Kılavuz gövdesi 142 (Bölüm I eleştiri/video kaynaklı 47, bunun 34'ü video; Bölüm II konu taraması 95). Ek 1 tek onay 40; Ek 2 belirsiz/kaynakta karşılığı yok 146 (111'i eleştiri kaynaklı); Ek 3 tartışmalı/şüpheli 12; Ek 4 başka dönem 26. Elenen 3, saman adam 2. Başka döneme ait ve doğrulanamayan 168 madde kılavuz dışında (`dogrulanmis/`).
- Orkestratör örnekleme denetimi: B'nin 8 onayı (2'si kanıtsız), "kesin hata"dan 12 madde ve C ile yükselen 6 madde kanıt metniyle karşılaştırıldı. 18 gövde maddesinin 3'ünde esaslı sorun (M0418, M0072, M0358 → Ek 3), 5'inde zayıf kanıt (bilgi muhtemelen doğru).
- Çıktı: `Tarih Hassasiyet Kılavuzu.md` (giriş `betikler/kilavuz_giris.md` + `ham-sayfalar/kilavuz-govde.md`), `dogrulanmis/<konu>.md`.

### Açık işler
- Kılavuz gövdesindeki maddelerin örnekleme dışındaki kısmı yalnız modellerce doğrulandı; denetimdeki hata oranı (~1/6) göz önüne alınarak öncelikle Bölüm I ve en çarpıcı maddeler insan gözüyle okunmalı.
- OpenCode kotası yenilenirse Ek 1 ve Ek 2 için Google dışı ikinci bir doğrulayıcı daha çalıştırılabilir.
- Yeniden üretmek için: `python dogrula.py sonuc` → `python ucuncu.py sonuc` → `python kilavuz.py` → `cat kilavuz_giris.md ../ham-sayfalar/kilavuz-govde.md > "../Tarih Hassasiyet Kılavuzu.md"` (giriş sayıları elle yazıldı; yeniden üretimde güncellenmeli).

### Devam adımları (Orkestratör II, güncel yol)
Hepsi `betikler/` içinde, `PYTHONUTF8=1` ile. Betikler biten işi atlar.
1. [x] Çıkarım bitti.
2. Tekilleştirme: `GEMINI_ARALIK=20 python gemini.py isler ../ham-sayfalar/isler-tekil.json 1 gemma-4-31b-it` (eksik konu kalmayana dek) → `python birlestir.py uygula`
3. `python dogrula2.py slug-isler 30` → `GEMINI_ARALIK=20 python gemini.py isler ../ham-sayfalar/isler-slug.json 2 gemma-4-31b-it` → `python dogrula2.py kanit`
4. `python dogrula2.py isler 8 15` → A: `GEMINI_ARALIK=20 python gemini.py isler ../ham-sayfalar/isler-dogA.json 2 gemma-4-31b-it`; B: `python gemini.py isler ../ham-sayfalar/isler-dogB.json 1 gemini-3.1-flash-lite`, kota dolarsa aynı komut `gemini-3.5-flash-lite` ile → `python dogrula.py sonuc`
5. `python kilavuz.py` → `ham-sayfalar/kilavuz-govde.md`'ye giriş ve en çarpıcı maddeler eklenerek `Tarih Hassasiyet Kılavuzu.md`.
6. Örnekleme ile kalite denetimi (TDV metni `tdv.py getir <slug>` ile okunabilir); her aşamada commit ve push.
