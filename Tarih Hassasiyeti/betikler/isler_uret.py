"""İş listesi üretici. Kullanım: python isler_uret.py kaynak|konu > isler.json"""
import json, sys

KONULAR = {
    "unvan-hitap": "unvan ve hitaplar (ağa, efendi, bey, paşa, sultan, hanım, hatun, çelebi, efendimiz, hünkâr, 'majesteleri' gibi Batılı kalıplar)",
    "saray-devlet": "saray ve devlet teşkilatı (Divan-ı Hümayun, Bâbıâli, Arz Odası, sadrazam, kubbe vezirleri, reisülküttap, kaptanıderya, şeyhülislam, kadı, enderun, bostancı, kapıcıbaşı, padişahın gündelik işleyişi)",
    "ordu": "ordu ve asker (yeniçeri, kapıkulu, sipahi, tımar, Nizam-ı Cedid, topçu, humbaracı, lağımcı, rütbeler, 'asker', 'gardiyan', 'muhafız' gibi yanlış kullanılan kelimeler)",
    "giyim": "giyim ve kuşam (sarık, kavuk, kallavi, mücevveze, fes (1829 sonrası), kaftan, ferace, yaşmak, çarşaf, renk ve kıyafet kuralları, sınıflara göre kıyafet)",
    "gundelik-dil": "gündelik dil ve konuşma (dönemde söylenmeyecek modern kelimeler ve kalıplar: 'tamam', 'merhaba', 'teşekkürler', 'okey', 'saat kaç', 'Türkiye', 'vatandaş', 'millet' anlam kayması, öztürkçe kelimeler, Cumhuriyet dönemi uydurma kelimeleri)",
    "harem-kadin": "harem ve kadınlar (harem teşkilatı, valide sultan, haseki, kadınefendi (18. yy unvanları), cariye, kalfa, usta, ikbal, gözde, 'hürrem sultan' kalıpları, kadınların sokakta görünürlüğü, Batılı harem fantezileri)",
    "para-olcu-takvim": "para, ölçü, takvim ve saat (akçe, kuruş, para, altın türleri, okka, dirhem, arşın, zira, mil, fersah, Hicrî ve Rumî takvim, ezani/alaturka saat, gün batımıyla başlayan gün, saat söyleme biçimleri)",
    "din-gundelik": "din ve gündelik hayat (namaz vakitleri, ezan, cami görevlileri, tekke ve tarikatler, hamam, kadı mahkemesi, gayrimüslimler ve millet sistemi, cenaze, düğün, bayram, Ramazan gelenekleri)",
    "yemek-kahve-tutun": "yemek, kahve ve tütün (domates, patates, mısır, biber gibi Yeni Dünya ürünlerinin 1798'deki yaygınlığı, çay (yaygın değil), kahvehane, tütün ve çubuk, nargile, sofra düzeni, çatal-kaşık, şerbet, rakı-şarap, ekmek)",
    "sehir-mekan": "şehir ve mekân adları (İstanbul / Kostantiniyye / Dersaadet, Topkapı Sarayı adı, Dolmabahçe (1856), Beyoğlu/Pera, Galata, Üsküdar, Rumeli, Anadolu, 'Türkiye' adı, Mısır, Arnavutluk vb. 1798 adları ve yapılar)",
    "teknoloji-esya": "teknoloji ve eşya anakronizmleri (kibrit, gaz lambası, fotoğraf, gözlük, cep saati, posta, telgraf, matbaa (Müteferrika), gazete, sigara, kâğıt para (kaime 1840), kilit, cam pencere, buharlı makine, tüfek türleri, çakmaklı tüfek)",
    "yazi-belge": "yazışma ve resmî belgeler (ferman, berat, hatt-ı hümayun, tuğra, mühür, padişahın imza atmaması, arz, takrir, ilam, kâtip, divan edebiyatı ve yazı türleri, Osmanlıca yazı, 'kanun' ve 'yasa' kelimeleri)",
    "isim-ad": "kişi adları ve adlandırma (soyadı olmaması (1934), lakap, baba adı, 'oğlu', memleket nisbesi, kul kökenli adlar, gayrimüslim adları, padişah adlandırma ('Sultan Selim Han'), 1798'de bir Türk'ün tanıtılma biçimi)",
    "diplomasi-donem": "1798-1800 dönemine özgü siyaset ve diplomasi (III. Selim, Nizam-ı Cedid, Fransa'nın Mısır seferi 1798, Osmanlı-Rus-İngiliz ittifakı, Cezzar Ahmed Paşa, ayanlar, Pazvandoğlu, elçilikler, Yusuf Ziya Paşa, Küçük Hüseyin Paşa, dönemin terimleri)",
}

KISILER = [
    "Murat Bardakçı", "İlber Ortaylı", "Halil İnalcık", "Ceren Sungur (YouTube kanalı)",
    "Erhan Afyoncu", "Emrah Safa Gürkan", "Feridun M. Emecen", "Ahmet Şimşirgil",
    "Ekrem Buğra Ekinci", "Mustafa Armağan", "İskender Pala", "Talha Uğurluel",
]

