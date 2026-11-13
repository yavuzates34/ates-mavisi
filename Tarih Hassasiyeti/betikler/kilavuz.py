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
    return {"tek-onay": "doğrulaması eksik (tek onay)", "tek-red": "şüpheli (bir red)", "elendi": "elendi", "dogrulanamadi": "doğrulanamadı"}[s]


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
    govde, ek_tart, ek_diger, say = [], [], [], Counter()
    for kod in BASLIK:
        liste = grup.get(kod, [])
        if not liste:
            continue
        # kaynak sayısı çok olan (sık eleştirilen) öne
        liste.sort(key=lambda m: (-len(m.get("kaynaklar") or []), m["mid"]))
        dog = [m for m in liste if m["dogrulama"]["sonuc"] == "dogrulandi"]
        tar = [m for m in liste if m["dogrulama"]["sonuc"] == "tartismali"]
        dosya = [f"# {BASLIK[kod]} – doğrulama sonuçları", "",
                 f"Doğrulanan: {len(dog)}, tartışmalı: {len(tar)}, toplam aday: {len(liste)}.", ""]
        for i, m in enumerate(liste, 1):
            dosya.append(madde_md(i, m, ic=True))
            say[m["dogrulama"]["sonuc"]] += 1
        open(os.path.join(KOK, "dogrulanmis", f"{kod}.md"), "w", encoding="utf-8").write("\n".join(dosya))
        gecerli = [m for m in dog if not gecerlilik(m).startswith("hayır")]
        baska = [m for m in dog if gecerlilik(m).startswith("hayır")]
        if gecerli:
            govde.append(f"## {BASLIK[kod]}\n")
            for i, m in enumerate(gecerli, 1):
                govde.append(madde_md(i, m))
        if tar:
            ek_tart.append(f"### {BASLIK[kod]}\n")
            for i, m in enumerate(tar, 1):
                ek_tart.append(madde_md(i, m).replace("### ", "#### ", 1))
        if baska:
            ek_diger.append(f"### {BASLIK[kod]}\n")
            for i, m in enumerate(baska, 1):
                ek_diger.append(madde_md(i, m).replace("### ", "#### ", 1))
    metin = "\n".join(govde) + "\n## Ek 1: Tartışmalı maddeler\n\nİki doğrulayıcı model çelişti; kullanmadan önce ayrıca bakılmalı.\n\n" + "\n".join(ek_tart) \
        + "\n## Ek 2: Başka döneme ait doğrulanmış maddeler\n\nBu düzeltmeler kendi dönemleri için doğru, ama 1798 için geçerli değil; tuzak olarak bilinmeli.\n\n" + "\n".join(ek_diger)
    open(os.path.join(KOK, "ham-sayfalar", "kilavuz-govde.md"), "w", encoding="utf-8").write(metin)
    print(dict(say))


if __name__ == "__main__":
    main()
