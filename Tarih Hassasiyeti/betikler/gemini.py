"""Gemini API istemcisi (ücretsiz katman). Anahtar kullanıcı ortam değişkeni
GEMINI_API_KEY'den okunur; değeri hiçbir yere yazılmaz.

python gemini.py modeller      -> kullanılabilir model adları
python gemini.py deneme <model>
python gemini.py isler <isler.json> [paralel=2] [model]  -> oc.py ile aynı iş biçimi (girdi metni istemin sonuna eklenir)
"""
import json, os, re, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(KOK, "ham-sayfalar", "log")
URL = "https://generativelanguage.googleapis.com/v1beta"


def _anahtar():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            k = winreg.QueryValueEx(h, "GEMINI_API_KEY")[0]
    return k.strip()


ANAHTAR = None
KILIT = threading.Lock()
SON = [0.0]
ARALIK = float(os.environ.get("GEMINI_ARALIK", "7"))  # istekler arası en az saniye (dakikada ~8-9 istek)


def istek(yol, govde=None, sure=600):
    global ANAHTAR
    if ANAHTAR is None:
        ANAHTAR = _anahtar()
    req = urllib.request.Request(URL + yol, data=json.dumps(govde).encode() if govde is not None else None,
                                 headers={"x-goog-api-key": ANAHTAR, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=sure) as r:
        return json.loads(r.read().decode("utf-8"))


def uret(metin, model="gemini-3.5-flash", araclar=True, deneme=6):
    govde = {"contents": [{"role": "user", "parts": [{"text": metin}]}],
             "generationConfig": {"temperature": 0.2}}
    if araclar and not model.startswith("gemma"):  # gemma araç desteklemiyor
        govde["tools"] = [{"url_context": {}}]
    for d in range(deneme):
        with KILIT:
            bekle = SON[0] + ARALIK - time.time()
            if bekle > 0:
                time.sleep(bekle)
            SON[0] = time.time()
        try:
            r = istek(f"/models/{model}:generateContent", govde)
            parca = r["candidates"][0]["content"].get("parts", [])
            return "".join(p.get("text", "") for p in parca), r
        except urllib.error.HTTPError as e:
            govde_tam = e.read().decode("utf-8", "replace")
            govde_hata = govde_tam[:300]
            if e.code == 429 and "PerDay" in govde_tam:
                # günlük ücretsiz kota bitti: beklemenin anlamı yok
                raise RuntimeError(f"günlük kota bitti ({model})")
            if e.code in (429, 500, 503):
                time.sleep(30 * (d + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {govde_hata}")
        except (KeyError, IndexError):
            time.sleep(10)
            continue
        except Exception as e:
            time.sleep(15)
            continue
    raise RuntimeError("deneme sınırı aşıldı")


def json_cek(metin):
    for b in reversed(re.findall(r"```json\s*(.*?)```", metin, flags=re.S)):
        try:
            return json.loads(b)
        except Exception:
            pass
    for ac, kp in (("[", "]"), ("{", "}")):
        i, j = metin.find(ac), metin.rfind(kp)
        if i != -1 and j > i:
            try:
                return json.loads(metin[i:j + 1])
            except Exception:
                pass
    return None


def is_calistir(is_, model):
    ad, cikti = is_["ad"], is_["cikti"]
    if not os.path.isabs(cikti):
        cikti = os.path.join(KOK, cikti)
    if os.path.exists(cikti):
        return ad, "atlandı"
    os.makedirs(os.path.dirname(cikti), exist_ok=True)
    os.makedirs(LOG, exist_ok=True)
    istem = is_["istem"].replace("Çalışma klasöründeki girdi.json dosyasını read aracıyla oku", "Aşağıdaki GİRDİ bölümünü oku") \
                        .replace("webfetch", "url_context").replace("websearch ile", "bildiğin kaynaklardan yola çıkıp url_context ile").replace("websearch", "url_context").replace("read aracıyla", "")
    if is_.get("girdi") is not None:
        istem += "\n\nGİRDİ:\n" + is_["girdi"]
    t0 = time.time()
    for d in range(2):
        try:
            metin, ham = uret(istem, model=model)
        except Exception as e:
            return ad, f"hata: {str(e)[:200]}"
        open(os.path.join(LOG, f"{ad}.gemini.{d}.txt"), "w", encoding="utf-8").write(metin)
        veri = json_cek(metin)
        if veri is not None:
            okunan = []
            try:
                for u in ham["candidates"][0].get("urlContextMetadata", {}).get("urlMetadata", []):
                    okunan.append({"url": u.get("retrievedUrl"), "durum": u.get("urlRetrievalStatus", "").replace("URL_RETRIEVAL_STATUS_", "")})
            except Exception:
                pass
            json.dump({"model": "gemini/" + model, "ad": ad, "tarih": time.strftime("%Y-%m-%d %H:%M"), "okunan_adresler": okunan, "veri": veri},
                      open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            return ad, f"tamam ({int(time.time()-t0)} sn)"
    return ad, "json yok"


if __name__ == "__main__":
    k = sys.argv[1]
    if k == "modeller":
        r = istek("/models?pageSize=200")
        for m in r.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(m["name"])
    elif k == "deneme":
        t, _ = uret("Tek cümle: Osmanlı'da kapıkulu ne demektir?", model=sys.argv[2], araclar=False)
        print(t[:300])
    elif k == "isler":
        isler = json.load(open(sys.argv[2], encoding="utf-8"))
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        model = sys.argv[4] if len(sys.argv) > 4 else "gemini-3.5-flash"
        with ThreadPoolExecutor(n) as ex:
            for ad, durum in ex.map(lambda x: is_calistir(x, model), isler):
                print(f"{ad}: {durum}", flush=True)
