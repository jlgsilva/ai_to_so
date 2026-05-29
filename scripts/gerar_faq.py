# =============================================================================
# gerar_faq.py
# AgroAssist IA — Geração de FAQ Sintética via Groq
#
# O que faz:
#   - Conecta na API Groq (gratuita)
#   - Gera pares pergunta/resposta para 5 categorias de seguro agrícola
#   - Salva em dados/faq_agricola.json  (usado pelo ingestao.py)
#   - Salva em dados/faq_agricola.txt   (leitura humana / backup)
#
# Como usar:
#   1. pip install groq
#   2. Defina sua chave: export GROQ_API_KEY="sua_chave"
#      OU edite GROQ_API_KEY abaixo direto (não suba no GitHub!)
#   3. python gerar_faq.py
#
# Chave gratuita em: https://console.groq.com
# =============================================================================

import os
import json
import time
from groq import Groq

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────

from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


MODEL        = "llama-3.1-8b-instant"   # gratuito e rápido
OUTPUT_JSON  = "dados/faq_agricola.json"
OUTPUT_TXT   = "dados/faq_agricola.txt"
QA_POR_LOTE  = 15   # perguntas geradas por chamada
PAUSA_API    = 2    # segundos entre chamadas (evita rate limit)

client = Groq(api_key=GROQ_API_KEY)

# ── CATEGORIAS E INSTRUÇÕES ───────────────────────────────────────────────────
CATEGORIAS = [
    {
        "nome": "Conceitos de Seguro Agrícola",
        "instrucao": (
            "Gere pares de pergunta e resposta sobre conceitos básicos de seguro agrícola no Brasil. "
            "Inclua temas como: o que é seguro agrícola, o que cobre, o que não cobre, como funciona "
            "a franquia, como é feita a vistoria de sinistro, tipos de cobertura (compreensiva, "
            "multirisco, paramétrico), período de carência, importância segurada, taxa de prêmio. "
            "As perguntas devem simular dúvidas reais de produtores rurais e corretores de seguros."
        ),
    },
    {
        "nome": "PROAGRO e PROAGRO Mais",
        "instrucao": (
            "Gere pares de pergunta e resposta sobre o PROAGRO e PROAGRO Mais no Brasil. "
            "Inclua: o que é o PROAGRO, quem pode contratar, quais culturas são cobertas, "
            "diferença entre PROAGRO e seguro rural privado, o que são perdas cobertas, "
            "como solicitar a cobertura, papel do banco financiador, PROAGRO Mais para "
            "agricultura familiar, prazos para comunicação de sinistro, como funciona a "
            "comissão técnica de avaliação (CTA)."
        ),
    },
    {
        "nome": "Subvenção ao Prêmio do Seguro Rural (PSR)",
        "instrucao": (
            "Gere pares de pergunta e resposta sobre o Programa de Subvenção ao Prêmio do "
            "Seguro Rural (PSR) do governo federal brasileiro. Inclua: o que é a subvenção, "
            "quem tem direito, como solicitar, quais culturas e regiões são contempladas, "
            "percentual de subvenção, diferença entre subvenção federal e estadual, papel "
            "do MAPA na gestão do programa, relação com o crédito rural, como o corretor "
            "deve orientar o produtor, prazos e limites anuais."
        ),
    },
    {
        "nome": "Sinistros no Seguro Agrícola",
        "instrucao": (
            "Gere pares de pergunta e resposta sobre o processo de sinistro em seguro agrícola "
            "no Brasil. Inclua: como abrir um sinistro, quais documentos são necessários, "
            "prazo para comunicar o sinistro à seguradora, como funciona a perícia / vistoria, "
            "o que é laudo de vistoria, como é calculada a indenização, o que pode levar à "
            "negativa do sinistro, diferença entre sinistro parcial e total, papel do corretor "
            "no processo de sinistro, sinistros por seca, granizo, geada e excesso de chuvas."
        ),
    },
    {
        "nome": "Crédito Rural e Seguro Obrigatório",
        "instrucao": (
            "Gere pares de pergunta e resposta sobre a relação entre crédito rural e seguro "
            "agrícola no Brasil. Inclua: quando o seguro é obrigatório no financiamento rural, "
            "o que diz o Manual de Crédito Rural (MCR) do Banco Central sobre seguros, "
            "diferença entre seguro de custeio e seguro de investimento, como o seguro protege "
            "o produtor e o banco, o que acontece se o produtor não contratar o seguro exigido, "
            "linhas de crédito (Pronaf, Pronamp, crédito comercial) e suas exigências de seguro, "
            "seguro de máquinas agrícolas e benfeitorias rurais como garantia."
        ),
    },
]

