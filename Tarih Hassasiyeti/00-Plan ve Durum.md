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
- `kilavuz.py` değişti: eleştiri kaynağı olmayan ve doğrulayıcılardan birinin saman adam dediği maddeler kılavuza girmiyor; kılavuzdaki video ve eleştiri kaynaklı madde sayısı yazılıyor.

### Devam adımları
1. `cd betikler; set PYTHONUTF8=1`; kalan çıkarımı bitir: `python gemini.py isler ../ham-sayfalar/isler-kalan1.json 3`
2. `python birlestir.py topla` → `python birlestir.py isler > ../ham-sayfalar/isler-tekil.json` → `python gemini.py isler ../ham-sayfalar/isler-tekil.json 2` → `python birlestir.py uygula`
3. `python dogrula.py isler 6` → `python gemini.py isler ../ham-sayfalar/isler-dogA.json 2 gemini-3.5-flash` ve `python gemini.py isler ../ham-sayfalar/isler-dogB.json 2 gemini-3.1-flash-lite` → `python dogrula.py sonuc`
4. `python kilavuz.py` → `ham-sayfalar/kilavuz-govde.md`'ye giriş ve en çarpıcı maddeler eklenerek `Tarih Hassasiyet Kılavuzu.md`.
5. Örnekleme ile kalite denetimi; her aşamada commit ve push.
