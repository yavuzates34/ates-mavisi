"""Aşama 6: doğrulama sonucundan dogrulanmis/<konu>.md dosyalarını ve kılavuz gövdesini üretir.

python kilavuz.py  -> dogrulanmis/*.md, ham-sayfalar/kilavuz-govde.md, istatistik
"""
import json, os
from collections import Counter, defaultdict
from isler_uret import KONULAR

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASLIK = {
    "unvan-hitap": "Unvan ve hitaplar", "saray-devlet": "Saray ve devlet teşkilatı", "ordu": "Ordu ve asker",
    "giyim": "Giyim, sarık ve kavuk", "gundelik-dil": "Gündelik dil", "harem-kadin": "Harem ve kadınlar",
    "para-olcu-takvim": "Para, ölçü, takvim ve saat", "din-gundelik": "Din ve gündelik hayat",
    "yemek-kahve-tutun": "Yemek, kahve ve tütün", "sehir-mekan": "Şehir ve mekân adları",
    "teknoloji-esya": "Teknoloji ve eşya", "yazi-belge": "Yazışma ve resmî belgeler",
    "isim-ad": "Kişi adları", "diplomasi-donem": "1798–1800 siyaseti ve diplomasi", "diger": "Diğer",
}
KISA = lambda s: (s or "").replace("opencode/", "")

# ham maddelerin kökeni: kaynak-* (web eleştirisi), video-* (video), konu-* (konu taraması; eleştiri değil)
HAM = {}
for _y in __import__("glob").glob(os.path.join(KOK, "ham-sayfalar", "toplu", "*.json")):
    for _m in json.load(open(_y, encoding="utf-8")):
        HAM[_m["id"]] = _m


def kaynaklar(m):
    """Maddeyi oluşturan ham maddelerin kaynakları, kökeniyle (eleştiri önce, konu taraması sonra)."""
    out, gor = [], set()
    for i in m.get("birlesen", []):
        x = HAM.get(i)
        if not x or not x.get("kaynak_url") or x["kaynak_url"] in gor:
            continue
        gor.add(x["kaynak_url"])
        hd = x.get("ham_dosya", "")
        tur = "video" if hd.startswith("video-") else ("eleştiri" if hd.startswith("kaynak-") else "konu")
        out.append(dict(x, tur=tur))
    return sorted(out, key=lambda k: {"eleştiri": 0, "video": 1, "konu": 2}[k["tur"]])


def elestirili(m):
    return any(k["tur"] != "konu" for k in kaynaklar(m))


def gecerlilik(m):
    oylar = [str((m["dogrulama"].get(h) or {}).get("gecerli_1798", "")).lower() for h in "AB"]
    oylar = [o for o in oylar if o]
    if not oylar:
        return str(m.get("gecerli_1798") or "bilinmiyor").lower()
    c = Counter(oylar).most_common()
    return c[0][0] if len(c) == 1 or c[0][1] > c[1][1] else "tartışmalı (" + " / ".join(oylar) + ")"


_dy = os.path.join(KOK, "orkestrator-denetim.json")
DENETIM = {k: v for k, v in json.load(open(_dy, encoding="utf-8")).items() if not k.startswith("_")} if os.path.exists(_dy) else {}


def nihai(m):
    """A/B sonucunu, örneklemde çalışan üçüncü doğrulayıcı C (Google dışı) ile günceller.
    A+B onayına C kanıtla red derse madde tartışmalıya iner; tek onaya C de onay verirse
    iki bağımsız onay olur (doğrulandı); tek redde C de red derse elenir."""
    d = m["dogrulama"]
    if m["mid"] in DENETIM:
        return DENETIM[m["mid"]]["sonuc"]
    s = d["sonuc"]
    c = (d.get("C") or {}).get("karar")
    if s == "dogrulandi" and c == "red":
        return "tartismali"
    if s == "tek-onay" and c == "onay":
        return "dogrulandi"
    if s == "tek-red" and c == "red":
        return "elendi"
    return s


