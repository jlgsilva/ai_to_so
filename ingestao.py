# =============================================================================
# ingestao.py
# AgroAssist IA — Pipeline de Ingestão RAG
#
# O que faz:
#   1. Carrega PDFs oficiais (MAPA, BACEN, Embrapa, etc.)
#   2. Carrega FAQ sintética (faq_agricola.json)
#   3. Divide em chunks com overlap
#   4. Gera embeddings multilíngues (local, gratuito)
#   5. Salva índice FAISS em vectordb/
#
# Como usar:
#   1. pip install langchain langchain-community faiss-cpu
#                  sentence-transformers pypdf python-dotenv
#   2. Coloque os PDFs em dados/
#   3. python ingestao.py
#
# Resultado: vectordb/faiss_index  (pasta com index.faiss + index.pkl)
# =============================================================================

import os
import json
import pickle
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# LangChain
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────
PASTA_DADOS     = Path("dados")
PASTA_VECTORDB  = Path("vectordb")
INDICE_NOME     = "faiss_index"

# Modelo de embedding: multilíngue, gratuito, bom em PT-BR
# ~120MB no primeiro uso (baixa automaticamente)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Chunking
CHUNK_SIZE      = 800
CHUNK_OVERLAP   = 100

# ── FUNÇÕES DE CARREGAMENTO ───────────────────────────────────────────────────

def carregar_pdfs(pasta: Path) -> list[Document]:
    """Carrega todos os PDFs da pasta dados/."""
    docs = []
    pdfs = list(pasta.glob("*.pdf"))

    if not pdfs:
        print("  ⚠️  Nenhum PDF encontrado em dados/ — pulando PDFs.")
        return docs

    for pdf_path in pdfs:
        print(f"  📄 Carregando: {pdf_path.name} ...", end=" ", flush=True)
        try:
            loader = PyPDFLoader(str(pdf_path))
            paginas = loader.load()
            # Adiciona metadado de fonte
            for p in paginas:
                p.metadata["fonte"]    = pdf_path.name
                p.metadata["tipo"]     = "documento_oficial"
            docs.extend(paginas)
            print(f"✅  {len(paginas)} páginas")
        except Exception as e:
            print(f"❌  Erro: {e}")

    return docs


def carregar_faq(pasta: Path) -> list[Document]:
    """Carrega faq_agricola.json e converte em Documents."""
    faq_path = pasta / "faq_agricola.json"

    if not faq_path.exists():
        print("  ⚠️  faq_agricola.json não encontrado — pulando FAQ.")
        return []

    print(f"  📋 Carregando: faq_agricola.json ...", end=" ", flush=True)

    with open(faq_path, "r", encoding="utf-8") as f:
        itens = json.load(f)

    docs = []
    for item in itens:
        # Formata Q&A como texto corrido — melhora recuperação semântica
        conteudo = (
            f"Pergunta: {item['pergunta']}\n"
            f"Resposta: {item['resposta']}"
        )
        doc = Document(
            page_content=conteudo,
            metadata={
                "fonte":     "faq_agricola.json",
                "tipo":      "faq_sintetica",
                "categoria": item.get("categoria", "geral"),
                "pergunta":  item["pergunta"],   # facilita debug
            }
        )
        docs.append(doc)

    print(f"✅  {len(docs)} pares Q&A")
    return docs


def carregar_txts(pasta: Path) -> list[Document]:
    """Carrega arquivos .txt adicionais da pasta dados/ (exceto README)."""
    docs = []
    txts = [p for p in pasta.glob("*.txt") if "readme" not in p.name.lower()]

    for txt_path in txts:
        print(f"  📝 Carregando: {txt_path.name} ...", end=" ", flush=True)
        try:
            texto = txt_path.read_text(encoding="utf-8")
            doc = Document(
                page_content=texto,
                metadata={
                    "fonte": txt_path.name,
                    "tipo":  "texto_adicional",
                }
            )
            docs.append(doc)
            print("✅")
        except Exception as e:
            print(f"❌  Erro: {e}")

    return docs


# ── CHUNKING ──────────────────────────────────────────────────────────────────

