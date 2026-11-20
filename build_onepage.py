# -*- coding: utf-8 -*-
"""Assemble the 10-page Krupka site into one long-scroll index.html.
Run once; safe to re-run (reads from .bak originals if present)."""
import re, os, shutil, io

SITE = os.path.dirname(os.path.abspath(__file__))

PAGES = ["index","object","plans","market","business","financials","investors","swot","roadmap"]

def src(name):
    """Read original page (prefer .orig backup so the script is idempotent)."""
    orig = os.path.join(SITE, "_orig", name + ".html")
    live = os.path.join(SITE, name + ".html")
    path = orig if os.path.exists(orig) else live
    with io.open(path, encoding="utf-8") as f:
        return f.read()

# ---- backup originals once ----
orig_dir = os.path.join(SITE, "_orig")
if not os.path.exists(orig_dir):
    os.makedirs(orig_dir)
    for p in PAGES + ["brandbook"]:
        shutil.copy2(os.path.join(SITE, p + ".html"), os.path.join(orig_dir, p + ".html"))

def body_content(html):
    """Content between the closing nav and the footer."""
    a = html.index("</div></nav>") + len("</div></nav>")
    b = html.index("<footer>")
    return html[a:b]

def cut_between(text, start_marker, end_marker):
    """Remove text from start_marker up to (not incl.) end_marker."""
    a = text.index(start_marker)
    b = text.index(end_marker)
    return text[:a] + text[b:]

def cut_from(text, start_marker):
    a = text.index(start_marker)
    return text[:a]

def strip_cta_bands(text):
    """Remove trailing CTA paragraph bands (buttons linking to other pages)."""
    return re.sub(
        r'\n\s*<p style="margin-top:2[68]px[^"]*">\s*(?:<a class="btn[^>]*>.*?</a>\s*(?:&nbsp;)?\s*)+</p>',
        "", text, flags=re.S)

LINKMAP = {
    "index.html": "#top", "object.html": "#about", "plans.html": "#plans",
    "market.html": "#location", "business.html": "#business",
    "financials.html": "#financials", "investors.html": "#investors",
    "swot.html": "#risks", "roadmap.html": "#roadmap",
}

def rewrite_links(text):
    for k, v in LINKMAP.items():
        text = text.replace('href="%s"' % k, 'href="%s"' % v)
    return text

def demote_h1(text):
    return text.replace("<h1>", '<h2 class="h1">').replace("</h1>", "</h2>")

def process(text):
    return rewrite_links(demote_h1(strip_cta_bands(text)))

# ================= per-page extraction =================

# ---- old index: keep stats strip + six pillars + glance (overview) ----
idx = body_content(src("index"))
idx = cut_between(idx, "<!-- HERO -->", "<!-- STATS STRIP -->")   # hero rebuilt from scratch
overview = process(idx)

# ---- object: about (intro + floors + done/ahead) ; photos extracted separately ----
obj = body_content(src("object"))
obj = cut_between(obj, "<!-- VISUALIZATIONS -->", "<!-- REAL STATE -->")
# pull out the REAL STATE photo gallery -> its own #photos section
a = obj.index("<!-- REAL STATE -->"); b = obj.index("<!-- FLOOR BY FLOOR -->")
photos_sec = obj[a:b]
obj = obj[:a] + obj[b:]
# the "honest note" references 3D renders that no longer exist on the page -> rewrite
obj = obj.replace(
    'см. <a href="plans.html">Планировки</a>; новые 3D-виды построены по этим чертежам. Фотофиксации фасада в data room по-прежнему нет — все внешние виды остаются концепт-визуализациями до её получения.',
    'см. <a href="plans.html">Планировки</a>. Фотофиксации фасада в data room пока нет — внешний вид мы показываем обмерным чертежом, а не рендером.')
obj = obj.replace(
    'viz <a href="plans.html">Výkresy</a>; nové 3D pohledy vycházejí z těchto výkresů. Fotodokumentace fasády v data roomu stále chybí — všechny exteriérové pohledy zůstávají konceptními vizualizacemi, dokud nebude k dispozici.',
    'viz <a href="plans.html">Výkresy</a>. Fotodokumentace fasády v data roomu zatím chybí — vzhled objektu ukazujeme zaměřeným výkresem, nikoli renderem.')