YAPIMLAR = [
    "Muhteşem Yüzyıl", "Muhteşem Yüzyıl Kösem", "Diriliş Ertuğrul", "Kuruluş Osman",
    "Payitaht Abdülhamid", "Mehmed: Fetihler Sultanı", "Rise of Empires: Ottoman (Netflix)",
    "Barbaroslar: Akdeniz'in Kılıcı", "Fetih 1453 (film)", "Kalbimin Sultanı ve III. Selim dönemini anlatan yapımlar",
    "Osmanlı dizilerinde en çok yapılan tarih hataları (genel derlemeler)",
    "tarihi dizilerde anakronik kelime ve deyimler (dil hataları)",
]

MADDE = (
    '{"yanlis": "dizide/filmde görülen yanlış kullanım", "dogru": "doğrusu", '
    '"aciklama": "en çok 2 cümle", "konu": "şu kodlardan biri: ' + ", ".join(KONULAR) + '", '
    '"donem": "eleştirinin ait olduğu dönem: 13.yy / 15.yy / 16.yy / 17.yy / 18.yy / 19.yy / genel", '
    '"gecerli_1798": "evet / hayır / kısmen (1798-1800 İstanbul\'u için bu düzeltme geçerli mi)", '
    '"yapim": "hangi dizi/film", "kisi": "eleştiren kişi", "kaynak_url": "adres", '
    '"kaynak_ozet": "kaynaktaki ilgili ifadenin en çok 15 kelimelik özeti veya kısa alıntısı"}'
)

ORTAK = (
    "Bir alternatif tarih romanı (olaylar 1798-1800 İstanbul'unda, III. Selim döneminde geçiyor) için "
    "Osmanlı konulu dizi ve filmlerde tarihçilerin eleştirdiği bariz hataları topluyoruz. "
    "Kurallar: Yalnız gerçekten okuduğun sayfalardaki bilgiyi yaz; adres uydurma; sayfayı webfetch ile açamadıysan o maddeyi yazma. "
    "Kaynaktan uzun alıntı kopyalama, en çok 15 kelime. Bütün metin Türkçe olsun. "
    "Dönem ayrımına dikkat: 16. yüzyılda doğru olan şey 1798'de yanlış olabilir, tersi de mümkün. "
)


def kaynak_isleri():
    isler = []
    hedefler = [("kisi", k) for k in KISILER] + [("yapim", y) for y in YAPIMLAR]
    for i, (tur, ad) in enumerate(hedefler):
        if tur == "kisi":
            gorev = (f"Görev: websearch ile {ad} adlı tarihçi/anlatıcının Osmanlı konulu dizi ve filmlerdeki tarih hatalarını eleştirdiği "
                     "yazı, röportaj, haber ve video açıklamalarını ara (en az 4 farklı arama sorgusu dene). En alakalı 5-8 sayfayı webfetch ile oku.")
        else:
            gorev = (f"Görev: websearch ile '{ad}' hakkında tarihçilerin ve uzmanların dile getirdiği tarih hatalarını (kıyafet, unvan, dil, mekân, olay, teşkilat) "
                     "ara (en az 4 farklı arama sorgusu dene). En alakalı 5-8 sayfayı webfetch ile oku.")
        cikis = (" Sonunda YALNIZCA tek bir ```json bloğu yaz, biçimi: "
                 '{"kaynaklar": [{"url": "", "baslik": "", "kisi": "", "tarih": "yayın tarihi ya da bilinmiyor", "yapim": "", "tur": "yazı/haber/röportaj/video/forum"}], '
                 '"maddeler": [' + MADDE + "]}. "
                 "Somut, tek tek hata maddeleri istiyoruz (ör. 'X kıyafeti o dönemde yoktu'), genel yorum değil. Bulabildiğin kadar madde yaz, 30'u geçme.")
        isler.append({"ad": f"kaynak-{i+1:02d}", "model": "opencode/deepseek-v4.1-flash-free",
                      "istem": ORTAK + gorev + cikis, "cikti": f"ham/kaynak-{i+1:02d}.json", "sure": 1500})
    return isler


def konu_isleri():
    isler = []
    for kod, tanim in KONULAR.items():
        istem = (ORTAK +
                 f"Görev: Konu: {tanim}. Bir yazarın ya da dizi senaristinin 1798-1800 İstanbul'unu anlatırken bu konuda en sık yapacağı, "
                 "tarih bilen okurun midesini bulandıracak 20-30 bariz hatayı listele. Önce aklındaki adayları çıkar, sonra her biri için "
                 "TDV İslam Ansiklopedisi'nde (https://islamansiklopedisi.org.tr/<madde-adi> biçiminde, ör. https://islamansiklopedisi.org.tr/kapikulu) "
                 "ilgili maddeyi webfetch ile aç ve bilgiyi oradan teyit et. TDV'de bulamazsan güvenilir başka bir kaynak (üniversite yayını, dergipark makalesi) ara. "
                 "Teyit edemediğin adayı listeye koyma. Her maddede 'kisi' alanına 'konu taraması', 'yapim' alanına biliniyorsa örnek yapımı ya da 'genel' yaz. "
                 "Sonunda YALNIZCA tek bir ```json bloğu yaz, biçimi: "
                 '{"maddeler": [' + MADDE + "]}.")
        isler.append({"ad": f"konu-{kod}", "model": "opencode/deepseek-v4.1-flash-free",
                      "istem": istem, "cikti": f"ham/konu-{kod}.json", "sure": 1800})
    return isler


if __name__ == "__main__":
    f = {"kaynak": kaynak_isleri, "konu": konu_isleri}[sys.argv[1]]
    print(json.dumps(f(), ensure_ascii=False, indent=1))
