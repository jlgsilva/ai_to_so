# =============================================================================
# app.py
# AgroAssist IA — Interface Streamlit
#
# Como rodar localmente:
#   streamlit run app.py
#
# Requer:
#   - vectordb/faiss_index/ gerado pelo ingestao.py
#   - .env com GROQ_API_KEY=...
#   - pip install streamlit langchain-community langchain-core
#                langchain-huggingface faiss-cpu sentence-transformers
#                groq python-dotenv
# =============================================================================

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# ── CONSTANTES ────────────────────────────────────────────────────────────────
GROQ_API_KEY    = os.environ.get("GROQ_API_KEY")
MODEL           = "llama-3.1-8b-instant"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VECTORDB_PATH   = "vectordb/faiss_index"
K_RETRIEVAL     = 6      # chunks recuperados por consulta
MAX_HIST        = 6      # mensagens do histórico enviadas ao LLM (3 trocas)
MAX_TOKENS      = 900

# Fontes com nome amigável para exibição
FONTES_AMIGAVEIS = {
    "lei_10823_2003.pdf":                                          "Lei 10.823/2003",
    "resolucao_cmn_4902_2021.pdf":                                 "Resolução CMN 4.902/2021",
    "resolucao_cmn_5220_2025.pdf":                                 "Resolução CMN 5.220/2025",
    "Res_4418_v2_L.pdf":                                           "Resolução BACEN 4.418 (PROAGRO)",
    "Guia-dos-Seguros-Rurais-205x275cm-WEB_200228_211105.pdf":     "Guia dos Seguros Rurais — CNA/MAPA",
    "Manual de Comercialização Agrícola_v1_200506.pdf":            "Manual de Comercialização Agrícola — Swiss Re",
    "2021-leila-harfuch-seguro-rural-no-mundo-e-alternativas-para-o-brasil.pdf": "Seguro Rural no Mundo — Estudo Técnico",
    "Boletim-IRBMercado-Dezembro-Final.pdf":                       "Boletim IRB+ Mercado",
    "DOC-Autógrafo - Projeto de Lei-20100806.pdf":                 "Projeto de Lei — Fundo de Cobertura Suplementar",
    "requisitos-basicos-para-capacitacao-de-peritos-rurais-vol-1-1.pdf": "Capacitação de Peritos Rurais — Manual",
    "seer236_p,+RPA+2+2023_+8+Modelagens-atuariais-seguro-agricola.pdf": "Modelagens Atuariais — Seguro Agrícola",
    "faq_agricola.json":                                           "Base de Conhecimento AgroAssist",
    "faq_agricola.txt":                                            "Base de Conhecimento AgroAssist",
}

# ── PROMPTS ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é AgroAssist IA, assistente virtual especializado em seguros agrícolas, \
seguro rural e crédito rural no Brasil.

Seu perfil:
- Conhecimento técnico profundo em: seguro agrícola, PROAGRO, PSR (Programa de Subvenção ao Prêmio), \
sinistros rurais, crédito rural, seguro paramétrico, seguro de máquinas agrícolas e benfeitorias rurais.
- Tom: profissional, claro e acessível — tanto para produtores rurais quanto para corretores e técnicos.
- Idioma: sempre português brasileiro.

Regras obrigatórias:
1. Use APENAS o contexto fornecido para embasar as respostas. Nunca invente coberturas, \
valores, prazos ou regras que não estejam no contexto.
2. Se o contexto não contiver a informação necessária, diga claramente: \
"Não encontrei essa informação na minha base de conhecimento. Recomendo consultar um corretor \
de seguros habilitado ou o site do MAPA (gov.br/agricultura)."
3. Ao final de cada resposta, cite as fontes usadas no formato: "📚 Fontes: [nome da fonte]"
4. Nunca afirme que uma apólice específica cobre ou não cobre algo — \
as coberturas variam por seguradora e apólice. Sempre oriente o usuário a verificar as condições gerais.
5. Para solicitações de cotação ou abertura de sinistro, colete as informações necessárias \
passo a passo antes de orientar.

CONTEXTO RECUPERADO:
{contexto}
"""

# ── CLASSIFICADOR DE INTENÇÃO ─────────────────────────────────────────────────
INTENCOES = {
    "sinistro": [
        "sinistro", "abrir sinistro", "comunicar sinistro", "perda", "perdeu",
        "granizo", "geada", "seca", "inundação", "enchente", "queimada",
        "destruiu", "danificou", "perito", "vistoria", "indenização",
    ],
    "cotacao": [
        "cotação", "cotar", "contratar", "quero seguro", "quanto custa",
        "valor do seguro", "prêmio", "fazer seguro", "preciso de seguro",
    ],
    "fora_escopo": [
        "seguro de vida", "seguro saúde", "seguro auto", "seguro residencial",
        "plano de saúde", "seguro viagem", "previdência",
    ],
}

def classificar_intencao(texto: str) -> str:
    texto_lower = texto.lower()
    for intencao, palavras in INTENCOES.items():
        if any(p in texto_lower for p in palavras):
            return intencao
    return "duvida_geral"


# ── FLUXOS GUIADOS ────────────────────────────────────────────────────────────
FLUXO_SINISTRO = """O usuário quer abrir ou saber sobre um sinistro agrícola.
Responda de forma acolhedora e colete as informações necessárias passo a passo:
1. Qual cultura/produto foi afetado?
2. Qual foi o evento causador (granizo, seca, geada, excesso de chuva, etc.)?
3. O produtor possui apólice de seguro ou está vinculado ao PROAGRO?
4. Já comunicou à seguradora/banco? Em que data ocorreu o evento?

