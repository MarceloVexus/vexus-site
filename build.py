#!/usr/bin/env python3
"""Gerador estático do site Vexus — SEM dependências (só a biblioteca padrão).

  src/layout.html          cabeçalho + menu + rodapé (definidos UMA vez)
  src/pages/*.html         páginas institucionais (fragmento com <!-- meta ... -->)
  src/posts/*.html         posts do blog (fragmento com <!-- post ... -->)
        ->  docs/*.html    (páginas), site/<slug>.html (posts), site/conteudo.html (índice)

Rodar:  python3 build.py
"""
import os, re, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "src")
OUT  = os.path.join(ROOT, "docs")
NAV_KEYS = ["home", "servicos", "assessores", "conteudo", "trabalhe"]
MESES = ["", "janeiro","fevereiro","março","abril","maio","junho",
         "julho","agosto","setembro","outubro","novembro","dezembro"]

def parse_meta(text, tag="meta"):
    m = re.match(r"\s*<!--\s*%s(.*?)-->(.*)" % tag, text, re.S)
    meta, body = {}, text
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body

def render(layout, title, desc, active, mode, content):
    html = (layout
            .replace("{{TITLE}}", title)
            .replace("{{DESC}}", desc)
            .replace("{{CONTENT}}", content)
            .replace("{{TOPO_MODO}}", "" if mode == "hero" else "solido")
            .replace("{{BTN_COR}}", "branco"))
    for k in NAV_KEYS:
        html = html.replace("{{a_%s}}" % k, "ativo" if k == active else "")
    return html

def data_br(iso):
    try:
        a, m, d = iso.split("-")
        return f"{int(d)} de {MESES[int(m)]} de {a}"
    except Exception:
        return iso

def write(name, html):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(html)

def build_pages(layout):
    pages = sorted(glob.glob(os.path.join(SRC, "pages", "*.html")))
    for p in pages:
        meta, body = parse_meta(open(p, encoding="utf-8").read())
        write(os.path.basename(p),
              render(layout, meta.get("title","Vexus Capital"), meta.get("desc",""),
                     meta.get("active",""), meta.get("mode","solid"), body))
    return [os.path.basename(p) for p in pages]

def build_blog(layout):
    posts = []
    for p in sorted(glob.glob(os.path.join(SRC, "posts", "*.html"))):
        slug = os.path.splitext(os.path.basename(p))[0]
        meta, body = parse_meta(open(p, encoding="utf-8").read(), tag="post")
        posts.append({"slug": slug, "title": meta.get("title", slug),
                      "date": meta.get("date", ""), "cover": meta.get("cover", ""),
                      "excerpt": meta.get("excerpt", ""), "body": body})
    posts.sort(key=lambda x: x["date"], reverse=True)

    # páginas de artigo
    for po in posts:
        capa = f'<img class="capa-post" src="{po["cover"]}" alt="">' if po["cover"] else ""
        art = f'''
  <section class="artigo">
    <div class="wrap"><div class="col">
      <a class="voltar" href="/conteudo.html">&lsaquo; Voltar ao Conteúdo</a>
      <h1>{po["title"]}</h1>
      <div class="data">{data_br(po["date"])}</div>
      {capa}
      <div class="corpo">{po["body"].strip()}</div>
      <div class="fim-cta"><a class="btn btn-verde" href="/#contato">Fale com um assessor &rsaquo;</a></div>
    </div></div>
  </section>'''
        write(f"{po['slug']}.html",
              render(layout, f'{po["title"]} · Vexus Capital', po["excerpt"],
                     "conteudo", "solid", art))

    # índice do blog
    cards = []
    for po in posts:
        if po["cover"]:
            capa = f'<a class="capa" href="/{po["slug"]}.html"><img src="{po["cover"]}" alt=""></a>'
        else:
            capa = f'<a class="capa semcapa" href="/{po["slug"]}.html"><span>{po["title"]}</span></a>'
        cards.append(f'''
        <article class="post">
          {capa}
          <h3><a href="/{po["slug"]}.html">{po["title"]}</a></h3>
          <p>{po["excerpt"]}</p>
          <a class="saiba" href="/{po["slug"]}.html">Saiba mais</a>
        </article>''')
    idx = f'''
  <section class="pagina-topo">
    <div class="wrap">
      <h1 class="secao-titulo">Conteúdo</h1>
      <p>Análises e conteúdos sobre investimentos, câmbio, offshore e o mercado financeiro.</p>
    </div>
  </section>
  <section class="conteudo">
    <div class="wrap"><div class="posts">{"".join(cards)}
    </div></div>
  </section>'''
    write("conteudo.html",
          render(layout, "Conteúdo · Vexus Capital",
                 "Análises e conteúdos sobre investimentos, câmbio e offshore.",
                 "conteudo", "solid", idx))
    return posts

def main():
    layout = open(os.path.join(SRC, "layout.html"), encoding="utf-8").read()
    pages = build_pages(layout)
    posts = build_blog(layout)
    print(f"Páginas: {len(pages)}  ({', '.join(pages)})")
    print(f"Blog: índice conteudo.html + {len(posts)} post(s)")
    # trava: nenhum placeholder pode sobrar
    faltas = 0
    for f in glob.glob(os.path.join(OUT, "*.html")):
        left = set(re.findall(r"\{\{[^}]+\}\}", open(f, encoding="utf-8").read()))
        if left:
            faltas += 1; print(f"  AVISO {os.path.basename(f)}: {left}")
    # ⚠ O CNAME SÓ ENTRA QUANDO O DNS JÁ APONTA (18/08/2026). Com o arquivo `CNAME`
    # presente, o GitHub Pages serve o site SÓ no domínio próprio — e enquanto o
    # `vexuscapital.com.br` não tiver registro (hoje ele só tem MX, o site saiu do ar depois
    # de 23/07), o endereço de prévia `marcelovexus.github.io/vexus-site` também para de
    # responder. Ou seja: publicar com CNAME antes do DNS deixa o site inalcançável nos dois
    # endereços, que é o oposto de subir.
    #
    # ⚠ VIROU AO CONTRÁRIO EM 26/08/2026, e a razão é uma cicatriz: o DNS FICOU PRONTO.
    # Enquanto o domínio não resolvia, o padrão seguro era NÃO escrever o CNAME. Agora que
    # `vexuscapital.com.br` está no ar, o padrão seguro é o oposto: rodar o build sem
    # variável nenhuma (o jeito normal de rodar) apagava o CNAME e DERRUBAVA o domínio.
    # Aconteceu de verdade, num commit que só mexia em CSS.
    # Para voltar ao endereço do GitHub de propósito: VEXUS_SEM_DOMINIO=1.
    if os.environ.get("VEXUS_SEM_DOMINIO") == "1":
        _cn = os.path.join(OUT, "CNAME")
        if os.path.exists(_cn):
            os.remove(_cn)
        print("Domínio: endereço do GitHub (sem CNAME) — pedido por VEXUS_SEM_DOMINIO=1")
    else:
        open(os.path.join(OUT, "CNAME"), "w").write("vexuscapital.com.br\n")
        print("Domínio: CNAME=vexuscapital.com.br + .nojekyll")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print("OK — tudo resolvido." if not faltas else f"{faltas} arquivo(s) com pendência.")

if __name__ == "__main__":
    main()
