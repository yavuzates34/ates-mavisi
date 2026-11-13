"""Aşama 4: bağımsız iki ücretsiz modelle doğrulama.

python dogrula.py isler [parti=6] > isler.json   (birlesik.json'dan; iki doğrulayıcı için ayrı işler)
python dogrula.py sonuc                          (iki doğrulayıcının kararlarını birleştirir -> ham-sayfalar/dogrulama-sonuc.json)
"""
import glob, json, os, sys
from collections import Counter

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOGRULAYICILAR = {"A": "gemini/gemini-3.5-flash",
                  "B": os.environ.get("DOG_B", "gemini/gemini-3.1-flash-lite")}  # OpenCode kotası yenilenirse DOG_B=opencode/mimo-v2.6-flash-free ile oc.py

ISTEM = (
    "Sen bir Osmanlı tarihi doğrulayıcısısın. Bir alternatif tarih romanı 1798-1800 İstanbul'unda (III. Selim dönemi) geçiyor. "
    "Çalışma klasöründeki girdi.json dosyasını read aracıyla oku. İçinde, dizi ve filmlerde yapıldığı söylenen tarih hatalarına dair maddeler var "
    "('yanlis' yanlış kullanım, 'dogru' önerilen doğrusu). Maddeleri hazırlayan model zayıftır; hiçbirine baştan güvenme. "
    "Her madde için: önce TDV İslam Ansiklopedisi'nde ilgili maddeyi webfetch ile aç (adres biçimi https://islamansiklopedisi.org.tr/<madde-adi>, "
    "Türkçe harfsiz, küçük harf, kelimeler tireli; ör. https://islamansiklopedisi.org.tr/kapikulu, https://islamansiklopedisi.org.tr/fes, "
    "https://islamansiklopedisi.org.tr/selim-iii; adres açılmazsa en olası başka adı dene). "
    "TDV'de yoksa üniversite yayını veya dergipark makalesi gibi güvenilir bir kaynağın adresini aç. "
    "Sonra karar ver: 'dogru' alanındaki bilgi 1798-1800 için kaynakça destekleniyor mu? "
    "karar: 'onay' (kaynak açıkça destekliyor), 'red' (kaynak çürütüyor ya da madde yanlış), 'belirsiz' (kaynak bulamadın ya da kaynak net değil). "
    "Kaynağı gerçekten açıp okumadıysan 'onay' verme. Adres uydurma. Kaynaktan en çok 15 kelime alıntı ya da özet yaz. "
    "Madde başka bir döneme aitse (ör. 13. ya da 16. yüzyıl için doğru ama 1798'de durum farklı) bunu gecerli_1798 ve not alanında belirt. "
    "Ayrıca 'saman_adam' alanında şunu değerlendir: 'yanlis' alanındaki kullanım gerçekten dizi, film ya da popüler anlatıda görülen, "
    "bir yazarın düşebileceği bir hata mı ('hayır'), yoksa kimsenin yapmadığı, doğruyu anlatmak için uydurulmuş yapay bir yanlış mı ('evet')? "
    "Bütün metin Türkçe. Sonunda YALNIZCA tek bir ```json bloğu yaz, girdideki her madde için bir kayıt: "
    '[{"mid": "", "karar": "onay|red|belirsiz", "gecerli_1798": "evet|hayır|kısmen", "saman_adam": "evet|hayır", '
    '"duzeltme": "dogru alanı eksik ya da hatalıysa düzeltilmiş hali, değilse boş", '
    '"kaynak_url": "", "kaynak_ozet": "en çok 15 kelime", "not": "en çok 2 cümle"}]'
)