Após coletar, oriente sobre os próximos passos com base no contexto recuperado.
Lembre que o prazo de comunicação de sinistro é crítico — reforce isso."""

FLUXO_COTACAO = """O usuário quer cotar ou contratar um seguro agrícola.
Colete as informações necessárias passo a passo:
1. Qual cultura deseja segurar?
2. Em qual município/estado está a propriedade?
3. Qual é a área aproximada (hectares)?
4. Já possui financiamento rural (custeio)?

Após coletar, oriente sobre tipos de cobertura disponíveis e recomende que entre em contato \
com um corretor habilitado para obter cotação formal. Use o contexto recuperado para enriquecer."""

FLUXO_FORA_ESCOPO = """O usuário perguntou sobre um tipo de seguro fora do escopo do AgroAssist IA \
(seguros não agrícolas/rurais).
Responda com cordialidade, explique que você é especializado em seguros agrícolas e rurais, \
e ofereça ajuda dentro desse escopo."""


def montar_instrucao_fluxo(intencao: str) -> str:
    if intencao == "sinistro":
        return FLUXO_SINISTRO
    elif intencao == "cotacao":
        return FLUXO_COTACAO
    elif intencao == "fora_escopo":
        return FLUXO_FORA_ESCOPO
    return ""  # duvida_geral: só usa RAG + system prompt padrão


# ── CARREGAMENTO DO ÍNDICE ────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Carregando base de conhecimento...")
def carregar_retriever():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectordb = FAISS.load_local(
        VECTORDB_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectordb.as_retriever(search_kwargs={"k": K_RETRIEVAL})


def formatar_fontes(docs) -> str:
    """Extrai fontes únicas e retorna string formatada."""
    fontes_vistas = []
    for doc in docs:
        raw = doc.metadata.get("fonte", "")
        amigavel = FONTES_AMIGAVEIS.get(raw, raw)
        if amigavel and amigavel not in fontes_vistas:
            fontes_vistas.append(amigavel)
    if not fontes_vistas:
        return ""
    return "📚 **Fontes:** " + " · ".join(fontes_vistas)


# ── INTERFACE ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroAssist IA",
    page_icon="🌾",
    layout="centered",
)

# Cabeçalho
st.markdown("""
<div style='text-align:center; padding: 1rem 0 0.5rem 0'>
    <h1 style='font-size:2.2rem; margin-bottom:0'>🌾 AgroAssist IA</h1>
    <p style='color:gray; margin-top:0.3rem'>
        Assistente especializado em Seguro Agrícola · Seguro Rural · Crédito Rural
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Tópicos de exemplo (clicáveis)
with st.expander("💡 Exemplos de perguntas — clique para expandir"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - O que é o PSR e quem tem direito?
        - Como funciona o PROAGRO?
        - Quais culturas têm cobertura no seguro rural?
        - O que é seguro paramétrico?
        """)
    with col2:
        st.markdown("""
        - Perdi minha lavoura de soja por granizo. O que fazer?
        - Quero cotar seguro para milho em MT
        - Qual o prazo para comunicar um sinistro?
        - O seguro é obrigatório no crédito rural?
        """)

# Histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensagem de boas-vindas
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Olá! Sou o **AgroAssist IA**, seu assistente especializado em seguros agrícolas "
            "e crédito rural no Brasil. 🌾\n\n"
            "Posso te ajudar com dúvidas sobre **seguro agrícola, PROAGRO, subvenção ao prêmio (PSR), "
            "sinistros rurais, crédito rural** e muito mais.\n\n"
            "Como posso te ajudar hoje?"
        ),
        "fontes": "",
    })

# Renderizar histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("fontes"):
            st.caption(msg["fontes"])

# ── INPUT DO USUÁRIO ──────────────────────────────────────────────────────────
if prompt := st.chat_input("Digite sua dúvida sobre seguro agrícola..."):

    # Exibir mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt, "fontes": ""})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Classificar intenção
    intencao = classificar_intencao(prompt)

    # Recuperar contexto RAG
    retriever = carregar_retriever()
    docs_relevantes = retriever.invoke(prompt)
    contexto = "\n\n---\n\n".join([
        f"[Fonte: {doc.metadata.get('fonte', 'desconhecida')}]\n{doc.page_content}"
        for doc in docs_relevantes
    ])

    # Montar instrução de fluxo (se aplicável)
    instrucao_fluxo = montar_instrucao_fluxo(intencao)
    system_final = SYSTEM_PROMPT.format(contexto=contexto)
    if instrucao_fluxo:
        system_final += f"\n\nINSTRUÇÃO DE FLUXO:\n{instrucao_fluxo}"

    # Montar histórico para a API (últimas MAX_HIST mensagens)
    historico_api = [{"role": "system", "content": system_final}]
    for m in st.session_state.messages[-MAX_HIST:]:
        if m["role"] in ("user", "assistant"):
            historico_api.append({"role": m["role"], "content": m["content"]})

    # Chamada ao LLM
    with st.chat_message("assistant"):
        with st.spinner("Consultando base de conhecimento..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=historico_api,
                    temperature=0.2,
                    max_tokens=MAX_TOKENS,
                )
                resposta = response.choices[0].message.content
                fontes_str = formatar_fontes(docs_relevantes)

                st.markdown(resposta)
                if fontes_str:
                    st.caption(fontes_str)

            except Exception as e:
                resposta = (
                    "Desculpe, ocorreu um erro ao processar sua pergunta. "
                    f"Detalhes: {str(e)}"
                )
                fontes_str = ""
                st.error(resposta)

    # Salvar no histórico
    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta,
        "fontes": fontes_str,
    })

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ AgroAssist IA é um assistente informativo. "
    "As respostas não substituem a orientação de um corretor de seguros habilitado "
    "ou consulta às condições gerais da apólice. "
    "Para contratação, acione um profissional credenciado pela SUSEP."
)
