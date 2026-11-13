"""Üçüncü, Google dışı doğrulayıcı (OpenRouter ücretsiz katmanı, günde ~50 istek).
Anahtar kullanıcı ortam değişkeni OPENROUTER_API_KEY'den okunur; değeri hiçbir yere yazılmaz.
A ve B ile aynı TDV kanıtını ve aynı istemi kullanır; yalnız bir örneklemde çalışır:
A/B'nin ikisinin de onayladığı (kılavuza girecek) maddelerden bir pay ile A/B'nin ayrıştığı maddeler.

python ucuncu.py isler [parti=12] [en_cok_istek=40]   -> ham-sayfalar/isler-dogC.json
python ucuncu.py calistir [model]                     -> ham-sayfalar/dogrulama-C/*.json
python ucuncu.py sonuc                                -> karşılaştırma özeti (ham-sayfalar/dogrulama-C-ozet.json)
"""
import json, os, random, sys, time, urllib.request, urllib.error
from collections import Counter
from gemini import json_cek
import dogrula2

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HS = os.path.join(KOK, "ham-sayfalar")
MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


def _anahtar():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            k = winreg.QueryValueEx(h, "OPENROUTER_API_KEY")[0]
    return k.strip()


def sor(metin, model):
    govde = {"model": model, "messages": [{"role": "user", "content": metin}], "temperature": 0.2}
    for d in range(4):
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(govde).encode(),
                                     headers={"Authorization": "Bearer " + _anahtar(), "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                j = json.loads(r.read().decode("utf-8"))
            return j["choices"][0]["message"].get("content") or ""
        except urllib.error.HTTPError as e:
            g = e.read().decode("utf-8", "replace")[:200]
            if e.code == 429 and "per-day" in g.lower():
                raise RuntimeError("günlük kota bitti")
            if e.code in (429, 500, 502, 503):
                time.sleep(40 * (d + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {g}")
        except Exception:
            time.sleep(20)
    raise RuntimeError("deneme sınırı aşıldı")


def isler():
    parti = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    sinir = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    ms = json.load(open(os.path.join(HS, "dogrulama-sonuc.json"), encoding="utf-8"))
    kan = json.load(open(os.path.join(HS, "kanit.json"), encoding="utf-8"))
    ayris = [m for m in ms if m["dogrulama"]["sonuc"] in ("tartismali", "tek-red", "tek-onay")]
    onay = [m for m in ms if m["dogrulama"]["sonuc"] == "dogrulandi"]
    random.seed(1798)
    # önce ayrışanlar (kanıtı olanlar), sonra onaylılardan rastgele pay
    ayris = [m for m in ayris if kan.get(m["mid"])]
    kapasite = parti * sinir
    secim = ayris[: kapasite // 2]
    secim += random.sample(onay, min(len(onay), kapasite - len(secim)))
    out = []
    for i in range(0, len(secim), parti):
        p = [dict({k: m.get(k) for k in ("mid", "yanlis", "dogru", "aciklama", "donem")}, kanit=kan.get(m["mid"], [])) for m in secim[i:i + parti]]
        out.append({"ad": f"dogC-{p[0]['mid']}", "girdi": json.dumps(p, ensure_ascii=False, indent=0)})
    json.dump(out, open(os.path.join(HS, "isler-dogC.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("iş", len(out), "madde", len(secim), "ayrışan", min(len(ayris), kapasite // 2), "onaylı", len(secim) - min(len(ayris), kapasite // 2))


def calistir():
    model = sys.argv[2] if len(sys.argv) > 2 else MODEL
    os.makedirs(os.path.join(HS, "dogrulama-C"), exist_ok=True)
    istem = dogrula2.ISTEM.replace("Kanıt yetmiyorsa ve web sayfası açma aracın varsa güvenilir bir sayfayı (TDV, dergipark, üniversite yayını) kendin açabilirsin; açmadığın adresi yazma. ", "Web aracın yok; yalnız verilen kanıtı kullan, başka adres yazma. ")
    for is_ in json.load(open(os.path.join(HS, "isler-dogC.json"), encoding="utf-8")):
        yol = os.path.join(HS, "dogrulama-C", is_["ad"] + ".json")
        if os.path.exists(yol):
            continue
        t0 = time.time()
        try:
            metin = sor(istem + "\n\nGİRDİ:\n" + is_["girdi"], model)
        except Exception as e:
            print(is_["ad"], "hata:", str(e)[:120], flush=True)
            if "günlük" in str(e):
                break
            continue
        open(os.path.join(HS, "log", is_["ad"] + ".or.txt"), "w", encoding="utf-8").write(metin)
        v = json_cek(metin)
        if v is None:
            print(is_["ad"], "json yok", flush=True)
            continue
        json.dump({"model": "openrouter/" + model, "ad": is_["ad"], "tarih": time.strftime("%Y-%m-%d %H:%M"), "veri": v},
                  open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(is_["ad"], f"tamam ({int(time.time()-t0)} sn)", flush=True)
        time.sleep(8)


def sonuc():
    ms = {m["mid"]: m for m in json.load(open(os.path.join(HS, "dogrulama-sonuc.json"), encoding="utf-8"))}
    kan = json.load(open(os.path.join(HS, "kanit.json"), encoding="utf-8"))
    norm = lambda u: (u or "").strip().lower().rstrip("/").replace("http://", "https://").replace("://www.", "://")
    say, ornek = Counter(), []
    for yol in os.listdir(os.path.join(HS, "dogrulama-C")):
        d = json.load(open(os.path.join(HS, "dogrulama-C", yol), encoding="utf-8"))
        v = d["veri"] if isinstance(d["veri"], list) else next((x for x in d["veri"].values() if isinstance(x, list)), [])
        for k in v:
            if not isinstance(k, dict) or k.get("mid") not in ms:
                continue
            m = ms[k["mid"]]
            kc = k.get("karar")
            if kc == "onay" and norm(k.get("kaynak_url")) not in {norm(e["url"]) for e in kan.get(k["mid"], [])}:
                kc = "belirsiz"
            s = m["dogrulama"]["sonuc"]
            say[(s, kc)] += 1
            if s == "dogrulandi" and kc == "red":
                ornek.append({"mid": k["mid"], "yanlis": m["yanlis"], "not": k.get("not")})
            m["dogrulama"]["C"] = dict(k, model=d["model"], karar=kc)
    json.dump(list(ms.values()), open(os.path.join(HS, "dogrulama-sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    oz = {"sayim": {f"{a} / C:{b}": n for (a, b), n in sorted(say.items())}, "onayliya_C_red": ornek}
    json.dump(oz, open(os.path.join(HS, "dogrulama-C-ozet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(oz["sayim"], ensure_ascii=False), "onaylıya red:", len(ornek))


if __name__ == "__main__":
    {"isler": isler, "calistir": calistir, "sonuc": sonuc}[sys.argv[1]]()