def isler():
    parti = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    ms = json.load(open(os.path.join(KOK, "ham-sayfalar", "birlesik.json"), encoding="utf-8"))
    # kota yarıda biterse en değerliler doğrulanmış olsun: 1798'e uyan, eleştiri/video kaynaklı maddeler önce
    ms.sort(key=lambda m: (str(m.get("gecerli_1798")).lower().startswith("hay"), not m.get("kaynaklar"), m["mid"]))
    hafif = [{k: m.get(k) for k in ("mid", "yanlis", "dogru", "aciklama", "donem", "gecerli_1798")} for m in ms]
    out = []
    for harf, model in DOGRULAYICILAR.items():
        for i in range(0, len(hafif), parti):
            p = hafif[i:i + parti]
            ad = f"dog{harf}-{p[0]['mid']}"
            out.append({"ad": ad, "model": model, "istem": ISTEM, "girdi": json.dumps(p, ensure_ascii=False, indent=1),
                        "cikti": f"ham-sayfalar/dogrulama/{ad}.json", "sure": 1500})
    for harf in DOGRULAYICILAR:
        json.dump([x for x in out if x["ad"].startswith("dog" + harf)],
                  open(os.path.join(KOK, "ham-sayfalar", f"isler-dog{harf}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out))


def sonuc():
    ms = {m["mid"]: m for m in json.load(open(os.path.join(KOK, "ham-sayfalar", "birlesik.json"), encoding="utf-8"))}
    kararlar = {h: {} for h in DOGRULAYICILAR}
    global KANIT
    ky = os.path.join(KOK, "ham-sayfalar", "kanit.json")
    KANIT = json.load(open(ky, encoding="utf-8")) if os.path.exists(ky) else {}
    # düzeltme işleri (-duz-) eskilerin üstüne yazılsın diye en sona
    for yol in sorted(glob.glob(os.path.join(KOK, "ham-sayfalar", "dogrulama", "*.json")), key=lambda y: ("-duz-" in y, y)):
        d = json.load(open(yol, encoding="utf-8"))
        harf = os.path.basename(yol)[3]
        v = d["veri"]
        if isinstance(v, dict):
            v = next((x for x in v.values() if isinstance(x, list)), [])
        norm = lambda u: (u or "").strip().lower().rstrip("/").replace("http://", "https://").replace("://www.", "://")
        okunan = {norm(u["url"]) for u in d.get("okunan_adresler", []) if u.get("durum") == "SUCCESS"}
        if str(d.get("model", "")).startswith("opencode/"):
            # OpenCode: başarılı okumalar günlükte "% WebFetch <adres>" satırı olarak görünür
            for lg in glob.glob(os.path.join(KOK, "ham-sayfalar", "log", d["ad"] + ".*.txt")):
                for satir in open(lg, encoding="utf-8", errors="replace"):
                    s = satir.strip()
                    if s.startswith("% WebFetch "):
                        okunan.add(norm(s.split()[2]))
        for k in v:
            if isinstance(k, dict) and k.get("mid") in ms:
                k["model"] = d["model"]
                # kanıta dayalı yolda (dogrula2.py) betiğin indirdiği TDV adresleri okunmuş sayılır
                okunan_m = okunan | {norm(e["url"]) for e in KANIT.get(k["mid"], [])}
                # kaynağı gerçekten okunmamış onay sayılmaz
                if k.get("karar") == "onay" and norm(k.get("kaynak_url")) not in okunan_m:
                    k["karar_ilk"] = "onay"
                    k["karar"] = "belirsiz"
                    k["not"] = ((k.get("not") or "") + " [Orkestratör: gösterilen kaynak bu oturumda okunmuş görünmüyor, onay belirsize indirildi.]").strip()
                kararlar[harf][k["mid"]] = k
    sayac = Counter()
    for mid, m in ms.items():
        a, b = kararlar["A"].get(mid), kararlar["B"].get(mid)
        ka = (a or {}).get("karar", "yok") if (a and (a.get("kaynak_url") or a.get("karar") != "onay")) else ("belirsiz" if a else "yok")
        kb = (b or {}).get("karar", "yok") if (b and (b.get("kaynak_url") or b.get("karar") != "onay")) else ("belirsiz" if b else "yok")
        if ka == "onay" and kb == "onay":
            s = "dogrulandi"
        elif "onay" in (ka, kb) and "red" in (ka, kb):
            s = "tartismali"
        elif ka == "red" and kb == "red":
            s = "elendi"
        elif "onay" in (ka, kb):
            s = "tek-onay"      # biri onay, diğeri belirsiz/yok
        elif "red" in (ka, kb):
            s = "tek-red"
        else:
            s = "dogrulanamadi"
        m["dogrulama"] = {"A": a, "B": b, "sonuc": s}
        sayac[s] += 1
    json.dump(list(ms.values()), open(os.path.join(KOK, "ham-sayfalar", "dogrulama-sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(dict(sayac), "A:", len(kararlar["A"]), "B:", len(kararlar["B"]))


if __name__ == "__main__":
    {"isler": isler, "sonuc": sonuc}[sys.argv[1]]()