# ── PROMPT TEMPLATE ───────────────────────────────────────────────────────────
PROMPT_SISTEMA = """Você é um especialista sênior em seguros agrícolas e crédito rural no Brasil,
com mais de 20 anos de experiência em seguradoras, resseguradoras e no mercado de agronegócio.
Seu conhecimento inclui legislação brasileira, regulação da SUSEP, programas do MAPA e BACEN.

Sempre responda em português brasileiro claro e preciso.
Nunca invente coberturas, regras ou valores fictícios.
Quando houver variações entre seguradoras, mencione que os termos podem variar conforme a apólice."""

def gerar_lote(categoria: dict) -> list[dict]:
    """Gera um lote de pares Q&A para uma categoria."""
    prompt = f"""
{categoria['instrucao']}

Gere EXATAMENTE {QA_POR_LOTE} pares de pergunta e resposta.

REGRAS OBRIGATÓRIAS:
- As perguntas devem ser variadas (não repetir o mesmo tema)
- As respostas devem ter entre 3 e 8 linhas — completas, mas objetivas
- As respostas devem ser tecnicamente corretas e baseadas na realidade do mercado brasileiro
- Simule o tom de um assistente virtual de uma seguradora ou corretora
- NÃO use valores monetários específicos de prêmio (eles variam muito)

Responda SOMENTE com um array JSON válido, sem nenhum texto antes ou depois:
[
  {{
    "categoria": "{categoria['nome']}",
    "pergunta": "...",
    "resposta": "..."
  }},
  ...
]
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.4,
        max_tokens=4000,
    )

    texto = response.choices[0].message.content.strip()

    # Remove possíveis marcações markdown que o modelo insira
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
    texto = texto.strip()

    try:
        lote = json.loads(texto)
        return lote
    except json.JSONDecodeError as e:
        print(f"  ⚠️  Erro ao parsear JSON: {e}")
        print(f"  Trecho recebido: {texto[:300]}")
        return []


# ── EXECUÇÃO PRINCIPAL ────────────────────────────────────────────────────────
def main():
    os.makedirs("dados", exist_ok=True)

    todos_qa = []
    total_gerados = 0

    print("=" * 60)
    print("  AgroAssist IA — Geração de FAQ Sintética")
    print("=" * 60)

    for i, cat in enumerate(CATEGORIAS, 1):
        print(f"\n[{i}/{len(CATEGORIAS)}] Gerando: {cat['nome']} ...", end=" ", flush=True)

        lote = gerar_lote(cat)

        if lote:
            todos_qa.extend(lote)
            total_gerados += len(lote)
            print(f"✅  {len(lote)} pares gerados")
        else:
            print("❌  Falhou — verifique a saída acima")

        if i < len(CATEGORIAS):
            time.sleep(PAUSA_API)

    # ── Salvar JSON ───────────────────────────────────────────────────────────
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(todos_qa, f, ensure_ascii=False, indent=2)
    print(f"\n✅  JSON salvo em: {OUTPUT_JSON}  ({total_gerados} pares)")

    # ── Salvar TXT (leitura humana) ───────────────────────────────────────────
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write("AgroAssist IA — FAQ de Seguro Agrícola\n")
        f.write("Gerado automaticamente via LLM. Revise antes de usar em produção.\n")
        f.write("=" * 60 + "\n\n")

        categoria_atual = ""
        for item in todos_qa:
            if item.get("categoria") != categoria_atual:
                categoria_atual = item.get("categoria", "")
                f.write(f"\n{'='*60}\n")
                f.write(f"  {categoria_atual.upper()}\n")
                f.write(f"{'='*60}\n\n")

            f.write(f"P: {item['pergunta']}\n")
            f.write(f"R: {item['resposta']}\n\n")

    print(f"✅  TXT  salvo em: {OUTPUT_TXT}")

    # ── Estatísticas ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Total de pares Q&A gerados: {total_gerados}")
    print(f"  Categorias cobertas:        {len(CATEGORIAS)}")
    print("\n  PRÓXIMO PASSO:")
    print("  Abra dados/faq_agricola.txt, revise as respostas")
    print("  e corrija qualquer imprecisão com seu conhecimento")
    print("  de especialista antes de rodar ingestao.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
