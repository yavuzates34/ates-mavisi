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
- [ ] Kaynak toplama
- [ ] Video kaynakları (arama, transkript, çıkarım)
- [ ] Konu taraması
- [ ] Birleştirme
- [ ] Doğrulama
- [ ] Kalite denetimi
- [ ] Kılavuz

## Sorunlar ve notlar

- İlk deneme işi takıldı: Python'dan başlatılan `opencode run` standart girdiyi bekliyordu. `stdin=DEVNULL` ile düzeltildi (13 Kasım 14:57).
- OpenCode, iş klasörü yerine git kökünü (Ateş Mavisi) proje dizini olarak görüyor. İstemler dosya yazdırmıyor; yine de her aşama sonunda `git status` ile kitap dosyalarına dokunulmadığı denetleniyor.

- Pakalın'ın sözlüğü çevrimiçi serbest erişimde değil; doğrulamada pratikte TDV İslam Ansiklopedisi birincil başvuru oldu.
