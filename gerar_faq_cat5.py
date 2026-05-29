# =============================================================================
# gerar_faq_cat5.py
# Gera APENAS a categoria 5 (Crédito Rural) que falhou por rate limit
# e ADICIONA ao arquivo faq_agricola.json existente
# =============================================================================

import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL        = "llama-3.1-8b-instant"
OUTPUT_JSON  = "dados/faq_agricola.json"
OUTPUT_TXT   = "dados/faq_agricola.txt"

client = Groq(api_key=GROQ_API_KEY)

PROMPT_SISTEMA = """Você é um especialista sênior em seguros agrícolas e crédito rural no Brasil,
com mais de 20 anos de experiência em seguradoras, resseguradoras e no mercado de agronegócio.
Sempre responda em português brasileiro claro e preciso.
Nunca invente coberturas, regras ou valores fictícios."""

CATEGORIA_5 = {
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
}

def gerar_com_retry(categoria, tentativas=3, pausa_inicial=15):
    """Tenta gerar com pausa progressiva em caso de rate limit."""
    for tentativa in range(1, tentativas + 1):
        try:
            print(f"  Tentativa {tentativa}/{tentativas} ...", end=" ", flush=True)

            prompt = f"""
{categoria['instrucao']}

Gere EXATAMENTE 15 pares de pergunta e resposta.

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
  }}
]
"""
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.4,
                max_tokens=3000,   # reduzido para caber no limite de TPM
            )

            texto = response.choices[0].message.content.strip()

            if texto.startswith("```"):
                texto = texto.split("```")[1]
                if texto.startswith("json"):
                    texto = texto[4:]
            texto = texto.strip()

            lote = json.loads(texto)
            print(f"✅  {len(lote)} pares gerados")
            return lote

        except Exception as e:
            msg = str(e)
            if "rate_limit" in msg or "429" in msg:
                espera = pausa_inicial * tentativa
                print(f"⏳  Rate limit — aguardando {espera}s...")
                time.sleep(espera)
            else:
                print(f"❌  Erro inesperado: {msg}")
                return []

    print("❌  Todas as tentativas falharam.")
    return []


def main():
    # Aguarda 20s para o rate limit resetar antes de começar
    print("Aguardando 20s para o rate limit resetar...", end=" ", flush=True)
    time.sleep(20)
    print("ok\n")

    print(f"Gerando: {CATEGORIA_5['nome']}")
    lote = gerar_com_retry(CATEGORIA_5)

    if not lote:
        print("Não foi possível gerar. Tente novamente em alguns minutos.")
        return

    # ── Carregar JSON existente e adicionar ──────────────────────────────────
    qa_existente = []
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            qa_existente = json.load(f)
        print(f"JSON existente carregado: {len(qa_existente)} pares")

    qa_total = qa_existente + lote

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(qa_total, f, ensure_ascii=False, indent=2)
    print(f"✅  JSON atualizado: {len(qa_total)} pares totais → {OUTPUT_JSON}")

    # ── Atualizar TXT ────────────────────────────────────────────────────────
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write("AgroAssist IA — FAQ de Seguro Agrícola\n")
        f.write("Gerado automaticamente via LLM. Revise antes de usar em produção.\n")
        f.write("=" * 60 + "\n\n")

        categoria_atual = ""
        for item in qa_total:
            if item.get("categoria") != categoria_atual:
                categoria_atual = item.get("categoria", "")
                f.write(f"\n{'='*60}\n")
                f.write(f"  {categoria_atual.upper()}\n")
                f.write(f"{'='*60}\n\n")
            f.write(f"P: {item['pergunta']}\n")
            f.write(f"R: {item['resposta']}\n\n")

    print(f"✅  TXT  atualizado → {OUTPUT_TXT}")
    print(f"\n  Total final: {len(qa_total)} pares Q&A em 5 categorias")
    print("\n  PRÓXIMO PASSO: revise dados/faq_agricola.txt e rode ingestao.py")


if __name__ == "__main__":
    main()