def dividir_em_chunks(docs: list[Document]) -> list[Document]:
    """
    Divide documentos longos em chunks menores com overlap.
    FAQs já são pequenas — o splitter as mantém intactas.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(docs)

    # Garante que chunks de FAQ não percam o metadado de pergunta
    for chunk in chunks:
        if "pergunta" not in chunk.metadata:
            chunk.metadata["pergunta"] = ""

    return chunks


# ── EMBEDDINGS + FAISS ────────────────────────────────────────────────────────

def criar_indice(chunks: list[Document]) -> FAISS:
    """Gera embeddings e cria índice FAISS."""
    print(f"\n  🔄 Carregando modelo de embedding: {EMBEDDING_MODEL}")
    print("     (pode demorar ~1 min no primeiro uso — baixa ~120MB)")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"  ⚙️  Gerando embeddings para {len(chunks)} chunks...", end=" ", flush=True)
    t0 = time.time()
    vectordb = FAISS.from_documents(chunks, embeddings)
    t1 = time.time()
    print(f"✅  {t1-t0:.1f}s")

    return vectordb


def salvar_indice(vectordb: FAISS, pasta: Path, nome: str):
    """Salva índice FAISS localmente."""
    pasta.mkdir(parents=True, exist_ok=True)
    vectordb.save_local(str(pasta / nome))
    print(f"  💾 Índice salvo em: {pasta / nome}/")


def salvar_metadata(chunks: list[Document], pasta: Path):
    """
    Salva metadados dos chunks em JSON — útil para debug e
    para citar fontes no chatbot.
    """
    meta_path = pasta / "chunks_metadata.json"
    meta = [
        {
            "indice":    i,
            "fonte":     c.metadata.get("fonte", ""),
            "tipo":      c.metadata.get("tipo", ""),
            "categoria": c.metadata.get("categoria", ""),
            "tamanho":   len(c.page_content),
            "preview":   c.page_content[:120].replace("\n", " "),
        }
        for i, c in enumerate(chunks)
    ]
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  📊 Metadados salvos em: {meta_path}")


# ── TESTE RÁPIDO ──────────────────────────────────────────────────────────────

def testar_indice(pasta: Path, nome: str):
    """
    Carrega o índice recém-criado e faz 3 buscas de teste
    para confirmar que está funcionando.
    """
    print("\n" + "─" * 60)
    print("  🧪 TESTE RÁPIDO DO ÍNDICE")
    print("─" * 60)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vectordb = FAISS.load_local(
        str(pasta / nome),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})

    perguntas_teste = [
        "O que é seguro agrícola?",
        "Como funciona o PROAGRO?",
        "Quais documentos preciso para abrir um sinistro?",
    ]

    for pergunta in perguntas_teste:
        print(f"\n  Q: {pergunta}")
        resultados = retriever.invoke(pergunta)
        for j, doc in enumerate(resultados, 1):
            fonte = doc.metadata.get("fonte", "desconhecida")
            preview = doc.page_content[:100].replace("\n", " ")
            print(f"     [{j}] ({fonte}) {preview}...")


# ── EXECUÇÃO PRINCIPAL ────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AgroAssist IA — Pipeline de Ingestão RAG")
    print("=" * 60)

    # 1. Carregamento
    print("\n📂 CARREGANDO DOCUMENTOS")
    print("─" * 60)
    docs_pdf  = carregar_pdfs(PASTA_DADOS)
    docs_faq  = carregar_faq(PASTA_DADOS)
    docs_txt  = carregar_txts(PASTA_DADOS)

    todos_docs = docs_pdf + docs_faq + docs_txt

    if not todos_docs:
        print("\n❌ Nenhum documento carregado. Verifique a pasta dados/")
        return

    print(f"\n  Total carregado: {len(todos_docs)} documentos/páginas")

    # 2. Chunking
    print("\n✂️  DIVIDINDO EM CHUNKS")
    print("─" * 60)
    chunks = dividir_em_chunks(todos_docs)
    print(f"  Total de chunks: {len(chunks)}")

    # Estatísticas por fonte
    fontes = {}
    for c in chunks:
        f = c.metadata.get("fonte", "desconhecida")
        fontes[f] = fontes.get(f, 0) + 1
    print("  Distribuição por fonte:")
    for fonte, qtd in sorted(fontes.items()):
        print(f"    • {fonte}: {qtd} chunks")

    # 3. Embeddings + FAISS
    print("\n🔢 GERANDO EMBEDDINGS E ÍNDICE FAISS")
    print("─" * 60)
    vectordb = criar_indice(chunks)

    # 4. Salvar
    print("\n💾 SALVANDO")
    print("─" * 60)
    salvar_indice(vectordb, PASTA_VECTORDB, INDICE_NOME)
    salvar_metadata(chunks, PASTA_VECTORDB)

    # 5. Teste
    testar_indice(PASTA_VECTORDB, INDICE_NOME)

    # 6. Resumo final
    print("\n" + "=" * 60)
    print("  ✅ INGESTÃO CONCLUÍDA COM SUCESSO")
    print("=" * 60)
    print(f"  Documentos carregados : {len(todos_docs)}")
    print(f"  Chunks gerados        : {len(chunks)}")
    print(f"  Índice salvo em       : {PASTA_VECTORDB / INDICE_NOME}/")
    print()
    print("  PRÓXIMO PASSO:")
    print("  Rode app.py para iniciar o chatbot localmente:")
    print("  > streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
