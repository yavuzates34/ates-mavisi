"""Aşama 3: ham/*.json maddelerini konu başına toplar, kimlik verir ve
tekilleştirme işleri üretir.

python birlestir.py topla      -> ham-sayfalar/toplu/<konu>.json + kaynaklar/kaynak-listesi.md
python birlestir.py isler      -> tekilleştirme iş listesi (stdout)
"""
import glob, json, os, sys, re
from isler_uret import KONULAR

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPLU = os.path.join(KOK, "ham-sayfalar", "toplu")


def konu_bul(m):
    k = (m.get("konu") or "").strip().lower()
    for kod in KONULAR:
        if kod in k:
            return kod
    return "diger"


def topla():
    os.makedirs(TOPLU, exist_ok=True)
    gruplar, kaynaklar = {}, {}
    for yol in sorted(glob.glob(os.path.join(KOK, "ham", "*.json"))):
        d = json.load(open(yol, encoding="utf-8"))
        veri = d["veri"] if isinstance(d["veri"], dict) else {"maddeler": d["veri"]}
        dosya = os.path.basename(yol)
        for k in veri.get("kaynaklar", []) or []:
            u = (k.get("url") or "").strip()
            if u and u not in kaynaklar:
                kaynaklar[u] = dict(k, bulan=dosya)
        for m in veri.get("maddeler", []) or []:
            if not isinstance(m, dict) or not m.get("yanlis"):
                continue
            m["ham_dosya"] = dosya
            m["cikaran_model"] = d.get("model")
            gruplar.setdefault(konu_bul(m), []).append(m)
    for kod, ms in gruplar.items():
        for i, m in enumerate(ms):
            m["id"] = f"{kod}-h{i+1:03d}"
        json.dump(ms, open(os.path.join(TOPLU, f"{kod}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(kod, len(ms))
    # kaynak listesi
    satir = ["# Kaynak listesi", "",
             "Ücretsiz ajanların (OpenCode, deepseek-v4.1-flash-free) web aramasıyla bulup okuduğunu bildirdiği sayfalar. "
             "Adresler ajan çıktısından aktarıldı; tek tek açılıp denetlenmedi, kılavuzdaki maddelerin kaynağı ayrıca doğrulama aşamasında denetlendi.", ""]
    for u, k in sorted(kaynaklar.items(), key=lambda x: (x[1].get("kisi") or "", x[0])):
        satir.append(f"- {k.get('kisi','?')} | {k.get('yapim','?')} | {k.get('tarih','?')} | {k.get('tur','?')} | {k.get('baslik','').strip()} | <{u}> | bulan: {k['bulan']}")
    open(os.path.join(KOK, "kaynaklar", "kaynak-listesi.md"), "w", encoding="utf-8").write("\n".join(satir) + "\n")
    print("kaynak", len(kaynaklar), "madde", sum(len(v) for v in gruplar.values()))


def isler():
    out = []
    for yol in sorted(glob.glob(os.path.join(TOPLU, "*.json"))):
        kod = os.path.basename(yol)[:-5]
        ms = json.load(open(yol, encoding="utf-8"))
        hafif = [{k: m.get(k) for k in ("id", "yanlis", "dogru", "donem", "gecerli_1798")} for m in ms]
        istem = (
            f"Çalışma klasöründeki girdi.json dosyasını read aracıyla oku (gerekirse parça parça). İçinde '{kod}' konusunda, Osmanlı dizi/filmlerindeki tarih hatalarına dair ham maddeler var. "
            "Görevin yalnız tekilleştirme: aynı hatayı anlatan maddeleri grupla. Yeni madde ekleme, içerik değiştirme, web'e çıkma. "
            "Her grup için en açık ve eksiksiz maddeyi 'ana' seç. Tek kalan maddeler de kendi grubunu oluşturur. "
            "Ayrıca konusu yanlış atanmış maddeleri 'konu' alanında doğru koda yönlendir; kodlar: " + ", ".join(KONULAR) + ". "
            "Çıktı: YALNIZCA tek bir ```json bloğu, biçimi: "
            '{"gruplar": [{"ana": "id", "digerleri": ["id", ...], "konu": "kod"}]}. Her id tam olarak bir grupta geçmeli.'
        )
        out.append({"ad": f"tekil-{kod}", "model": "opencode/deepseek-v4.1-flash-free", "istem": istem,
                    "cikti": f"ham-sayfalar/tekil/{kod}.json", "sure": 900,
                    "girdi": json.dumps(hafif, ensure_ascii=False, indent=0)})
    print(json.dumps(out, ensure_ascii=False, indent=1))


def uygula():
    """Tekilleştirme gruplarını uygular -> ham-sayfalar/birlesik.json"""
    sonuc = []
    for yol in sorted(glob.glob(os.path.join(TOPLU, "*.json"))):
        kod = os.path.basename(yol)[:-5]
        ms = {m["id"]: m for m in json.load(open(yol, encoding="utf-8"))}
        tyol = os.path.join(KOK, "ham-sayfalar", "tekil", f"{kod}.json")
        gruplar = []
        if os.path.exists(tyol):
            v = json.load(open(tyol, encoding="utf-8"))["veri"]
            gruplar = v.get("gruplar", []) if isinstance(v, dict) else []
        kullanilan = set()
        for g in gruplar:
            ana = g.get("ana")
            if ana not in ms or ana in kullanilan:
                continue
            uyeler = [ana] + [x for x in g.get("digerleri", []) if x in ms and x not in kullanilan and x != ana]
            kullanilan.update(uyeler)
            m = dict(ms[ana])
            m["konu"] = g.get("konu") if g.get("konu") in KONULAR else kod
            m["kaynaklar"] = []
            for u in uyeler:
                x = ms[u]
                if x.get("kaynak_url"):
                    m["kaynaklar"].append({k: x.get(k) for k in ("kaynak_url", "kaynak_ozet", "kisi", "yapim", "donem")})
            m["birlesen"] = uyeler
            sonuc.append(m)
        for i, m in ms.items():  # gruplanmamış kalanlar
            if i not in kullanilan:
                m = dict(m)
                m["kaynaklar"] = [{k: m.get(k) for k in ("kaynak_url", "kaynak_ozet", "kisi", "yapim", "donem")}] if m.get("kaynak_url") else []
                m["birlesen"] = [i]
                sonuc.append(m)
    for i, m in enumerate(sonuc):
        m["mid"] = f"M{i+1:04d}"
    json.dump(sonuc, open(os.path.join(KOK, "ham-sayfalar", "birlesik.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(sonuc), Counter(m["konu"] for m in sonuc).most_common(), Counter(str(m.get("gecerli_1798")).lower()[:5] for m in sonuc))


if __name__ == "__main__":
    {"topla": topla, "isler": isler, "uygula": uygula}[sys.argv[1]]()
