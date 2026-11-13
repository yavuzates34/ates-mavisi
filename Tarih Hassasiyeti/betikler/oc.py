"""OpenCode ücretsiz modelleriyle paralel iş çalıştırıcı.

Kullanım: python oc.py isler.json [paralel=6]
isler.json: [{"ad": "...", "model": "opencode/...-free", "istem": "...", "cikti": "yol.json"}]
Her iş kendi boş klasöründe (ham-sayfalar/is/<ad>) çalışır; stdout ham olarak
ham-sayfalar/log/<ad>.txt'ye, son ```json bloğu cikti yoluna yazılır.
Çıktısı zaten olan iş atlanır (kaldığı yerden devam).
"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IS = os.path.join(KOK, "ham-sayfalar", "is")
LOG = os.path.join(KOK, "ham-sayfalar", "log")
OPENCODE = os.path.join(os.environ["APPDATA"], "npm", "node_modules", "@opencode", "cli", "bin", "opencode.exe")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def json_cek(metin):
    bloklar = re.findall(r"```json\s*(.*?)```", metin, flags=re.S)
    for b in reversed(bloklar):
        try:
            return json.loads(b)
        except Exception:
            continue
    # yedek: en dıştaki [ ... ] ya da { ... }
    for ac, kp in (("[", "]"), ("{", "}")):
        i, j = metin.find(ac), metin.rfind(kp)
        if i != -1 and j > i:
            try:
                return json.loads(metin[i:j + 1])
            except Exception:
                pass
    return None


import threading
TUKENEN = set()          # kotası dolan modeller (bu çalıştırma boyunca)
KILIT = threading.Lock()
HAVUZ = {
    # çıkarım: deepseek tükenirse sırayla bunlar denenir
    "opencode/deepseek-v4.1-flash-free": ["opencode/deepseek-v4.1-flash-free", "opencode/longcat-2.5-free", "opencode/iceman-free",
                                          "opencode/beam-free", "opencode/minimax-m3.1-flash-free", "opencode/inkling-2-small-free"],
    # doğrulayıcı A ve B havuzları birbirinden ayrık tutulur
    "opencode/glm-5.3-flash-free": ["opencode/glm-5.3-flash-free", "opencode/longcat-2.5-free", "opencode/nemotron-3.5-super-vl-free"],
    # B doğrulayıcı (A artık Gemini): OpenCode ücretsiz modellerinden hangisi açıksa
    "opencode/mimo-v2.6-flash-free": ["opencode/mimo-v2.6-flash-free", "opencode/longcat-2.5-free", "opencode/beam-free",
                                      "opencode/glm-5.3-flash-free", "opencode/iceman-free", "opencode/minimax-m3.1-flash-free",
                                      "opencode/deepseek-v4.1-flash-free", "opencode/nemotron-3.5-super-vl-free"],
}


def calistir(is_):
    ad, model, istem, cikti = is_["ad"], is_["model"], is_["istem"], is_["cikti"]
    if not os.path.isabs(cikti):
        cikti = os.path.join(KOK, cikti)
    if os.path.exists(cikti):
        return ad, "atlandı"
    kl = os.path.join(IS, ad)
    os.makedirs(kl, exist_ok=True)
    os.makedirs(LOG, exist_ok=True)
    os.makedirs(os.path.dirname(cikti), exist_ok=True)
    if is_.get("girdi") is not None:
        with open(os.path.join(kl, "girdi.json"), "w", encoding="utf-8") as f:
            f.write(is_["girdi"])
    son = "hata"
    havuz = HAVUZ.get(model, [model])
    deneme = 0
    while deneme < int(is_.get("deneme", 2)):
        with KILIT:
            uygun = [m for m in havuz if m not in TUKENEN]
        if not uygun:
            return ad, "kota bitti (havuzdaki tüm modeller)"
        model = uygun[0]
        t0 = time.time()
        try:
            p = subprocess.run(
                [OPENCODE, "run", "--auto", "-m", model, istem],
                cwd=kl, capture_output=True, stdin=subprocess.DEVNULL, timeout=int(is_.get("sure", 1200)),
                encoding="utf-8", errors="replace", shell=False,
            )
            out = ANSI.sub("", (p.stdout or "") + "\n" + (p.stderr or ""))
        except subprocess.TimeoutExpired as e:
            out = "ZAMAN AŞIMI\n" + ANSI.sub("", (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
        with open(os.path.join(LOG, f"{ad}.{deneme}.txt"), "w", encoding="utf-8") as f:
            f.write(out)
        if "Free usage limit reached" in out:
            with KILIT:
                TUKENEN.add(model)
            continue
        deneme += 1
        veri = json_cek(out)
        if veri is not None:
            with open(cikti, "w", encoding="utf-8") as f:
                json.dump({"model": model, "ad": ad, "tarih": time.strftime("%Y-%m-%d %H:%M"), "veri": veri}, f, ensure_ascii=False, indent=1)
            return ad, f"tamam ({int(time.time()-t0)} sn)"
        son = f"json yok ({int(time.time()-t0)} sn)"
    return ad, son


def main():
    isler = json.load(open(sys.argv[1], encoding="utf-8"))
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    with ThreadPoolExecutor(n) as ex:
        for ad, durum in ex.map(calistir, isler):
            print(f"{ad}: {durum}", flush=True)


if __name__ == "__main__":
    main()
