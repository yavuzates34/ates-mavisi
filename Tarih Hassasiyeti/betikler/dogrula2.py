"""Aşama 4 (ikinci yol, 13 Kasım 16:45): kanıta dayalı doğrulama.

Gemini'nin ücretsiz katmanında her model günde ~20 istekle sınırlı çıktı; url_context ile
madde başına kaynak aramak bu kotaya sığmıyor. Bunun yerine:
  1. slug   : gemma, her madde için TDV madde adı (slug) ve anahtar kelime önerir (iş listesi üretir).
  2. kanit  : betik TDV maddelerini kendisi indirir (tdv.py), ilgili paragrafları seçer -> ham-sayfalar/kanit.json
  3. isler  : iki doğrulayıcı aynı kanıtı birbirinden bağımsız okuyup karar verir.
     A: gemma-4-31b-it (araçsız)   B: gemini-3.1-flash-lite (kanıt + gerekirse url_context)
  4. sonuc  : dogrula.py sonuc (kanıt adresleri "okunmuş" sayılır).

python dogrula2.py slug-isler [parti=30]
python dogrula2.py kanit
python dogrula2.py isler [partiA=8] [partiB=15]
"""
import json, os, sys, glob
from concurrent.futures import ThreadPoolExecutor
import tdv

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HS = os.path.join(KOK, "ham-sayfalar")


def maddeler():
    ms = json.load(open(os.path.join(HS, "birlesik.json"), encoding="utf-8"))
    ms.sort(key=lambda m: (str(m.get("gecerli_1798")).lower().startswith("hay"), not m.get("kaynaklar"), m["mid"]))
    return ms


SLUG_ISTEM = (
    "Aşağıdaki GİRDİ'de Osmanlı konulu dizi/filmlerdeki tarih hatalarına dair maddeler var. Her madde için, iddiayı doğrulamaya "
    "en uygun TDV İslâm Ansiklopedisi maddelerinin adres adlarını (slug) öner: 1-3 tane, en ilgilisi önce. Slug biçimi: Türkçe harfsiz, küçük harf, "
    "kelimeler tireli; ör. kapikulu, yeniceri, kavuk, fes, selim-iii, valide-sultan, harem, sadrazam, divan-i-humayun, kahve, tutun, "
    "kazasker, reisulkuttab, enderun, bostanci, nizam-i-cedid. Gerçekte var olduğunu bildiğin madde adlarını yaz. "
    "Ayrıca metinde aranacak 3-6 Türkçe anahtar kelime ver (terimler, unvanlar, eşya adları). "
    "Çıktı: YALNIZCA tek bir ```json bloğu: [{\"mid\": \"\", \"sluglar\": [\"\"], \"anahtarlar\": [\"\"]}]"
)


