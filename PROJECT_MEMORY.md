# Project memory — Ateş Mavisi

Second Brain project id: `539d3197fb9ab3c96152d3be`  
Second Brain record: `projects/539d3197fb9ab3c96152d3be.md`

This file is the compact, project-local handoff. Keep it factual and source-linked.

## Purpose

Yavuz Ateş alternatif tarih roman serisinin (1798 Osmanlı, zaman yolcusu mühendis) çalışma klasörü. Kanon: `Yavuz Ateş Serisi – Dizi Defteri.md`. Kitaplar claude.ai sohbetlerinde yazıldı; son sohbetin ekran görüntüleri `son claude sohbet oturumu.pdf` (metin katmanı yok).

## Decisions and rationale

- 9 Kasım 2026 20:50: Yavuz bu klasördeki Claude Code oturumuna "Kütüphaneci" adını verdi; oturum kimliği `fa42d7d9-4fd4-489d-a78b-1a79cb754111`. Kayıt: `CLAUDE.md`.
- 9 Kasım 2026 21:28–21:35: Yavuz onayladı ve deftere işlendi: ibret-i âlem kuralı (Et Meydanı yemini yalnız gözdağı); 3. Kitap 10 bölüm + 4 ara sahne; Tipu ölü kalır, kolordu Maskat'ta takıldı, Wellesley esir ve takas yok, Selim Ekim–Kasım 1799'da ölür, Korfu ara sahnesi Ağustos 1799, Balo Bölüm 8 (Ocak 1800), Kent 9, Westminster 10. Gerekçe: Bölüm 4 sonu Tipu'nun ölümüne kurulu; balo esir değişimiyle açıldığı için çıkarmadan önce olmalı.

- 13 Kasım 2026 17:43: Tarih hassasiyeti araştırmasının ikinci dalgası için Yavuz onayı: önce Osmanlı kılavuzu (Tarih Orkestratörü II yürütüyor) bitip yöntem değerlendirilecek; iş görüyorsa Britanya ve Fransa aynı düzenle (tarihçi eleştirisi + kaynakla doğrulama, İngilizce kaynak ağırlıklı), Rusya/Avusturya/Prusya orta düzey, Asya/Afrika/Amerika yalnız kısa "bariz hata" listesi; ülke önceliği yeni senaryo netleşince. İkinci dalganın orkestratörü Codex'te gpt-6.1-sol, xhigh olacak (Yavuz). Başlangıç en erken 14 Kasım 11:00 sonrası (Gemini günlük kotaları). Gerekçe: Osmanlı kadar titizlik gerekmeyebilir ama "tamamen de boşveremeyiz".
- 13 Kasım 2026 17:22: Doğrulamada TDV'de karşılığı olmayan (gündelik dil, hitap) maddeler elenmez, "belirsiz" diye ayrı tutulur (Yavuz onayı).

- 13 Kasım 2026 19:09: Yavuz netleştirdi: ilk seri (Mühür, Ada, yarım Yıldırım) yayımlanmayacak deneme eserleridir. Asıl seri `master` üzerinde yazılacak. Sıra: önce tarih hassasiyeti kılavuzları biter; sonra ayrı bir oturumda Fable modeli orkestratör olarak çalışır, Opus alt ajanlarıyla üç ChatGPT oturumunu (zip) okutur, parçaları kuş bakışı birleştirir ve yeni asıl seri için Yavuz'la diyaloğa geçer. Kütüphaneci bu oturumu başlatmaz; zip'i açmaz. Yayın: ElevenReader gibi platformlara konacak kitap yeni asıl seri olacak; ilk seri silinmez (`ilk-seri` dalında korunur) ama yayımlanmaz (Yavuz, 19:27).

## Current status

- 1. Kitap Mühür (6 bölüm) ve 2. Kitap Ada (5 bölüm + ara sahne) tamam. 3. Kitap Yıldırım'da 4 bölüm ve 2 ara sahne (Kutu, Mühendis) var; defter planı artık 10 bölüm ve 4 ara sahne (Kutu, Mühendis, Mihaylovski, Korfu).
- 9 Kasım 2026 akşamı: dört Opus alt ajanıyla (Mühür, Ada, Yıldırım, Sohbet okuyucuları) seri boyu çelişki taraması yapıldı; kritik bulgular satır satır doğrulandı. Ayrıntılı rapor: `Tutarlılık Taraması – 9 Kasım 2026.md`. Kitap dosyalarına henüz dokunulmadı.