obj = obj.replace(
    'see <a href="plans.html">Drawings</a>; the new 3D views are built from these drawings. The data room still holds no facade photo — all exterior views remain concept visualizations until it arrives.',
    'see <a href="plans.html">Drawings</a>. The data room holds no facade photo yet — we show the building through the measured drawing, not a render.')
about = process(obj)
photos = process(photos_sec)
# photos gallery was .alt? it was a plain section; keep as is.

# ---- plans: drop the renders-from-drawings section ----
pl = body_content(src("plans"))
pl = cut_from(pl, "<!-- RENDERS FROM DRAWINGS -->")
plans = process(pl)

# ---- market -> location ----
market = process(body_content(src("market")))

# ---- business ----
business = process(body_content(src("business")))

# ---- financials ----
financials = process(body_content(src("financials")))

# ---- investors: de-hero the header, drop 3D tag, split off data-room card ----
inv = body_content(src("investors"))
# remove the 3D concept tag paragraph
inv = re.sub(r'\n\s*<p class="small" style="position:relative;z-index:2;margin-top:12px"><span class="tag concept">.*?</p>', "", inv, flags=re.S)
# hero div -> plain section (keep kicker/h1/badge/lead)
inv = inv.replace("<div class=\"hero\" style=\"background-image:url('assets/renders2/facade-true-day.jpg')\">",
                  '<section style="padding-bottom:0">')
# its closing: the hero block ends with "</div>\n</div>" before first <section>; convert outer one
inv = inv.replace("  </div>\n</div>\n\n<section>", "  </div>\n</section>\n\n<section>", 1)
inv = inv.replace('<p class="lead">', '<p class="lead" style="font-size:19px;max-width:860px;margin-top:14px">', 1)
# split: contact card section is the last <section> (data room)
cut = inv.rindex("<section>")
contact_sec = inv[cut:]
inv = inv[:cut]
investors = process(inv)
# contact: add a site-visit ghost button next to the data-room button
contact_sec = contact_sec.replace(
    '<a class="btn" href="mailto:ivan.mokan@imscout.org?subject=Krupka%20Cave%20Resort%20%E2%80%94%20Data%20Room">',
    '<a class="btn" href="mailto:ivan.mokan@imscout.org?subject=Krupka%20Cave%20Resort%20%E2%80%94%20Data%20Room">', 1)
contact_sec = contact_sec.replace(
    '</a>\n      <p class="small" style="margin-top:22px">',
    '</a>\n      &nbsp;<a class="btn ghost" href="mailto:ivan.mokan@imscout.org?subject=Krupka%20Cave%20Resort%20%E2%80%94%20Site%20Visit"><span data-lang="ru">Запросить визит на объект</span><span data-lang="cz">Vyžádat prohlídku objektu</span><span data-lang="en">Request a site visit</span></a>\n      <p class="small" style="margin-top:22px">', 1)
contact = process(contact_sec)

# ---- swot -> risks ----
risks = process(body_content(src("swot")))

# ---- roadmap ----
roadmap = process(body_content(src("roadmap")))

# ================= authored blocks =================

