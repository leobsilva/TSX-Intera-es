"""Split four interactive sections of the TSX prototype into standalone demo pages.

usage: python3 -I split_sections.py <prototype dir> <output repo dir>
"""
import re
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
html = (SRC / 'index.html').read_text(encoding='utf-8')


def between(start, end, text=html, include_start=True):
    a = text.index(start)
    b = text.index(end, a + len(start))
    return text[a if include_start else a + len(start):b]


def section(cls):
    a = html.index('<section class="%s"' % cls)
    b = html.index('</section>', a) + len('</section>')
    return html[a:b]


def dedent_css(css):
    return css.rstrip() + '\n'


# ---------- Shared CSS ----------
tokens = between('  :root {', '  /* ---------- Placeholder sections')
eyebrow = between('  .eyebrow {', '  .about__body {')
btn = between('  .btn {', '  /* ---------- Brand strip')
lenis_css = between('  /* ---------- Smooth scroll (Lenis) ---------- */', '  /* ---------- Scroll tuner')

base_css = '''/* Base compartilhada pelas demos: tokens, reset, eyebrow e botão.
   Extraída do protótipo TSX (index.html). */
''' + tokens.replace('\n  ', '\n').lstrip() + '\n' + eyebrow.replace('\n  ', '\n').lstrip() + '\n' + \
    btn.replace('\n  ', '\n').lstrip() + '\n' + lenis_css.replace('\n  ', '\n').lstrip() + '''
/* Moldura das demos (não faz parte do site) */
.demo-bar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  background: var(--navy);
  color: #FFFFFF;
  font: 400 14px/1.5 var(--font);
}
.demo-bar a { color: #CEAE80; text-decoration: none; }
.demo-bar a:hover { text-decoration: underline; }
.demo-spacer {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px 20px;
  background: var(--navy);
  color: rgba(255, 255, 255, .6);
  font: 400 16px/1.5 var(--font);
  text-align: center;
}
'''

# ---------- Section CSS ----------
about_css = between('  /* ---------- Quem somos nós ---------- */', '  /* ---------- Segmentos atendidos')
about_css = about_css.replace(eyebrow, '')          # lives in base.css
sectors_css = between('  /* ---------- Segmentos atendidos', '  /* ---------- Serviços (Em que atuamos)')
projects_css = between('  /* ---------- Nossos projetos ---------- */', '  /* ---------- Notícias')
regions_css = between('  /* ---------- Regiões de atuação ---------- */', '  /* ---------- Carreira')

# ---------- Section JS ----------
js = between('<script>\n(() => {', '})();\n</script>', include_start=False)

about_js = between('  /* ---------- Title words ---------- */', '  /* ---------- Tuner UI', js)
about_js = re.sub(r"\n    live\.textContent = [^;]+;", '', about_js)
about_js = '''  const section = document.querySelector('.about');
  const row = document.getElementById('stats');
  const title = document.getElementById('about-title');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- Parameters ---------- */
  // Gatilho "enter":  % da section que já entrou na tela vindo de baixo (100% = section inteira visível).
  // Gatilho "exit":   % da section que já passou pelo topo depois de aparecer inteira.
  // Gatilho "center": 0% quando a fileira de boxes entra por baixo, 100% quando o centro da section
  //                   chega ao centro da tela (os boxes se alinham à medida que a section é centralizada).
  const P = {
    titleTrigger: 'enter',  titleStart: 0, titleEnd: 100,
    boxTrigger: 'center',   boxStart: 0,   boxEnd: 100,
    step: 25.76,       // diferença de altura entre boxes vizinhos antes do scroll
    smoothing: 0.07,   // 0–1: menor = movimento mais macio
    scrollLerp: 0.08,  // inércia do scroll suave (Lenis)
  };

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const easeInOut = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const range = (m, start, end) => end <= start ? (m >= start ? 1 : 0) : clamp((m - start) / (end - start), 0, 1);

''' + about_js + '''  /* ---------- Smooth scroll ---------- */
  let lenis = null;
  function setupLenis() {
    lenis?.destroy();
    lenis = null;
    if (reduce.matches || typeof Lenis === 'undefined') return;
    lenis = new Lenis({ lerp: P.scrollLerp, autoRaf: true });
  }

  /* ---------- Start ---------- */
  row.style.setProperty('--step', P.step + 'px');
  setupLenis();
  measure();
  Object.assign(current, target);
  apply(current);
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  reduce.addEventListener?.('change', () => { setupLenis(); apply(current); });
'''

sectors_js = between('  /* ---------- Sectors:', '  /* ---------- Brand strip', js)
projects_js = "  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');\n\n" + \
    between('  /* ---------- Projects:', '  /* ---------- Smooth scroll ---------- */', js)
regions_js = "  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');\n\n" + \
    between('  /* ---------- Regiões:', '  /* ---------- Navbar:', js)

# ---------- Pages ----------
FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600&family=Spline+Sans+Mono:wght@400&display=swap">'''

