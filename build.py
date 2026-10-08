from pathlib import Path
from html import escape
import argparse
import json
import shutil

ROOT = Path(__file__).resolve().parent
BASE = 'https://dimazikskyter.github.io/web-analytics-labs/'
ASSETS = ['style.css', 'ui.js', 'counters.js', 'favicon.svg']
MODELS = json.loads((ROOT / 'models.json').read_text(encoding='utf-8'))


def integration(name):
    return (ROOT / 'integrations' / name).read_text(encoding='utf-8')


def json_script(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')


def phone_art(tone, hero=False):
    return f'<div class="phone-art {escape(tone)} {"large" if hero else ""}" aria-hidden="true"><div class="phone-shell"><div class="phone-screen"><span class="phone-camera"></span><span class="screen-orbit"></span><span class="screen-orbit second"></span><span class="screen-line"></span></div></div></div>'


def card(model, small=False):
    m = model
    return f'''<article class="phone-card {"related-card" if small else ""}" data-phone-card data-search="{escape(' '.join([m['search'], m['brand'], m['name'], m['system'], m['storage']]), quote=True)}" data-categories="{' '.join(m['categories'])}">
<a class="card-visual" href="{m['slug']}.html" aria-label="{escape(m['name'])}: характеристики и выбор">{phone_art(m['tone'])}<span class="pill">{escape(m['tag'])}</span></a>
<div class="card-body"><p class="brand-label">{escape(m['brand'])}</p><h3><a href="{m['slug']}.html">{escape(m['name'])}</a></h3><p class="card-summary">{escape(m['summary'])}</p><dl class="card-specs"><div><dt>Экран</dt><dd>{escape(m['screen'])}</dd></div><div><dt>Частота</dt><dd>{escape(m['refresh'])}</dd></div></dl><a class="text-link" href="{m['slug']}.html">Подробнее <span aria-hidden="true">↗</span></a></div></article>'''


def shell(title, description, body, page='index.html', model=None):
    config = json_script(json.loads((ROOT / 'counters.json').read_text(encoding='utf-8')))
    tracking_head = integration('liveinternet-head.html') + f'<script type="application/json" id="counter-config">{config}</script>'
    tracking_body = integration('sberads.html') + integration('mytracker.html')
    badges = integration('liveinternet-badge.html') + integration('sberads-badge.html')
    schema = {'@context': 'https://schema.org', '@type': 'WebSite' if model is None else 'Article', 'name': title, 'url': BASE + page, 'inLanguage': 'ru', 'description': description}
    if model:
        schema.update({'headline': model['question'], 'dateModified': '2026-10-08', 'publisher': {'@type': 'Organization', 'name': 'СмартВыбор'}})
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · СмартВыбор</title><meta name="description" content="{escape(description, quote=True)}"><meta name="theme-color" content="#f6f7fb"><link rel="canonical" href="{BASE + page}"><meta property="og:type" content="{'article' if model else 'website'}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{BASE + page}"><meta property="og:site_name" content="СмартВыбор"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script type="application/ld+json">{json_script(schema)}</script>{tracking_head}<script src="assets/counters.js" defer></script><script src="assets/ui.js" defer></script></head>
<body>{tracking_body}<a class="skip" href="#main">К содержанию</a><header class="site-header"><div class="header-inner"><a class="logo" href="index.html"><span class="logo-mark" aria-hidden="true">S</span>СмартВыбор<span class="logo-dot" aria-hidden="true">.</span></a><nav aria-label="Главное меню" data-analytics-block="phone-navigation"><a href="index.html#catalog">Смартфоны</a><a href="index.html#choose">Как выбрать</a><a href="index.html#about">О проекте</a></nav><a class="header-cta" href="index.html#catalog">Найти телефон <span aria-hidden="true">↗</span></a></div></header><main id="main">{body}</main><footer class="site-footer"><div class="footer-main"><a class="logo" href="index.html"><span class="logo-mark" aria-hidden="true">S</span>СмартВыбор<span class="logo-dot" aria-hidden="true">.</span></a><p>Характеристики и понятные ориентиры для выбора смартфона.</p><span>© 2026 СмартВыбор</span></div><div class="footer-bottom"><span>Характеристики сверены 8 октября 2026. Версии для разных рынков могут отличаться.</span><div class="counter-badges">{badges}</div></div></footer></body></html>'''


def home():
    content = (ROOT / 'content' / 'home.html').read_text(encoding='utf-8')
    content = content.replace('<!-- PHONE_CARDS -->', ''.join(card(m) for m in MODELS))
    return shell('Смартфоны для ваших задач: выбор и характеристики', 'Сравните iPhone, Samsung Galaxy, Redmi, POCO и Google Pixel. Поиск по моделям и выбор телефона для фото, игр или повседневных задач.', content)


def article(model, index):
    m = model
    rows = ''.join(f'<tr><th scope="row">{escape(k)}</th><td>{escape(v)}</td></tr>' for k, v in m['specs'])
    faq = ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in m['faq'])
    body = (ROOT / 'content' / f"{m['slug']}.html").read_text(encoding='utf-8')
    related = [MODELS[(index + 1) % len(MODELS)], MODELS[(index + 2) % len(MODELS)]]
    toc = '<nav class="article-toc" aria-label="Содержание"><a href="#overview">Для кого</a><a href="#check">Перед покупкой</a><a href="#specs">Характеристики</a><a href="#faq">Вопросы</a></nav>'
    page = f'''<div class="container"><nav class="breadcrumbs" aria-label="Хлебные крошки"><a href="index.html">Главная</a><span aria-hidden="true">/</span><a href="index.html#catalog">Смартфоны</a><span aria-hidden="true">/</span><span>{escape(m['name'])}</span></nav><section class="product-hero"><div><span class="eyebrow">{escape(m['brand'])} / Разбор модели</span><h1>{escape(m['question'])}</h1><p class="lead">{escape(m['summary'])}</p><p class="updated">Обновлено 8 октября 2026 · По характеристикам производителя</p><div class="actions" data-analytics-block="phone-actions"><a class="button" href="#specs">Смотреть характеристики <span aria-hidden="true">↓</span></a><button class="button secondary" type="button" data-print-report>Печать / сохранить PDF</button></div></div><div class="product-visual {m['tone']}">{phone_art(m['tone'], True)}<span class="visual-label">{escape(m['tag'])}</span></div></section>{toc}<div class="article-layout"><article class="article-body" data-analytics-block="{m['slug']}-article">{body}<section id="specs"><span class="eyebrow">Основные параметры</span><h2>Характеристики {escape(m['name'])}</h2><div class="table-scroll"><table><caption>Данные производителя; комплектация и варианты памяти зависят от рынка</caption><tbody>{rows}</tbody></table></div><p class="source-note">Источник: <a href="{escape(m['source'], quote=True)}" target="_blank" rel="noopener">{escape(m['source_name'])}</a>.</p></section><section id="faq"><span class="eyebrow">Коротко и по делу</span><h2>Частые вопросы</h2>{faq}</section><section class="sources" id="sources"><h2>Проверить у производителя</h2><p>Перед заказом сопоставьте точное имя модели, региональное исполнение и условия продавца.</p><a class="button secondary" href="{escape(m['source'], quote=True)}" target="_blank" rel="noopener">Официальная спецификация <span aria-hidden="true">↗</span></a></section></article><aside class="article-aside"><div class="aside-box"><span class="eyebrow">Быстрый ориентир</span><h2>{escape(m['name'])}</h2><dl><div><dt>Система</dt><dd>{escape(m['system'])}</dd></div><div><dt>Экран</dt><dd>{escape(m['screen'])}</dd></div><div><dt>Накопитель</dt><dd>{escape(m['storage'])}</dd></div></dl><a class="text-link" href="index.html#catalog">Посмотреть другие модели ↗</a></div></aside></div><section class="related"><div class="section-heading"><div><span class="eyebrow">Продолжить выбор</span><h2>Ещё два варианта для сравнения</h2></div><a class="text-link" href="index.html#catalog">Все смартфоны ↗</a></div><div class="related-grid">{''.join(card(r, True) for r in related)}</div></section></div>'''
    return shell(m['question'], m['description'], page, f"{m['slug']}.html", m)


def build(site):
    site.mkdir(parents=True, exist_ok=True)
    (site / 'assets').mkdir(exist_ok=True)
    for name in ASSETS:
        shutil.copy2(ROOT / 'assets' / name, site / 'assets' / name)
    (site / '.nojekyll').write_text('', encoding='utf-8')
    (site / 'index.html').write_text(home(), encoding='utf-8')
    for index, m in enumerate(MODELS):
        target = f"{m['slug']}.html"
        (site / target).write_text(article(m, index), encoding='utf-8')
        legacy = f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(m["name"])} · СмартВыбор</title><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{BASE + target}"></head><body><p>Перейти к материалу <a href="{target}">{escape(m["name"])}</a>.</p></body></html>'
        (site / f'lab-{index + 1}.html').write_text(legacy, encoding='utf-8')
    urls = ['index.html'] + [f"{m['slug']}.html" for m in MODELS]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{BASE + p}</loc><lastmod>2026-10-08</lastmod></url>' for p in urls) + '</urlset>'
    (site / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (site / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n', encoding='utf-8')
    print(f'Built 6 content pages and 5 redirects in {site.name}/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='site')
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError('Output must stay within the project')
    build(output)
