# TSX Interações

Repositório de referência de como algumas sections do site do Grupo TSX se comportam com interações. Cada section roda sozinha, com o mesmo HTML, CSS e JS do protótipo do site (`index.html` do projeto TSX).

## Como abrir

Abra `index.html` no navegador. A página lista as sections e leva a cada demo.

Se preferir servir localmente:

```sh
python3 -m http.server 8000
# http://localhost:8000
```

## Sections

| Section | Pasta | Interação |
|---|---|---|
| Quem somos nós | [`quem-somos-nos/`](quem-somos-nos/) | O título revela as palavras conforme a section entra na tela. Os quatro bignumbers começam desalinhados e se alinham à medida que a section se aproxima do centro da tela, só com o scroll (volta ao rolar para cima). Usa scroll suave (Lenis). |
| Soluções em diferentes frentes | [`solucoes-em-diferentes-frentes/`](solucoes-em-diferentes-frentes/) | Lista de segmentos atendidos. Hover, foco ou toque num segmento destaca o item (fundo bege e barra azul) e troca a foto ao lado com fade. |
| Traduzindo experiência em resultados | [`traduzindo-experiencia-em-resultados/`](traduzindo-experiencia-em-resultados/) | Carrossel infinito de projetos que começa no projeto do meio. Navega pelas setas, pelo teclado (← →) e por arraste/scroll horizontal. |
| Regiões que atuamos | [`regioes-que-atuamos/`](regioes-que-atuamos/) | Mapa do Brasil. Quando a section entra na tela, os estados acendem em sequência e o card mostra as cidades e uma foto. Hover ou foco num estado assume o controle; ao sair, a sequência continua de onde parou. |

As demos de **Quem somos nós** e **Regiões que atuamos** têm um espaço escuro antes e depois da section, porque a interação depende do scroll ou da entrada na tela.

Todas respeitam `prefers-reduced-motion`: com movimento reduzido, os bignumbers já aparecem alinhados, o mapa fica parado num estado e o carrossel troca sem animação.

## Parâmetros principais

- **Quem somos nós** — no início do script, objeto `P`:
  - `boxTrigger: 'center'`, `boxStart: 0`, `boxEnd: 100`: os boxes vão de desalinhados (0%) a alinhados (100%) entre o momento em que a fileira entra por baixo e o momento em que o centro da section chega ao centro da tela.
  - `step`: diferença de altura entre boxes vizinhos antes do alinhamento (25.76px).
  - `smoothing`: suavidade do movimento (0.07; 1 acompanha o scroll sem atraso).
  - `scrollLerp`: inércia do scroll suave (0.08).
- **Regiões que atuamos** — `HOLD` (2640 ms com o estado aberto), `GAP` (1300 ms até o próximo) e `SWAP` (640 ms para o card fechar antes de reabrir com outro estado).
- **Traduzindo experiência em resultados** — o carrossel tem cópias inertes antes e depois dos projetos reais; quando o scroll para numa cópia, salta sem animação para o mesmo card no conjunto real.

## Estrutura

```
index.html                 lista das demos
shared/base.css            tokens de cor e fonte, eyebrow, botão e estilos do Lenis
<section>/index.html       uma demo por section (CSS e JS da section embutidos)
assets/                    imagens e logos usados pelas demos
scripts/split_sections.py  extrai as sections do protótipo e regera as demos
```

## Atualizar a partir do protótipo

As demos são geradas a partir do `index.html` do protótipo. Depois de mudar o protótipo:

```sh
python3 scripts/split_sections.py "/caminho/para/TSX" .
```

O script localiza cada section pelos comentários de CSS e JS do protótipo (`/* ---------- Quem somos nós ---------- */` etc.). Se esses comentários mudarem, ajuste o script.

## Dependências externas

- Fontes Archivo e Plus Jakarta Sans (Google Fonts).
- [Lenis](https://github.com/darkroomengineering/lenis) 1.3.4 via jsDelivr, só na demo Quem somos nós.
