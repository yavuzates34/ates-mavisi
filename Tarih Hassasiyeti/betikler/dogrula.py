"""Aşama 4: bağımsız iki ücretsiz modelle doğrulama.

python dogrula.py isler [parti=6] > isler.json   (birlesik.json'dan; iki doğrulayıcı için ayrı işler)
python dogrula.py sonuc                          (iki doğrulayıcının kararlarını birleştirir -> ham-sayfalar/dogrulama-sonuc.json)
"""
import glob, json, os, sys
from collections import Counter

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOGRULAYICILAR = {"A": "opencode/glm-5.3-flash-free", "B": "opencode/mimo-v2.6-flash-free"}

ISTEM = (
    "Sen bir Osmanlı tarihi doğrulayıcısısın. Bir alternatif tarih romanı 1798-1800 İstanbul'unda (III. Selim dönemi) geçiyor. "
    "Çalışma klasöründeki girdi.json dosyasını read aracıyla oku. İçinde, dizi ve filmlerde yapıldığı söylenen tarih hatalarına dair maddeler var "
    "('yanlis' yanlış kullanım, 'dogru' önerilen doğrusu). Maddeleri hazırlayan model zayıftır; hiçbirine baştan güvenme. "
    "Her madde için: önce TDV İslam Ansiklopedisi'nde ilgili maddeyi webfetch ile aç (adres biçimi https://islamansiklopedisi.org.tr/<madde-adi>, "
    "ör. https://islamansiklopedisi.org.tr/kapikulu, https://islamansiklopedisi.org.tr/fes; madde adını bilmiyorsan websearch ile "
    "'site:islamansiklopedisi.org.tr <terim>' ara). TDV'de yoksa üniversite yayını veya dergipark makalesi gibi güvenilir bir kaynak bul. "
    "Sonra karar ver: 'dogru' alanındaki bilgi 1798-1800 için kaynakça destekleniyor mu? "
    "karar: 'onay' (kaynak açıkça destekliyor), 'red' (kaynak çürütüyor ya da madde yanlış), 'belirsiz' (kaynak bulamadın ya da kaynak net değil). "
    "Kaynağı gerçekten açıp okumadıysan 'onay' verme. Adres uydurma. Kaynaktan en çok 15 kelime alıntı ya da özet yaz. "
    "Madde başka bir döneme aitse (ör. 13. ya da 16. yüzyıl için doğru ama 1798'de durum farklı) bunu gecerli_1798 ve not alanında belirt. "
    "Bütün metin Türkçe. Sonunda YALNIZCA tek bir ```json bloğu yaz, girdideki her madde için bir kayıt: "
    '[{"mid": "", "karar": "onay|red|belirsiz", "gecerli_1798": "evet|hayır|kısmen", '
    '"duzeltme": "dogru alanı eksik ya da hatalıysa düzeltilmiş hali, değilse boş", '
    '"kaynak_url": "", "kaynak_ozet": "en çok 15 kelime", "not": "en çok 2 cümle"}]'
)


def isler():
    parti = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    ms = json.load(open(os.path.join(KOK, "ham-sayfalar", "birlesik.json"), encoding="utf-8"))
    hafif = [{k: m.get(k) for k in ("mid", "yanlis", "dogru", "aciklama", "donem", "gecerli_1798")} for m in ms]
    out = []
    for harf, model in DOGRULAYICILAR.items():
        for i in range(0, len(hafif), parti):
            p = hafif[i:i + parti]
            ad = f"dog{harf}-{p[0]['mid']}"
            out.append({"ad": ad, "model": model, "istem": ISTEM, "girdi": json.dumps(p, ensure_ascii=False, indent=1),
                        "cikti": f"ham-sayfalar/dogrulama/{ad}.json", "sure": 1500})
    # A ve B işlerini iç içe sırala ki ikisi paralel ilerlesin
    a = [x for x in out if x["ad"].startswith("dogA")]
    b = [x for x in out if x["ad"].startswith("dogB")]
    sirali = [x for pair in zip(a, b) for x in pair]
    print(json.dumps(sirali, ensure_ascii=False, indent=1))


def sonuc():
    ms = {m["mid"]: m for m in json.load(open(os.path.join(KOK, "ham-sayfalar", "birlesik.json"), encoding="utf-8"))}
    kararlar = {h: {} for h in DOGRULAYICILAR}
    for yol in glob.glob(os.path.join(KOK, "ham-sayfalar", "dogrulama", "*.json")):
        d = json.load(open(yol, encoding="utf-8"))
        harf = os.path.basename(yol)[3]
        v = d["veri"]
        if isinstance(v, dict):
            v = next((x for x in v.values() if isinstance(x, list)), [])
        for k in v:
            if isinstance(k, dict) and k.get("mid") in ms:
                k["model"] = d["model"]
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
