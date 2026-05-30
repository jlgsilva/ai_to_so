# =============================================================================
# gerar_relatorio_html.py
# Junta README.md + EVIDENCIAS.md num HTML completo com imagens embutidas.
# Abra o HTML no Chrome e Ctrl+P → Salvar como PDF.
#
# pip install markdown2
# %run gerar_relatorio_html.py
# =============================================================================

import base64, re, markdown2
from pathlib import Path

BASE_DIR    = Path(__file__).parent
OUTPUT_HTML = BASE_DIR / "Relatorio_AgroAssist_IA.html"

MD_FILES = [
    BASE_DIR / "README.md",
    BASE_DIR / "evidencias" / "EVIDENCIAS.md",
]

# ── Embutir imagens como base64 ───────────────────────────────────────────────
def embutir_imagens(html: str, md_dir: Path) -> str:
    def sub(m):
        src = m.group(1)
        if src.startswith("http"):
            return m.group(0)
        p = (md_dir / src).resolve()
        if not p.exists():
            return m.group(0)
        ext  = p.suffix.lower().lstrip(".")
        mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png","gif":"gif","webp":"webp"}.get(ext,"png")
        b64  = base64.b64encode(p.read_bytes()).decode()
        return f'src="data:image/{mime};base64,{b64}"'
    return re.sub(r'src="([^"]+)"', sub, html)

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 11pt;
    color: #2c2c2a;
    line-height: 1.7;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 50px;
  }
  h1 { font-size: 22pt; color: #1d6b3c; border-bottom: 2px solid #1d6b3c;
       padding-bottom: 6px; margin: 32px 0 12px; }
  h2 { font-size: 14pt; color: #1d6b3c; margin: 24px 0 8px; }
  h3 { font-size: 12pt; color: #444; margin: 18px 0 6px; }
  h4 { font-size: 11pt; color: #444; margin: 14px 0 4px; }
  p  { margin: 0 0 10px; text-align: justify; }
  ul, ol { margin: 6px 0 10px 24px; }
  li { margin-bottom: 4px; }
  table {
    width: 100%; border-collapse: collapse;
    margin: 14px 0; font-size: 9.5pt;
    page-break-inside: avoid;
  }
  thead tr { background: #1d6b3c; color: #fff; }
  th { padding: 6px 8px; text-align: left; font-weight: 600; }
  td { padding: 5px 8px; border-bottom: 1px solid #d3d1c7; vertical-align: top; }
  tr:nth-child(even) td { background: #e8f5ee; }
  img {
    max-width: 100%; height: auto;
    display: block; margin: 12px auto;
    border: 1px solid #d3d1c7; border-radius: 4px;
    page-break-inside: avoid;
  }
  pre  { background: #f1efe8; padding: 12px; border-radius: 4px;
         font-size: 8.5pt; overflow-x: auto; margin: 10px 0;
         page-break-inside: avoid; }
  code { font-family: monospace; font-size: 9pt;
         background: #f1efe8; padding: 1px 4px; border-radius: 3px; }
  pre code { background: none; padding: 0; }
  blockquote {
    border-left: 3px solid #1d6b3c; margin: 10px 0;
    padding: 8px 14px; background: #e8f5ee; border-radius: 0 4px 4px 0;
  }
  hr { border: none; border-top: 1px solid #d3d1c7; margin: 20px 0; }
  a  { color: #185fa5; }

  /* Capa */
  .capa {
    text-align: center; padding: 80px 0 60px;
    border-bottom: 2px solid #1d6b3c; margin-bottom: 40px;
  }
  .capa h1 { border: none; font-size: 28pt; margin: 0 0 12px; }
  .capa .sub { font-size: 14pt; color: #444; margin: 0 0 24px; }
  .capa .meta { font-size: 10pt; color: #888; line-height: 2; }

  /* Separador entre documentos */
  .doc-break { page-break-before: always; }

  /* Impressão */
  @media print {
    body { padding: 0; max-width: 100%; }
    h1, h2, h3 { page-break-after: avoid; }
    img { page-break-inside: avoid; }
    a  { color: inherit; text-decoration: none; }
  }
"""

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  AgroAssist IA — Gerando HTML para PDF")
    print("=" * 55)

    partes_html = []

    # Capa
    partes_html.append("""
    <div class="capa">
      <h1>🌾 AgroAssist IA</h1>
      <p class="sub">Assistente Virtual Especializado em<br>
         Seguro Agrícola e Crédito Rural</p>
      <hr style="width:200px;margin:20px auto;border-color:#1d6b3c">
      <div class="meta">
        Relatório de Experimento — Prova de Conceito (PoC)<br>
        InsurMinds | Inteligência Artificial Aplicada a Seguros<br>
        I2A2 – Instituto de Inteligência Artificial Aplicada<br><br>
        <strong>Autor:</strong> Jefferson L. G. Silva<br>
        <strong>Repositório:</strong> github.com/jlgsilva/ai_to_so<br>
        <strong>Demo:</strong> agro-assist-seguro-rural.streamlit.app
      </div>
    </div>
    """)

    for i, md_path in enumerate(MD_FILES):
        if not md_path.exists():
            print(f"  Nao encontrado: {md_path}")
            continue
        print(f"  Processando: {md_path.name} ...", end=" ")

        texto = md_path.read_text(encoding="utf-8")

        # Remove badges ([![...][...])
        texto = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', texto)

        html = markdown2.markdown(texto, extras=[
            "tables", "fenced-code-blocks", "strike",
            "break-on-newline", "header-ids",
        ])

        # Embutir imagens
        html = embutir_imagens(html, md_path.parent)

        # Separador de página entre documentos
        if i > 0:
            partes_html.append('<div class="doc-break"></div>')

        partes_html.append(html)
        print("ok")

    # Montar HTML final
    html_final = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width">
  <title>AgroAssist IA — Relatório</title>
  <style>{CSS}</style>
</head>
<body>
  {''.join(partes_html)}
</body>
</html>"""

    OUTPUT_HTML.write_text(html_final, encoding="utf-8")

    print(f"\n  HTML gerado: {OUTPUT_HTML}")
    print(f"\n  PROXIMO PASSO:")
    print(f"  1. Abra o arquivo no Chrome")
    print(f"  2. Ctrl+P (ou Cmd+P no Mac)")
    print(f"  3. Destino: 'Salvar como PDF'")
    print(f"  4. Layout: Retrato | Margens: Padrao")
    print(f"  5. Clique em Salvar")
    print("=" * 55)


if __name__ == "__main__":
    main()
