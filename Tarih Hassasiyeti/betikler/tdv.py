"""TDV İslâm Ansiklopedisi'nden madde metni getirir (önbellekli) ve bir iddiaya
en ilgili paragrafları seçer. Kaynağı orkestratörün kendi betiği okuduğu için
"kaynak gerçekten okundu mu" sorusu burada kanıtla çözülür: kanıt metni dosyada durur.

python tdv.py getir <slug>         -> başlık ve ilk 500 karakter
python tdv.py ara <sorgu>          -> arama sonucundaki madde adresleri
"""
import html, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request, urllib.error

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONBELLEK = os.path.join(KOK, "ham-sayfalar", "tdv")
TEMEL = "https://islamansiklopedisi.org.tr"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
GEZINTI = {"dosyalar", "duyurular", "gecen-ayin-ilk-20-si", "iletisim-formu", "sergi-arsivi", "arama", "hakkimizda",
           "yayin-ilkeleri", "kisaltmalar", "yazarlar", "ek-cilt", "sss", "kvkk", "en-cok-okunanlar"}


def _indir(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "tr-TR,tr;q=0.9", "Accept": "text/html"})
    for d in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (d + 1))
        except Exception:
            time.sleep(3 * (d + 1))
    return None


def slug_temizle(s):
    s = (s or "").strip().lower()
    s = s.replace(TEMEL.lower(), "").strip("/ ")
    s = s.replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ç", "c").replace("ö", "o").replace("ü", "u").replace("â", "a").replace("î", "i").replace("û", "u")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9-]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def getir(slug):
    """{'url','baslik','metin'} ya da None (madde yok)."""
    slug = slug_temizle(slug)
    if not slug or slug in GEZINTI:
        return None
    os.makedirs(ONBELLEK, exist_ok=True)
    yol = os.path.join(ONBELLEK, slug + ".json")
    if os.path.exists(yol):
        d = json.load(open(yol, encoding="utf-8"))
        return d or None
    h = _indir(f"{TEMEL}/{slug}")
    sonuc = {}
    if h and 'class="m-body"' in h:
        bas = h.find('class="m-body"')
        son = h.find('class="article-parts"', h.find('class="article-ps"', bas) if 'class="article-ps"' in h[bas:] else bas + 1)
        govde = h[bas: son if son > bas else len(h)]
        pler = [html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in re.findall(r"<p[^>]*>(.*?)</p>", govde, flags=re.S)]
        pler = [re.sub(r"\s+", " ", p) for p in pler if len(p) > 40 and "Değişiklikleriniz taslak" not in p]
        if sum(len(p) for p in pler) < 300:  # gövdesi olmayan yönlendirme/boş madde (ör. cariye, asker)
            pler = []
        t = re.search(r'<meta property="og:title" content="([^"]+)"', h)
        if pler:
            sonuc = {"url": f"{TEMEL}/{slug}", "baslik": html.unescape(t.group(1)).replace(" - TDV İslâm Ansiklopedisi", "") if t else slug,
                     "metin": pler, "tarih": time.strftime("%Y-%m-%d %H:%M")}
    json.dump(sonuc, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
    return sonuc or None


def ara(sorgu, en_cok=3):
    h = _indir(f"{TEMEL}/arama/?q=" + urllib.parse.quote(sorgu))
    if not h:
        return []
    out = []
    for s in re.findall(r'href="/([a-z0-9-]+)"', h):
        if s not in GEZINTI and s not in out:
            out.append(s)
    return out[:en_cok]


def _kok(k):
    k = k.lower()
    return k[:max(4, len(k) - 3)] if len(k) > 5 else k


def parca(madde, anahtarlar, sinir=1600):
    """Maddenin anahtar kelimelere en ilgili paragraflarını (cümle pencereleri) seçer."""
    koks = {_kok(a) for a in anahtarlar if a and len(a) >= 3}
    cumleler = []
    for p in madde["metin"]:
        cumleler.extend(re.split(r"(?<=[.!?])\s+", p))
    puan = []
    for i, c in enumerate(cumleler):
        cl = c.lower()
        puan.append(sum(1 for k in koks if k in cl))
    secili = set()
    for i in sorted(range(len(cumleler)), key=lambda i: -puan[i]):
        if puan[i] == 0 and secili:
            break
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(cumleler):
                secili.add(j)
        if sum(len(cumleler[j]) for j in secili) > sinir:
            break
    if not secili:
        secili = set(range(min(4, len(cumleler))))
    metin, onceki = [], None
    for j in sorted(secili):
        if onceki is not None and j != onceki + 1:
            metin.append("[…]")
        metin.append(cumleler[j])
        onceki = j
    return " ".join(metin)[: sinir + 400]


if __name__ == "__main__":
    k = sys.argv[1]
    if k == "getir":
        m = getir(sys.argv[2])
        print(m and (m["baslik"], m["url"], " ".join(m["metin"])[:500]))
    elif k == "ara":
        print(ara(" ".join(sys.argv[2:])))