NAV = '''<nav class="nav"><div class="wrap">
  <a class="logo" href="#top">KRUPKA <b>CAVE</b> RESORT</a>
  <div class="nav-links">
    <a href="#about"><span data-lang="ru">Объект</span><span data-lang="cz">Objekt</span><span data-lang="en">Object</span></a>
    <a href="#tour3d"><span data-lang="ru">3D-макет</span><span data-lang="cz">3D model</span><span data-lang="en">3D Model</span></a>
    <a href="#plans"><span data-lang="ru">Чертежи</span><span data-lang="cz">Výkresy</span><span data-lang="en">Drawings</span></a>
    <a href="#photos"><span data-lang="ru">Фото</span><span data-lang="cz">Foto</span><span data-lang="en">Photos</span></a>
    <a href="#location"><span data-lang="ru">Локация</span><span data-lang="cz">Lokalita</span><span data-lang="en">Location</span></a>
    <a href="#business"><span data-lang="ru">Бизнес</span><span data-lang="cz">Byznys</span><span data-lang="en">Business</span></a>
    <a href="#financials"><span data-lang="ru">Финансы</span><span data-lang="cz">Finance</span><span data-lang="en">Financials</span></a>
    <a href="#investors"><span data-lang="ru">Инвестору</span><span data-lang="cz">Investor</span><span data-lang="en">Investors</span></a>
    <a href="#risks"><span data-lang="ru">Риски</span><span data-lang="cz">Rizika</span><span data-lang="en">Risks</span></a>
    <a href="#roadmap"><span data-lang="ru">Дорожная карта</span><span data-lang="cz">Harmonogram</span><span data-lang="en">Roadmap</span></a>
  </div>
  <div class="langs">
    <button data-set="ru" onclick="kcrSetLang('ru')">RU</button>
    <button data-set="cz" onclick="kcrSetLang('cz')">CZ</button>
    <button data-set="en" onclick="kcrSetLang('en')">EN</button>
  </div>
</div></nav>'''

# hero: artistic gold-on-dark treatment of the real measured facade drawing
HERO = '''<header class="hero hero-draw" id="top">
  <div class="wrap">
    <div class="kicker"><span data-lang="ru">Инвестиционная возможность · Крупка · Устецкий край · модель v5</span><span data-lang="cz">Investiční příležitost · Krupka · Ústecký kraj · model v5</span><span data-lang="en">Investment Opportunity · Krupka · Ústecký kraj · Model v5</span></div>
    <h1>Krupka Cave Resort</h1>
    <p class="lead"><span data-lang="ru">Туристический комплекс в регионе UNESCO: 9 апартаментов B&amp;B (8 стандартных + терраса-флагман), почти достроенный ресторан и две природные пещеры — единственный известный нам объект с природными пещерами в частном туркомплексе Крушных гор — в часе езды от Дрездена. Две модели входа с одним источником кэша и полным потоком — без разрывов финансирования: equity 65% одним чеком 13,8 млн CZK (Base IRR +4,4%, Up +14,1%) или обеспеченный купон 10% под залог 1-го ранга — доходность сейчас.</span><span data-lang="cz">Turistický komplex v regionu UNESCO: 9 apartmánů B&amp;B (8 standardních + vlajková s terasou), téměř dokončená restaurace a dvě přírodní jeskyně — jediný nám známý objekt s přírodními jeskyněmi v soukromém turistickém areálu Krušných hor — hodinu jízdy od Drážďan. Dva modely vstupu s jedním zdrojem hotovosti a úplným tokem — bez mezer ve financování: equity 65 % jedním šekem 13,8 mil. CZK (Base IRR +4,4 %, Up +14,1 %) nebo zajištěný kupon 10 % se zástavou 1. pořadí — výnos hned.</span><span data-lang="en">A tourist complex in a UNESCO region: 9 B&amp;B apartments (8 standard + a terrace flagship), a near-finished restaurant and two natural caves — the only private tourist complex with natural caves in the Ore Mountains known to us — one hour's drive from Dresden. Two entry models with a single cash source and a full flow — no funding gaps: 65% equity via a single 13.8M CZK cheque (a +4.4% Base IRR, +14.1% Up) or a secured 10% coupon behind a first-rank lien — income now.</span></p>
    <p style="margin-top:22px">
      <a class="btn" href="#investors"><span data-lang="ru">Две модели для инвестора</span><span data-lang="cz">Dva modely pro investora</span><span data-lang="en">The Two Investor Models</span></a>
      &nbsp;<a class="btn ghost" href="#financials"><span data-lang="ru">Финансовая модель</span><span data-lang="cz">Finanční model</span><span data-lang="en">Financial Model</span></a>
    </p>
    <p class="small" style="margin-top:18px"><span class="tag real"><span data-lang="ru">ЧЕРТЁЖ · 07/2026</span><span data-lang="cz">VÝKRES · 07/2026</span><span data-lang="en">DRAWING · 07/2026</span></span><span data-lang="ru">Фон — обмерный чертёж фасада D-05 (stávající stav, 07/2026, Ing. Ciganik), художественная тонировка.</span><span data-lang="cz">Pozadí — zaměřený výkres fasády D-05 (stávající stav, 07/2026, Ing. Ciganik), umělecké tónování.</span><span data-lang="en">Background — the D-05 measured facade drawing (as-built survey, 07/2026, Ing. Ciganik), artistically toned.</span></p>
  </div>
</header>'''

