from pathlib import Path
from html import escape
import json
import argparse
import re
import shutil

ROOT = Path(__file__).resolve().parent
SITE = ROOT / 'site'
CONTENT = ROOT / 'content'
INTEGRATIONS = ROOT / 'integrations'
LABS = [
    ('Внутренняя статистика', 'Три лог-анализатора, классификация и контрольные вопросы.'),
    ('Внешняя статистика', 'Сравнение сервисов, измеримые цели и ошибки усреднения.'),
    ('LiveInternet', 'Регистрация счётчика и исследование посещаемости сайта.'),
    ('SberAds / Топ-100', 'Событийная аналитика, отчёты и целевые действия.'),
    ('Рейтинг Mail.ru / MyTracker', 'Настройка веб-счётчика, целей и сегментов.')
]

def integration(name):
    path = INTEGRATIONS / name
    return path.read_text(encoding='utf-8') if path.exists() else ''

def shell(title, body, current, lead=''):
    links = '<a href="index.html"'+(' aria-current="page"' if current == 0 else '')+'>Обзор работ</a>'
    for n, (name, _) in enumerate(LABS, 1):
        links += f'<a href="lab-{n}.html"'+(' aria-current="page"' if current == n else '')+f'>{n:02} · {escape(name)}</a>'
    tracking_head = integration('liveinternet-head.html')
    config = json.dumps(json.loads((ROOT/'counters.json').read_text(encoding='utf-8')), ensure_ascii=False).replace('<', '\\u003c')
    tracking_head += f'<script id="counter-config" type="application/json">{config}</script>'
    tracking_body = integration('sberads.html') + integration('mytracker.html')
    badges = integration('liveinternet-badge.html') + integration('sberads-badge.html')
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · Веб-аналитика</title>{tracking_head}<meta name="description" content="{escape(lead, quote=True)}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/counters.js" defer></script><script src="assets/ui.js" defer></script></head>
<body>{tracking_body}<a class="skip" href="#main">К содержанию</a><aside class="sidebar"><a class="brand" href="index.html">Веб-аналитика<small>Московский Политех · ВА78БЗ</small></a><nav aria-label="Лабораторные работы" data-analytics-block="lab-navigation">{links}</nav><footer>Лабораторные работы 1–5<br>Октябрь 2026</footer></aside><main id="main"><span class="eyebrow">Учебный стенд / {('Обзор' if current == 0 else f'Лабораторная {current:02}')}</span><h1>{escape(title)}</h1>{f'<p class="lead">{escape(lead)}</p>' if lead else ''}{body}<footer class="site-footer"><a href="https://github.com/DimazikSkyter/web-analytics-labs">Исходники на GitHub</a><p>Учебный проект · 2026</p><div id="counter-badges">{badges}</div></footer></main></body></html>'''

def build():
    SITE.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets', SITE/'assets', dirs_exist_ok=True)
    (SITE/'.nojekyll').write_text('', encoding='utf-8')
    status = json.loads((ROOT/'status.json').read_text(encoding='utf-8'))
    cards = ''
    for n, (name, desc) in enumerate(LABS, 1):
        cards += f'<a class="card" href="lab-{n}.html"><div class="number">{n:02}</div><h2>{escape(name)}</h2><p>{escape(desc)}</p><small>{escape(status[str(n)])}</small></a>'
        source = CONTENT/f'lab-{n}.html'
        if source.exists():
            controls = f'<div class="actions" data-analytics-block="report-actions"><button type="button" data-print-report>Печать отчёта</button><a class="button secondary" href="https://online.mospolytech.ru/mod/assign/view.php?id={576809+n}">Задание в СДО</a></div>'
            report = source.read_text(encoding='utf-8')
            headings = re.findall(r'<h2>(.*?)</h2>', report)
            toc = '<nav class="toc" aria-label="Содержание отчёта">' + ''.join(f'<a href="#section-{i}">{h}</a>' for i,h in enumerate(headings,1)) + '</nav>'
            i = 0
            def heading_id(match):
                nonlocal i
                i += 1
                return f'<h2 id="section-{i}">{match.group(1)}</h2>'
            report = re.sub(r'<h2>(.*?)</h2>', heading_id, report)
            proof = SITE/'assets'/'site-overview.jpg'
            if proof.exists():
                report = report.replace('<div class="site-proof"></div>', '<figure><a href="assets/site-overview.jpg"><img src="assets/site-overview.jpg" alt="Главная страница учебного сайта с меню пяти работ" loading="lazy" width="1548" height="1232"></a><figcaption>Рисунок 1 — опубликованный учебный сайт, 06.10.2026. Снимок можно открыть в полном размере.</figcaption></figure>')
            else:
                report = report.replace('<div class="site-proof"></div>', '')
            body = f'<span class="tag">{escape(status[str(n)])}</span>{controls}{toc}<article class="paper" data-analytics-block="lab-{n}-report"><header class="report-head"><p>Московский политехнический университет</p><p>Дисциплина «Веб-аналитика» · Лабораторная работа №{n} · Москва, 2026</p></header>{report}</article>'
            (SITE/f'lab-{n}.html').write_text(shell(name, body, n, desc), encoding='utf-8')
    home = (CONTENT/'home.html').read_text(encoding='utf-8')
    (SITE/'index.html').write_text(shell('Лабораторные работы 1–5', home+'<div class="grid">'+cards+'</div>', 0, 'Отчёты и исследование посещаемости на одном учебном сайте.'), encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='site')
    args = parser.parse_args()
    SITE = ROOT / args.output
    build()
