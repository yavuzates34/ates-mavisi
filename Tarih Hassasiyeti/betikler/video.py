"""Video aşaması: YouTube arama, altyazı (transkript) çekme ve çıkarım işleri.

python video.py ara        -> ham-sayfalar/video/adaylar.json (yt-dlp arama)
python video.py altyazi    -> ham-sayfalar/video/<id>.tr.vtt ve <id>.txt (zaman damgalı düz metin)
python video.py isler      -> çıkarım iş listesi (stdout)
python video.py liste      -> kaynaklar/video-listesi.md
"""
import glob, html, json, os, re, subprocess, sys
from isler_uret import KONULAR, MADDE

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VD = os.path.join(KOK, "ham-sayfalar", "video")

SORGULAR = [
    "Murat Bardakçı dizi hataları", "Murat Bardakçı Muhteşem Yüzyıl", "Murat Bardakçı Payitaht hatalar", "Murat Bardakçı Kuruluş Osman",
    "Murat Bardakçı tarihi dizi kıyafet", "Murat Bardakçı Kösem dizisi",
    "İlber Ortaylı dizi eleştirisi", "İlber Ortaylı Muhteşem Yüzyıl", "İlber Ortaylı tarihi diziler", "İlber Ortaylı Diriliş Ertuğrul",
    "Ceren Sungur dizi hataları", "Ceren Sungur Muhteşem Yüzyıl", "Ceren Sungur Kuruluş Osman", "Ceren Sungur tarihi dizi",
    "Emrah Safa Gürkan dizi", "Emrah Safa Gürkan Muhteşem Yüzyıl", "Emrah Safa Gürkan Rise of Empires", "Emrah Safa Gürkan tarihi dizi hataları",
    "Erhan Afyoncu dizi hataları", "Erhan Afyoncu Muhteşem Yüzyıl", "Erhan Afyoncu Kuruluş Osman", "Erhan Afyoncu tarihi diziler",
    "Feridun Emecen dizi", "Halil İnalcık Muhteşem Yüzyıl", "Ahmet Şimşirgil dizi hataları", "Ekrem Buğra Ekinci dizi hataları",
    "tarihi dizilerdeki hatalar Osmanlı", "Osmanlı dizilerinde yapılan tarihi hatalar", "Muhteşem Yüzyıl tarihi hatalar",
    "Payitaht Abdülhamid tarihi hatalar", "Kuruluş Osman tarihi hatalar", "Rise of Empires Ottoman hatalar",
    "Mehmed Fetihler Sultanı hatalar", "tarihi dizilerde kostüm hataları", "Osmanlı'da yeniçeri dizilerde yanlış",
]
ANAHTAR = re.compile(r"dizi|film|hata|yanlış|muhteşem|payitaht|kuruluş|diriliş|kösem|netflix|rise of|fetihler|barbaros|sinema|senaryo|kostüm|anakron|gerçek mi|gerçekler", re.I)