def durum(m, g):
    s = nihai(m)
    c = (m["dogrulama"].get("C") or {}).get("karar")
    if m["mid"] in DENETIM:
        return "tartışmalı — " + DENETIM[m["mid"]]["not"]
    if s == "tartismali":
        return "tartışmalı (doğrulayıcılar çelişti" + ("; A ve B onayladı, C kanıtla yalanladı)" if m["dogrulama"]["sonuc"] == "dogrulandi" else ")")
    if s == "dogrulandi" and m["dogrulama"]["sonuc"] == "tek-onay":
        return "kesin hata (iki onay: biri A/B, biri üçüncü doğrulayıcı C)" + (" — 1798 için kısmen geçerli" if g.startswith("kısmen") else "")
    if s == "dogrulandi" and c == "onay":
        return "kesin hata (üç doğrulayıcı da onayladı)" + (" — 1798 için kısmen geçerli" if g.startswith("kısmen") else "")
    if s == "dogrulandi":
        if g.startswith("hayır"):
            return "başka döneme ait"
        if g.startswith("kısmen"):
            return "kesin hata (1798 için kısmen geçerli)"
        return "kesin hata"
    return {"tek-onay": "tek onay (bir doğrulayıcı kanıtla onayladı, öteki karar veremedi)", "tek-red": "şüpheli (bir doğrulayıcı kanıtla yalanladı)",
            "elendi": "elendi (iki doğrulayıcı da yalanladı)", "dogrulanamadi": "belirsiz / kaynakta karşılığı yok"}[s]


def video_mu(m):
    return any(k["tur"] == "video" for k in kaynaklar(m))


def saman_adam(m):
    """Eleştiri kaynağı olmayan (konu taramasından gelen) ve doğrulayıcılardan en az birinin
    'kimsenin yapmadığı yapay yanlış' dediği madde."""
    if elestirili(m):
        return False
    oy = [str((m["dogrulama"].get(h) or {}).get("saman_adam", "")).lower() for h in "AB"]
    return "evet" in oy


def madde_md(n, m, ic=False):
    g = gecerlilik(m)
    d = m["dogrulama"]
    duz = [x.get("duzeltme") for x in (d.get("A"), d.get("B")) if x and x.get("duzeltme")]
    sat = [f"### {n}. {m['yanlis'].strip()}", ""]
    sat.append(f"- Yanlış: {m['yanlis'].strip()}")
    sat.append(f"- Doğrusu: {m['dogru'].strip()}")
    if duz:
        sat.append(f"- Doğrulayıcı düzeltmesi: {duz[0].strip()}")
    if m.get("aciklama"):
        sat.append(f"- Açıklama: {m['aciklama'].strip()}")
    sat.append(f"- Dönem: {m.get('donem') or 'belirtilmedi'}; 1798 için geçerli mi: {g}")
    sat.append(f"- Durum: {durum(m, g)}")
    ks = kaynaklar(m)
    for k in [k for k in ks if k["tur"] != "konu"][:3]:
        kim = " / ".join(x for x in (k.get("kisi"), k.get("yapim")) if x)
        zaman = f", {k['zaman']}" if k.get("zaman") else ""
        sat.append(f"- Kaynak ({k['tur']}{zaman}): <{k.get('kaynak_url')}> ({kim}): {k.get('kaynak_ozet') or ''}".rstrip())
    if not elestirili(m):
        sat.append("- Kaynak: konu taraması (bir tarihçinin ya da yapımın eleştirisine dayanmıyor; dayanak doğrulayıcının okuduğu TDV kanıtıdır)")
    for h in "ABC":  # C: örneklemde üçüncü, Google dışı doğrulayıcı (ucuncu.py)
        x = d.get(h)
        if x:
            sat.append(f"- Doğrulayan {KISA(x.get('model'))}: {x.get('karar')}; <{x.get('kaynak_url') or 'adres yok'}>: {x.get('kaynak_ozet') or ''}" + (f" Not: {x['not']}" if x.get("not") else ""))
    if ic:
        sat.append(f"- İz: {m['mid']} (ham: {', '.join(m.get('birlesen', []))})")
    return "\n".join(sat) + "\n"