TOUR3D = '''<section class="alt" style="padding:64px 0">
  <div class="wrap">
    <div class="kicker"><span data-lang="ru">Интерактив</span><span data-lang="cz">Interaktivní</span><span data-lang="en">Interactive</span></div>
    <h2><span data-lang="ru">Виртуальный 3D-макет</span><span data-lang="cz">Virtuální 3D model</span><span data-lang="en">Virtual 3D Model</span></h2>
    <p class="small" style="max-width:720px;margin-bottom:18px"><span data-lang="ru">Здесь будет интерактивный 3D-макет объекта, построенный по обмерам 07/2026.</span><span data-lang="cz">Zde bude interaktivní 3D model objektu postavený dle zaměření 07/2026.</span><span data-lang="en">An interactive 3D model of the building, built from the 07/2026 survey, will live here.</span></p>
    <div class="tour3d-slot"></div>
  </div>
</section>'''

FOOTER = '''<footer><div class="wrap">
  <p><span data-lang="ru">Krupka Cave Resort · Инвестиционная платформа · Ноябрь 2026 · Подготовлено с применением аналитики IM Holding. Индикативный материал, не является офертой. Финальные условия — после due diligence; юридические документы готовит лицензированный advokát, налоговый режим подтверждает daňový poradce.</span><span data-lang="cz">Krupka Cave Resort · Investiční platforma · Listopad 2026 · Připraveno s využitím analytiky IM Holding. Indikativní materiál, nejedná se o nabídku. Finální podmínky po due diligence; právní dokumenty připraví licencovaný advokát, daňový režim potvrdí daňový poradce.</span><span data-lang="en">Krupka Cave Resort · Investment platform · November 2026 · Prepared with IM Holding analytics. Indicative material, not an offer. Final terms subject to due diligence; legal documents by a licensed Czech advokát, tax treatment confirmed by a daňový poradce.</span></p>
</div></footer>'''

HEAD = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Krupka Cave Resort — Investment Package</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/brand.css">
<script src="assets/js/main.js" defer></script>
</head>
<body>
'''

def wrap(anchor, inner):
    return '\n<div class="page-sec" id="%s">%s</div>\n' % (anchor, inner)

page = (HEAD + NAV + "\n\n" + HERO + "\n"
        + overview
        + wrap("about", about)
        + '<div id="tour3d">' + TOUR3D + '</div>\n'
        + wrap("plans", plans)
        + wrap("photos", photos)
        + wrap("location", market)
        + wrap("business", business)
        + wrap("financials", financials)
        + wrap("investors", investors)
        + wrap("risks", risks)
        + wrap("roadmap", roadmap)
        + wrap("contact", contact)
        + "\n" + FOOTER + "\n\n</body>\n</html>\n")

with io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)

# ================= redirect stubs =================
REDIR = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=index.html{anchor}">
<link rel="canonical" href="index.html{anchor}">
<script>location.replace("index.html{anchor}")</script>
<title>Krupka Cave Resort</title>
</head>
<body><p><a href="index.html{anchor}">Krupka Cave Resort &rarr;</a></p></body>
</html>
'''
for name, anchor in [("object","#about"),("plans","#plans"),("market","#location"),
                     ("business","#business"),("financials","#financials"),
                     ("investors","#investors"),("swot","#risks"),("roadmap","#roadmap")]:
    with io.open(os.path.join(SITE, name + ".html"), "w", encoding="utf-8") as f:
        f.write(REDIR.format(anchor=anchor))

print("index.html bytes:", os.path.getsize(os.path.join(SITE, "index.html")))
print("OK")