def slug_isler():
    parti = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    ms = maddeler()
    out = []
    for i in range(0, len(ms), parti):
        p = [{k: m.get(k) for k in ("mid", "yanlis", "dogru")} for m in ms[i:i + parti]]
        ad = f"slug-{p[0]['mid']}"
        out.append({"ad": ad, "istem": SLUG_ISTEM, "girdi": json.dumps(p, ensure_ascii=False, indent=0),
                    "cikti": f"ham-sayfalar/slug/{ad}.json"})
    json.dump(out, open(os.path.join(HS, "isler-slug.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out))


def kanit():
    oneri = {}
    for yol in glob.glob(os.path.join(HS, "slug", "*.json")):
        v = json.load(open(yol, encoding="utf-8"))["veri"]
        if isinstance(v, dict):
            v = next((x for x in v.values() if isinstance(x, list)), [])
        for k in v:
            if isinstance(k, dict) and k.get("mid"):
                oneri[k["mid"]] = k
    ms = maddeler()

    def bir(m):
        o = oneri.get(m["mid"], {})
        anahtar = [a for a in (o.get("anahtarlar") or []) if isinstance(a, str)]
        bulunan = []
        for s in (o.get("sluglar") or [])[:3]:
            if not isinstance(s, str):
                continue
            d = tdv.getir(s)
            if d and d["url"] not in [b["url"] for b in bulunan]:
                bulunan.append(d)
            if len(bulunan) >= 2:
                break
        if not bulunan and anahtar:
            for s in tdv.ara(anahtar[0], 2):
                d = tdv.getir(s)
                if d:
                    bulunan.append(d)
        kel = anahtar + [w.strip(".,;:'\"()") for w in (m.get("dogru") or "").split() if len(w) > 4][:8]
        return m["mid"], [{"url": d["url"], "baslik": d["baslik"], "parca": tdv.parca(d, kel, 1500)} for d in bulunan[:2]]

    with ThreadPoolExecutor(4) as ex:
        sonuc = dict(ex.map(bir, ms))
    json.dump(sonuc, open(os.path.join(HS, "kanit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("madde", len(sonuc), "kanıtlı", sum(1 for v in sonuc.values() if v), "kanıtsız", sum(1 for v in sonuc.values() if not v),
          "önerisiz", sum(1 for m in ms if m["mid"] not in oneri))


ISTEM = (
    "Sen bir Osmanlı tarihi doğrulayıcısısın. Bir alternatif tarih romanı 1798-1800 İstanbul'unda (III. Selim dönemi) geçiyor. "
    "Aşağıdaki GİRDİ'de dizi ve filmlerde yapıldığı söylenen tarih hatalarına dair maddeler var ('yanlis' yanlış kullanım, 'dogru' önerilen doğrusu). "
    "Maddeleri hazırlayan model zayıftır; hiçbirine baştan güvenme. Her maddenin 'kanit' alanında TDV İslâm Ansiklopedisi'nden betikle indirilmiş "
    "ilgili parçalar ve adresleri var. Kararını bu kanıta dayandır: "
    "'onay' = kanıt 'dogru' alanındaki bilgiyi açıkça destekliyor; 'red' = kanıt bunu çürütüyor, ya da 'yanlis' diye gösterilen kullanım aslında doğru; "
    "'belirsiz' = kanıt konuyu kapsamıyor ya da yetersiz. Kendi bilgin tek başına onay için yetmez; kanıt yoksa ama bir sorun görüyorsan 'belirsiz' ver ve nota yaz. "
    "ÖNEMLİ: Gündelik dil, hitap, sokak sözü, gündelik hayat gibi ansiklopedide karşılığı olmayan konularda kanıtın konuya değinmemesi 'red' sebebi DEĞİLDİR; "
    "bu durumda 'belirsiz' ver ve 'kanit_kapsiyor' alanına 'hayır' yaz. 'red' yalnız kanıt maddeyi açıkça yalanlıyorsa verilir. "
    "Kanıt yetmiyorsa ve web sayfası açma aracın varsa güvenilir bir sayfayı (TDV, dergipark, üniversite yayını) kendin açabilirsin; açmadığın adresi yazma. "
    "kaynak_url kararının dayandığı adres olmalı (kanıttaki adreslerden ya da gerçekten açtığın sayfadan). "
    "Madde başka bir döneme aitse (ör. 16. yüzyıl için doğru ama 1798'de durum farklı) bunu gecerli_1798 ve not alanında belirt. "
    "'saman_adam' alanında: 'yanlis' alanındaki kullanım gerçekten dizi, film ya da popüler anlatıda görülen, bir yazarın düşebileceği bir hata mı ('hayır'), "
    "yoksa kimsenin yapmadığı, doğruyu anlatmak için uydurulmuş yapay bir yanlış mı ('evet')? "
    "Bütün metin Türkçe. Sonunda YALNIZCA tek bir ```json bloğu yaz, girdideki her madde için bir kayıt: "
    '[{"mid": "", "karar": "onay|red|belirsiz", "kanit_kapsiyor": "evet|hayır", "gecerli_1798": "evet|hayır|kısmen", "saman_adam": "evet|hayır", '
    '"duzeltme": "dogru alanı eksik ya da hatalıysa düzeltilmiş hali, değilse boş", '
    '"kaynak_url": "", "kaynak_ozet": "en çok 15 kelime", "not": "en çok 2 cümle"}]'
)


def isler():
    pa = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    pb = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    kan = json.load(open(os.path.join(HS, "kanit.json"), encoding="utf-8"))
    ms = maddeler()
    hafif = [dict({k: m.get(k) for k in ("mid", "yanlis", "dogru", "aciklama", "donem")}, kanit=kan.get(m["mid"], [])) for m in ms]
    for harf, parti in (("A", pa), ("B", pb)):
        out = []
        for i in range(0, len(hafif), parti):
            p = hafif[i:i + parti]
            ad = f"dog{harf}-{p[0]['mid']}"
            out.append({"ad": ad, "istem": ISTEM, "girdi": json.dumps(p, ensure_ascii=False, indent=0),
                        "cikti": f"ham-sayfalar/dogrulama/{ad}.json"})
        json.dump(out, open(os.path.join(HS, f"isler-dog{harf}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(harf, len(out))


if __name__ == "__main__":
    {"slug-isler": slug_isler, "kanit": kanit, "isler": isler}[sys.argv[1]]()