def main():
    ms = json.load(open(os.path.join(KOK, "ham-sayfalar", "dogrulama-sonuc.json"), encoding="utf-8"))
    grup = defaultdict(list)
    for m in ms:
        grup[m.get("konu") if m.get("konu") in BASLIK else "diger"].append(m)
    os.makedirs(os.path.join(KOK, "dogrulanmis"), exist_ok=True)
    govde, govde_k, ek_tart, ek_diger, ek_tek, ek_bel, say = [], [], [], [], [], [], Counter()
    for kod in BASLIK:
        liste = grup.get(kod, [])
        if not liste:
            continue
        # kaynak sayısı çok olan (sık eleştirilen) öne
        liste.sort(key=lambda m: (not elestirili(m), -sum(1 for k in kaynaklar(m) if k["tur"] != "konu"), m["mid"]))
        for m in liste:
            if saman_adam(m):
                say["saman-adam"] += 1
        S = nihai
        hayir = lambda m: gecerlilik(m).startswith("hayır")
        temiz = [m for m in liste if not saman_adam(m)]
        dog = [m for m in temiz if S(m) == "dogrulandi"]
        tar = [m for m in temiz if S(m) in ("tartismali", "tek-red")]
        dosya = [f"# {BASLIK[kod]} – doğrulama sonuçları", "",
                 f"Doğrulanan: {len(dog)}, tartışmalı/şüpheli: {len(tar)}, toplam aday: {len(liste)}.", ""]
        for i, m in enumerate(liste, 1):
            dosya.append(madde_md(i, m, ic=True))
            say[S(m)] += 1
        open(os.path.join(KOK, "dogrulanmis", f"{kod}.md"), "w", encoding="utf-8").write("\n".join(dosya))
        gecerli = [m for m in dog if not hayir(m)]
        baska = [m for m in dog if hayir(m)]
        tek = [m for m in temiz if S(m) == "tek-onay" and not hayir(m)]
        # Yavuz'un kuralı (13 Kasım): TDV'de karşılığı olmayan maddeler elenmez, ayrı kümede durur
        belirsiz = [m for m in temiz if S(m) == "dogrulanamadi" and not hayir(m)]
        say["kilavuz"] += len(gecerli)
        say["kilavuz-video"] += sum(1 for m in gecerli if video_mu(m))
        say["kilavuz-elestirili"] += sum(1 for m in gecerli if elestirili(m))
        say["ek-tek-onay"] += len(tek)
        say["ek-belirsiz-karsiligi-yok"] += len(belirsiz)
        say["ek-belirsiz-elestirili"] += sum(1 for m in belirsiz if elestirili(m))
        say["ek-tartismali-supheli"] += len(tar)
        say["ek-baska-donem"] += len(baska)
        say["c-baktigi-kilavuz"] += sum(1 for m in gecerli if m["dogrulama"].get("C"))
        say["c-ile-yukselen"] += sum(1 for m in gecerli if m["dogrulama"]["sonuc"] == "tek-onay")
        for hedef, lst in ((govde, [m for m in gecerli if elestirili(m)]), (govde_k, [m for m in gecerli if not elestirili(m)])):
            if lst:
                hedef.append(f"### {BASLIK[kod]}\n")
                for i, m in enumerate(lst, 1):
                    hedef.append(madde_md(i, m).replace("### ", "#### ", 1))
        for hedef, lst in ((ek_tek, tek), (ek_bel, belirsiz), (ek_tart, tar)):
            if lst:
                hedef.append(f"### {BASLIK[kod]}\n")
                for i, m in enumerate(lst, 1):
                    hedef.append(madde_md(i, m).replace("### ", "#### ", 1))
        if baska:
            ek_diger.append(f"### {BASLIK[kod]}\n")
            for m in baska:
                ek_diger.append(f"- {m['yanlis'].strip()} → {m['dogru'].strip()} (dönem: {m.get('donem') or '?'})")
            ek_diger.append("")
    metin = "## Bölüm I: Tarihçi ve yapım eleştirisine dayanan doğrulanmış maddeler\n\nBir tarihçinin, eleştirmenin ya da videonun gerçekten şikâyet ettiği ve doğrulayıcıların TDV kanıtıyla onayladığı hatalar.\n\n" + "\n".join(govde) \
        + "\n## Bölüm II: Konu taramasından gelen doğrulanmış uyarılar\n\nBir eleştiriye değil, 1798 için konu konu yapılan taramaya dayanan; doğrulayıcıların TDV kanıtıyla onayladığı maddeler. Saman adam (kimsenin yapmadığı yapay yanlış) işaretlenenler çıkarıldı.\n\n" + "\n".join(govde_k) \
        + "\n## Ek 1: Tek onaylı maddeler\n\nBir doğrulayıcı kanıtla onayladı, öteki karar veremedi (yalanlamadı). Büyük olasılıkla doğru; kullanmadan önce kaynağa bir göz atılmalı.\n\n" + "\n".join(ek_tek) \
        + "\n## Ek 2: Belirsiz / kaynakta karşılığı yok\n\nTDV'de karşılığı bulunamayan, ama kimsenin yalanlamadığı maddeler (çoğu gündelik dil, hitap, gündelik hayat). Eleştiri kaynağı varsa yanında. Yazar kendi muhakemesiyle kullanmalı.\n\n" + "\n".join(ek_bel) \
        + "\n## Ek 3: Tartışmalı ve şüpheli maddeler\n\nDoğrulayıcılar çelişti ya da biri kanıtla yalanladı; kullanmadan önce ayrıca bakılmalı.\n\n" + "\n".join(ek_tart) \
        + "\n## Ek 4: Başka döneme ait doğrulanmış maddeler\n\nBu düzeltmeler kendi dönemleri için doğru, ama 1798 için geçerli değil; tuzak olarak bilinmeli.\n\n" + "\n".join(ek_diger)
    open(os.path.join(KOK, "ham-sayfalar", "kilavuz-govde.md"), "w", encoding="utf-8").write(metin)
    print(dict(say))


if __name__ == "__main__":
    main()