SPACER_TOP = '<div class="demo-spacer" aria-hidden="true">Role para baixo ↓</div>'
SPACER_BOTTOM = '<div class="demo-spacer" aria-hidden="true">Role para cima ↑ para ver a interação ao contrário</div>'


def page(title, slug, about, css, body, script, extra_head='', spacers=False):
    body_html = body.replace('src="assets/', 'src="../assets/').replace('url("assets/', 'url("../assets/')
    css = css.replace('url("assets/', 'url("../assets/')
    parts = [
        '<!doctype html>',
        '<html lang="pt-BR">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s · TSX Interações</title>' % title,
        FONTS,
        '<link rel="stylesheet" href="../shared/base.css">',
        '<style>',
        dedent_css(css),
        '</style>',
        extra_head,
        '</head>',
        '<body>',
        '<div class="demo-bar"><span>%s — %s</span><a href="../index.html">← Todas as interações</a></div>' % (title, about),
        SPACER_TOP if spacers else '',
        body_html,
        SPACER_BOTTOM if spacers else '',
        '<script>',
        '(() => {',
        script.rstrip(),
        '})();',
        '</script>',
        '</body>',
        '</html>',
        '',
    ]
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text('\n'.join(p for p in parts if p != ''), encoding='utf-8')
    return body_html + css


LENIS = '<script src="https://cdn.jsdelivr.net/npm/lenis@1.3.4/dist/lenis.min.js"></script>'

DEMOS = [
    ('Quem somos nós', 'quem-somos-nos',
     'título revela palavra a palavra e os bignumbers se alinham conforme a section chega ao centro da tela',
     about_css, section('about'), about_js, LENIS, True),
    ('Soluções em diferentes frentes', 'solucoes-em-diferentes-frentes',
     'hover/foco/toque num segmento troca o estado do item e a imagem',
     sectors_css, section('sectors'), sectors_js, '', False),
    ('Traduzindo experiência em resultados', 'traduzindo-experiencia-em-resultados',
     'carrossel infinito de projetos, começa no projeto do meio (setas, teclado e arraste)',
     projects_css, section('projects'), projects_js, '', False),
    ('Regiões que atuamos', 'regioes-que-atuamos',
     'estados acendem em sequência no mapa; hover/foco num estado assume o controle',
     regions_css, section('regions'), regions_js, '', True),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'shared').mkdir(exist_ok=True)
(OUT / 'shared' / 'base.css').write_text(base_css, encoding='utf-8')

used = ''
for d in DEMOS:
    used += page(*d)

# ---------- Assets actually referenced ----------
(OUT / 'assets').mkdir(exist_ok=True)
assets = sorted(set(re.findall(r'\.\./assets/([\w.\-]+)', used)))
for a in assets:
    shutil.copy2(SRC / 'assets' / a, OUT / 'assets' / a)

# ---------- Hub ----------
cards = '\n'.join(
    '    <li><a href="%s/index.html"><span class="hub__name">%s</span><span class="hub__desc">%s</span></a></li>' % (slug, title, about)
    for title, slug, about, *_ in DEMOS)
(OUT / 'index.html').write_text('''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TSX Interações</title>
%s
<link rel="stylesheet" href="shared/base.css">
<style>
  .hub { max-width: 960px; margin: 0 auto; padding: 80px 24px; }
  .hub h1 { margin: 16px 0 8px; font: 500 clamp(32px, 4vw, 48px)/1.3 var(--font-2); }
  .hub > p { margin: 0 0 48px; font: 400 18px/1.5 var(--font-2); color: var(--ink-2); }
  .hub ul { list-style: none; margin: 0; padding: 0; border-top: 1px solid #C6CED2; }
  .hub li { border-bottom: 1px solid #C6CED2; }
  .hub a { display: flex; flex-direction: column; gap: 4px; padding: 24px 0; color: var(--ink); text-decoration: none; }
  .hub a:hover .hub__name { color: #005073; }
  .hub__name { font: 500 24px/1.3 var(--font-2); transition: color .2s ease; }
  .hub__desc { font: 400 16px/1.5 var(--font); color: var(--ink-2); }
</style>
</head>
<body>
<main class="hub">
  <p class="eyebrow">
    <svg viewBox="0 0 8 9" aria-hidden="true"><path fill="#AC8C58" d="M8 2.235 4 0 0 2.235v4.53L4 9l4-2.235z"/></svg>
    TSX · Site institucional
  </p>
  <h1>Interações das sections</h1>
  <p>Cada section roda sozinha, com o mesmo HTML, CSS e JS do protótipo.</p>
  <ul>
%s
  </ul>
</main>
</body>
</html>
''' % (FONTS, cards), encoding='utf-8')

print('assets:', ', '.join(assets))
for title, slug, *_ in DEMOS:
    print(slug, (OUT / slug / 'index.html').stat().st_size, 'bytes')