def ara():
    import yt_dlp
    os.makedirs(VD, exist_ok=True)
    adaylar = {}
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
        for q in SORGULAR:
            try:
                r = ydl.extract_info(f"ytsearch12:{q}", download=False)
            except Exception as e:
                print("hata", q, e); continue
            for e in r.get("entries") or []:
                vid, baslik = e.get("id"), e.get("title") or ""
                sure = e.get("duration") or 0
                if not vid or vid in adaylar or not ANAHTAR.search(baslik) or sure < 90 or sure > 7200:
                    continue
                adaylar[vid] = {"id": vid, "baslik": baslik, "kanal": e.get("channel") or e.get("uploader"), "sure": sure, "sorgu": q}
    json.dump(list(adaylar.values()), open(os.path.join(VD, "adaylar.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(adaylar))


def vtt_metin(yol):
    sat, son, bas = [], None, None
    blok = []
    for satir in open(yol, encoding="utf-8", errors="replace"):
        m = re.match(r"(\d+):(\d+):(\d+)\.\d+ -->", satir)
        if m:
            t = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
            if bas is None or t - bas >= 30:
                if blok:
                    sat.append(f"[{bas//60:02d}:{bas%60:02d}] " + " ".join(blok))
                blok, bas = [], t
            continue
        s = html.unescape(re.sub(r"<[^>]+>", "", satir)).replace(">>", "").strip()
        if not s or s.startswith(("WEBVTT", "Kind:", "Language:")) or s == son:
            continue
        son = s
        if not blok or blok[-1] != s:
            blok.append(s)
    if blok:
        sat.append(f"[{bas//60:02d}:{bas%60:02d}] " + " ".join(blok))
    return "\n".join(sat)


def altyazi():
    secilen = json.load(open(os.path.join(VD, "secilen.json"), encoding="utf-8"))
    for v in secilen:
        txt = os.path.join(VD, f"{v['id']}.txt")
        if os.path.exists(txt):
            continue
        subprocess.run([sys.executable, "-m", "yt_dlp", "--skip-download", "--write-auto-subs", "--write-subs",
                        "--sub-langs", "tr", "--sub-format", "vtt", "-o", os.path.join(VD, "%(id)s.%(ext)s"),
                        f"https://www.youtube.com/watch?v={v['id']}"], capture_output=True, timeout=180)
        vtts = glob.glob(os.path.join(VD, f"{v['id']}*.vtt"))
        if vtts:
            open(txt, "w", encoding="utf-8").write(vtt_metin(vtts[0]))
            print(v["id"], "tamam", os.path.getsize(txt))
        else:
            print(v["id"], "altyazı yok")


def isler():
    secilen = {v["id"]: v for v in json.load(open(os.path.join(VD, "secilen.json"), encoding="utf-8"))}
    madde = MADDE.replace('"kaynak_url": "adres"', '"kaynak_url": "https://youtu.be/<id>?t=<saniye>", "zaman": "dk:sn"')
    out = []
    for txt in sorted(glob.glob(os.path.join(VD, "*.txt"))):
        vid = os.path.basename(txt)[:-4]
        v = secilen.get(vid)
        metin = open(txt, encoding="utf-8").read()
        if not v or len(metin) < 500:
            continue
        # uzun transkriptleri ~35 bin karakterlik parçalara böl
        NL = chr(10)
        satirlar, parcalar, cur = metin.split(NL), [], []
        for st in satirlar:
            cur.append(st)
            if sum(len(x) for x in cur) > 35000:
                parcalar.append(NL.join(cur)); cur = []
        if cur:
            parcalar.append(NL.join(cur))
        for pi, parca in enumerate(parcalar):
          ek = f"-p{pi+1}" if len(parcalar) > 1 else ""
          istem = (
            "Bir alternatif tarih romanı 1798-1800 İstanbul'unda (III. Selim dönemi) geçiyor. Osmanlı konulu dizi ve filmlerde tarihçilerin eleştirdiği bariz hataları topluyoruz. "
            f"Çalışma klasöründeki girdi.json dosyası aslında düz metin: '{v['baslik']}' başlıklı YouTube videosunun ({v['kanal']}, https://youtu.be/{vid}) "
            "otomatik Türkçe altyazısı; her satır [dk:sn] zaman damgasıyla başlıyor. Dosyayı read aracıyla baştan sona oku (uzunsa parça parça). "
            "Otomatik altyazıda konuşma tanıma hataları olur, Osmanlı terimleri yanlış yazılmış olabilir; terimi bağlamdan doğru biçimine çevir, emin değilsen maddeyi yazma. "
            "Görev: konuşmacının dizi ve filmlerde eleştirdiği ya da 'aslında böyle değildi' dediği somut tarih bilgilerini madde madde çıkar "
            "(unvan, kıyafet, teşkilat, dil, mekân, harem, ordu, gündelik hayat vb.). Konuşmacının söylemediği bir şeyi ekleme, web'e çıkma. "
            "kisi alanına konuşmacının adını (başlık ve kanaldan anlaşılan), kaynak_url alanına https://youtu.be/" + vid + "?t=<saniye> yaz, zaman alanına [dk:sn] değerini koy, "
            "kaynak_ozet alanına konuşmacının sözünün en çok 15 kelimelik özetini yaz. Dönem ayrımına dikkat et: 16. yüzyılda doğru olan 1798'de yanlış olabilir. "
            "Videoda dizi/film eleştirisi ya da somut tarih düzeltmesi yoksa boş liste döndür. "
            "Sonunda YALNIZCA tek bir ```json bloğu yaz, biçimi: {\"maddeler\": [" + madde + "]}"
        )
          out.append({"ad": f"video-{vid}{ek}", "model": "opencode/deepseek-v4.1-flash-free", "istem": istem, "girdi": parca,
                    "cikti": f"ham/video-{vid}{ek}.json", "sure": 1200})
    print(json.dumps(out, ensure_ascii=False, indent=1))


def liste():
    secilen = json.load(open(os.path.join(VD, "secilen.json"), encoding="utf-8"))
    sat = ["# Video kaynakları", "", "YouTube'da yt-dlp aramasıyla bulunan ve otomatik Türkçe altyazısı (transkripti) çekilen videolar. "
           "Ham transkriptler git dışında (`ham-sayfalar/video/`). Madde sayısı, ücretsiz modelin transkriptten çıkardığı ham madde sayısıdır.", ""]
    for v in secilen:
        txt = os.path.join(VD, f"{v['id']}.txt")
        n = 0
        hs = glob.glob(os.path.join(KOK, "ham", f"video-{v['id']}*.json"))
        for h in hs:
            d = json.load(open(h, encoding="utf-8"))["veri"]
            n += len(d.get("maddeler", []) if isinstance(d, dict) else d)
        n = n if hs else "-"
        durum = "transkript var" if os.path.exists(txt) else "altyazı yok"
        sat.append(f"- {v['baslik']} | {v['kanal']} | {v['sure']//60} dk | <https://youtu.be/{v['id']}> | {durum} | madde: {n}")
    open(os.path.join(KOK, "kaynaklar", "video-listesi.md"), "w", encoding="utf-8").write("\n".join(sat) + "\n")


if __name__ == "__main__":
    {"ara": ara, "altyazi": altyazi, "isler": isler, "liste": liste}[sys.argv[1]]()
