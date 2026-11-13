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


def gecerlilik(m):
    oylar = [str((m["dogrulama"].get(h) or {}).get("gecerli_1798", "")).lower() for h in "AB"]
    oylar = [o for o in oylar if o]
    if not oylar:
        return str(m.get("gecerli_1798") or "bilinmiyor").lower()
    c = Counter(oylar).most_common()
    return c[0][0] if len(c) == 1 or c[0][1] > c[1][1] else "tartışmalı (" + " / ".join(oylar) + ")"


def durum(m, g):
    s = m["dogrulama"]["sonuc"]
    if s == "tartismali":
        return "tartışmalı (iki doğrulayıcı çelişti)"
    if s == "dogrulandi":
        if g.startswith("hayır"):
            return "başka döneme ait"
        if g.startswith("kısmen"):
            return "kesin hata (1798 için kısmen geçerli)"
        return "kesin hata"
    return {"tek-onay": "tek onay (bir doğrulayıcı kanıtla onayladı, öteki karar veremedi)", "tek-red": "şüpheli (bir doğrulayıcı kanıtla yalanladı)",
            "elendi": "elendi (iki doğrulayıcı da yalanladı)", "dogrulanamadi": "belirsiz / kaynakta karşılığı yok"}[s]


def video_mu(m):
    return any("youtu" in str(k.get("kaynak_url") or "") for k in (m.get("kaynaklar") or []))


def saman_adam(m):
    """Eleştiri kaynağı olmayan (konu taramasından gelen) ve doğrulayıcılardan en az birinin
    'kimsenin yapmadığı yapay yanlış' dediği madde."""
    if m.get("kaynaklar"):
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
    ks = m.get("kaynaklar") or []
    for k in ks[:3]:
        kim = " / ".join(x for x in (k.get("kisi"), k.get("yapim")) if x)
        sat.append(f"- Kaynak: <{k.get('kaynak_url')}> ({kim}): {k.get('kaynak_ozet') or ''}".rstrip())
    if not ks:
        sat.append("- Kaynak: konu taraması (eleştiri kaynağı yok; dayanak doğrulayıcı kaynağıdır)")
    for h in "AB":
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
    govde, ek_tart, ek_diger, ek_tek, ek_bel, say = [], [], [], [], [], Counter()
    for kod in BASLIK:
        liste = grup.get(kod, [])
        if not liste:
            continue
        # kaynak sayısı çok olan (sık eleştirilen) öne
        liste.sort(key=lambda m: (-len(m.get("kaynaklar") or []), m["mid"]))
        for m in liste:
            if saman_adam(m):
                say["saman-adam"] += 1
        S = lambda m: m["dogrulama"]["sonuc"]
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
        say["kilavuz-elestirili"] += sum(1 for m in gecerli if m.get("kaynaklar"))
        say["ek-tek-onay"] += len(tek)
        say["ek-belirsiz-karsiligi-yok"] += len(belirsiz)
        say["ek-belirsiz-elestirili"] += sum(1 for m in belirsiz if m.get("kaynaklar"))
        say["ek-tartismali-supheli"] += len(tar)
        say["ek-baska-donem"] += len(baska)
        if gecerli:
            govde.append(f"## {BASLIK[kod]}\n")
            for i, m in enumerate(gecerli, 1):
                govde.append(madde_md(i, m))
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
    metin = "\n".join(govde) \
        + "\n## Ek 1: Tek onaylı maddeler\n\nBir doğrulayıcı kanıtla onayladı, öteki karar veremedi (yalanlamadı). Büyük olasılıkla doğru; kullanmadan önce kaynağa bir göz atılmalı.\n\n" + "\n".join(ek_tek) \
        + "\n## Ek 2: Belirsiz / kaynakta karşılığı yok\n\nTDV'de karşılığı bulunamayan, ama kimsenin yalanlamadığı maddeler (çoğu gündelik dil, hitap, gündelik hayat). Eleştiri kaynağı varsa yanında. Yazar kendi muhakemesiyle kullanmalı.\n\n" + "\n".join(ek_bel) \
        + "\n## Ek 3: Tartışmalı ve şüpheli maddeler\n\nDoğrulayıcılar çelişti ya da biri kanıtla yalanladı; kullanmadan önce ayrıca bakılmalı.\n\n" + "\n".join(ek_tart) \
        + "\n## Ek 4: Başka döneme ait doğrulanmış maddeler\n\nBu düzeltmeler kendi dönemleri için doğru, ama 1798 için geçerli değil; tuzak olarak bilinmeli.\n\n" + "\n".join(ek_diger)
    open(os.path.join(KOK, "ham-sayfalar", "kilavuz-govde.md"), "w", encoding="utf-8").write(metin)
    print(dict(say))


if __name__ == "__main__":
    main()