- 9–10 Kasım 2026, Orkestratör (Kütüphaneci'nin başlattığı Claude Code oturumu) Aşama 1'i bitirdi: üç kitapta taramadaki net hatalar ve karar verilen konular işlendi (Bölüm 4 Mısır/Tipu/başpare, Silahdar'ın sırları, İrlanda uyarısı Ağustos 1798'e, Walsh–Tone, Kutu 18 Mart, Bozcaada 4 Mayıs, Holwood 19 Haziran, İngiliz şoku), yazar notları `Yazar Notları.md`'ye taşındı, defter ve README güncellendi, odaklı Opus doğrulaması yapıldı. Bölüm 5 planı `Bölüm 5 sahne planı.md`, Yavuz'un onayında.

## Open issues

- Bölüm 5 sahne planı ve Bölüm 6'nın Ağustos sonu–Eylül 1799'a kayması Yavuz'un onayını bekliyor.
- 12 Kasım 2026 19:05: Yavuz'un isteğiyle depo özel (private) GitHub deposuna pushlandı: https://github.com/yavuzates34/ates-mavisi (oluşturulma 2026-11-12T16:05:39Z). Amaç: kitaplara tarih damgası; zamanı gelince Yavuz public yapacak. Bundan sonra commit'ler pushlanır.
- 12 Kasım 2026 19:14: İlk seri dondu: `ilk-seri-v1` etiketi + GitHub release, `ilk-seri` branch'i (eski seriye düzeltmeler için). Yavuz 3. kitabı muhtemelen bitirmeyecek; ChatGPT'de 3 dallı oturumda (zamanda yolculuk, Osmanlı yönetimi, İngiltere'ye kansız strateji) yeni senaryo konuştu. Kayıtları handoff olarak getirecek; yeni senaryo `master` üzerinde ilerleyecek.
- 14 MB PDF commit edilmedi (büyük dosya).

- 13 Kasım 2026 ~21:50: Osmanlı (1798–1800) Tarih Hassasiyet Kılavuzu ilk sürümü bitti (`Tarih Hassasiyeti/Tarih Hassasiyet Kılavuzu.md`, commit 78cac9b, origin ile eşit). Ham 724, tekil 543; gövde 142 madde (Bölüm I eleştiri kaynaklı 47, 34'ü video; Bölüm II konu taraması 95); Ek 1 tek onay 40, Ek 2 belirsiz 146 (elenmedi, Yavuz'un kuralı), Ek 3 tartışmalı 12, Ek 4 başka dönem 26; 3 elendi, 2 saman adam. Doğrulayıcılar TDV kanıtı üzerinde: A gemma-4-31b-it, B gemini-3.1-flash-lite (42'sinde 3.5-flash-lite), C Nemotron 3 Ultra (OpenRouter, Google dışı, 233 madde). Kütüphaneci kontrolü: bölüm sayıları raporla tutuyor, denetimle indirilen 3 madde Ek 3'te. Zayıflıklar: orkestratör örneklemesinde 18 gövde maddesinin 3'ünde esaslı hata (yaklaşık altıda bir); doğrulayıcılar gevşek onaylıyor; gövdede 1798'le ilgisi zayıf ~20 madde var (ör. oyuncu yaşı, 13. yüzyıl "destur"), çünkü doğrulayıcılar dönem uygunluğunu değil olgunun doğruluğunu onayladı.

## Next step

- Yeni bağlamda (oturum başı veya compact sonrası) `Kütüphaneci Günlüğü.md`'nin son girişlerini oku; karar olmayan fikir ve tercihler orada. Günlük konuşma sürerken yazılır, compact beklenmez.

- Osmanlı kılavuzu bitti ve Yavuz'a aktarıldı (13 Kasım ~21:50). Açık işler: Bölüm I'in insan gözüyle okunması; gövdeden 1798'le ilgisiz maddelerin ayıklanması. Fable oturumu ve ikinci dalga (Britanya, Fransa; Codex gpt-6.1-sol xhigh) Yavuz'un kuracağı iş; Kütüphaneci istenmedikçe başlatmaz, brifi ancak istenirse yazar.
- Yavuz'un ChatGPT konuşma kayıtlarını (handoff) almak; oturumlar arası çelişkileri ayıklayıp sade liste sunmak; yeni senaryoyu `master`'da kurmak. Bölüm 5 askıda.
- (Geçersiz, 13 Kasım 19:09) Mühür'ü erken yayımlama önerisi düştü: ilk seri yayımlanmayacak bir deneme eseri.
