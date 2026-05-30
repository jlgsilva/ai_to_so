# 🌾 AgroAssist IA
### Assistente Virtual Especializado em Seguro Agrícola e Crédito Rural

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agro-assist-seguro-rural.streamlit.app/)

> **Acesse o chatbot online:** https://agro-assist-seguro-rural.streamlit.app/

---

## 📋 Sobre o Projeto

O **AgroAssist IA** é um chatbot de atendimento baseado em Inteligência Artificial, desenvolvido como Prova de Conceito (PoC) para o desafio do programa **InsurMinds | Inteligência Artificial Aplicada a Seguros** (I2A2 / Latin Re / Grupo FIT).

O assistente foi projetado para **automatizar o atendimento de primeiro nível** no segmento de seguros agrícolas e crédito rural no Brasil, respondendo perguntas frequentes de produtores rurais, corretores e técnicos agrícolas com base em documentação oficial e técnica.

### Diferencial de Especialização

Enquanto a maioria das soluções de chatbot para seguros aborda o setor de forma genérica, o AgroAssist IA foca exclusivamente no **agronegócio brasileiro**, contemplando:

- Seguro Agrícola (multirisco, compreensivo, paramétrico)
- PROAGRO e PROAGRO Mais
- Programa de Subvenção ao Prêmio do Seguro Rural (PSR)
- Seguro de Máquinas Agrícolas e Benfeitorias Rurais
- Crédito Rural e obrigatoriedade do seguro
- Sinistros rurais: abertura, perícia e indenização

---

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────┐
│                        USUÁRIO                              │
│              (Produtor / Corretor / Técnico)                │
└─────────────────────┬───────────────────────────────────────┘
                      │ Pergunta em linguagem natural
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   STREAMLIT (Frontend)                      │
│              Interface conversacional web                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            CLASSIFICADOR DE INTENÇÃO                        │
│  ┌─────────────┬──────────────┬────────────┬─────────────┐  │
│  │   SINISTRO  │   COTAÇÃO    │  DÚVIDA    │FORA ESCOPO │  │
│  │(fluxo guia- │(fluxo guia-  │  GERAL     │(redirecion.)│  │
│  │  do/coleta) │  do/coleta)  │   (RAG)    │             │  │
│  └──────┬──────┴──────┬───────┴─────┬──────┴─────────────┘  │
└─────────│─────────────│─────────────│───────────────────────┘
          │             │             │
          └─────────────┴─────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE                             │
│                                                             │
│   Query → HuggingFace Embeddings → FAISS Retriever         │
│         (paraphrase-multilingual-MiniLM-L12-v2)            │
│                        │                                    │
│                        ▼                                    │
│              Top-K Chunks Relevantes (k=6)                  │
│              + Metadados de Fonte                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ Contexto recuperado
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  LLM — Groq API                             │
│            (LLaMA 3.1 8B Instant)                           │
│                                                             │
│  System Prompt + Contexto RAG + Histórico + Guardrails      │
└─────────────────────┬───────────────────────────────────────┘
                      │ Resposta gerada + Citação de fonte
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      USUÁRIO                                │
│         Resposta contextualizada + Fonte citada             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxos Conversacionais

O AgroAssist IA implementa **4 fluxos distintos** de atendimento:

| Fluxo | Gatilho | Comportamento |
|---|---|---|
| **Sinistro** | Palavras-chave: granizo, seca, geada, perda, sinistro... | Coleta guiada: cultura afetada → evento → apólice/PROAGRO → data → orienta próximos passos |
| **Cotação** | Palavras-chave: cotar, contratar, quero seguro, quanto custa... | Coleta guiada: cultura → município/UF → área (ha) → financiamento → encaminha para corretor |
| **Dúvida Geral** | Qualquer pergunta informativa | Busca RAG → LLM responde com base nos documentos + cita fonte |
| **Fora de Escopo** | Seguro auto, saúde, vida, residencial... | Informa escopo do assistente e oferece ajuda dentro da especialidade |

---

## 📚 Base de Conhecimento

### Documentos Oficiais e Técnicos

| Documento | Tipo | Chunks |
|---|---|---|
| Requisitos Básicos para Capacitação de Peritos Rurais | Manual Técnico | 341 |
| Seguro Rural no Mundo e Alternativas para o Brasil | Estudo Acadêmico | 195 |
| Guia dos Seguros Rurais — CNA/MAPA | Guia Oficial | 118 |
| Resolução BACEN 4.418 (PROAGRO) | Regulação | 109 |
| Modelagens Atuariais — Seguro Agrícola | Artigo Científico | 105 |
| Manual de Comercialização Agrícola — Swiss Re | Manual Técnico | 102 |
| Boletim IRB+ Mercado — Dezembro | Boletim Setorial | 73 |
| Projeto de Lei — Fundo de Cobertura Suplementar | Legislação | 38 |
| Lei 10.823/2003 (PSR) | Legislação | — |
| Resolução CMN 4.902/2021 | Regulação | — |
| Resolução CMN 5.220/2025 | Regulação | — |
| FAQ Sintética AgroAssist (gerada via LLM + revisão especialista) | Base Q&A | 16 |

**Total: 375 páginas → 1.106 chunks indexados**

### Metodologia de Construção da Base

1. **Coleta:** documentos oficiais públicos (MAPA, BACEN, IRB+, legislação federal)
2. **Geração sintética:** FAQ gerada via LLaMA 3.1, organizada em 5 categorias temáticas: Conceitos de Seguro Agrícola, PROAGRO e PROAGRO Mais, Subvenção ao Prêmio (PSR), Sinistros e Crédito Rural
3. **Curadoria humana:** revisão por especialista em seguro agrícola e crédito rural — garantindo precisão técnica e aderência à regulação brasileira
4. **Chunking:** `RecursiveCharacterTextSplitter` com `chunk_size=800`, `chunk_overlap=100`
5. **Indexação:** embeddings multilíngues (`paraphrase-multilingual-MiniLM-L12-v2`) + índice FAISS

---

## 🧪 Evidências de Execução

Os testes abaixo foram realizados no chatbot online e demonstram o funcionamento dos principais fluxos implementados. Os prints estão disponíveis na pasta [`evidencias/`](./evidencias/).

### 01 — Interface Inicial
![Interface Inicial](evidencias/01_interface_inicial.png)

A interface carrega com mensagem de boas-vindas personalizada, painel de exemplos de perguntas e aviso legal no rodapé.

---

### 02 — Dúvida Geral: PSR
![Dúvida Geral PSR](evidencias/02_duvida_geral_PSR.png)

**Pergunta:** *"O que é o PSR e quem tem direito à subvenção?"*

O assistente recuperou corretamente contexto do **Guia dos Seguros Rurais (CNA/MAPA)** e do **Estudo Técnico sobre Seguro Rural no Mundo**, explicando que o PSR foi operacionalizado a partir de 2006 e que a subvenção é solicitada pela própria seguradora junto ao DEGER/MAPA, com concessão condicionada à situação cadastral do produtor e disponibilidade de recursos.

---

### 03 — PROAGRO vs Seguro Agrícola Privado
![PROAGRO Resolução BACEN](evidencias/03_proagro_resolucao_bacen.png)

**Pergunta:** *"Qual a diferença entre o PROAGRO e o seguro agrícola privado?"*

Resposta baseada em fontes regulatórias (Resolução BACEN 4.418) e técnicas (Modelagens Atuariais, Estudo Técnico), diferenciando financiamento público vs. privado, amplitude de cobertura, requisitos de adesão e estrutura de administração. O assistente recuperou contexto de 5 fontes distintas simultaneamente.

---

### 04 — Fluxo Guiado de Sinistro
![Fluxo Sinistro Guiado](evidencias/04_fluxo_sinistro_guiado.png)

**Pergunta:** *"Perdi minha lavoura de soja por granizo ontem. O que devo fazer?"*

O classificador de intenção identificou corretamente o evento como sinistro e ativou o fluxo guiado. O assistente orientou o produtor em 5 passos estruturados: verificação da apólice, coleta de evidências, comunicação à seguradora, envio de documentos e acompanhamento. Reforçou a criticidade do **prazo de comunicação**, com base no Manual de Peritos Rurais e na Resolução BACEN 4.418.

---

### 05 — Guardrail: Pergunta Fora do Escopo
![Guardrail Fora de Escopo](evidencias/05_guardrail_fora_escopo.png)

**Pergunta:** *"Quero fazer um seguro de carro, quanto custa?"*

O classificador de intenção identificou a pergunta como fora do domínio e o guardrail funcionou corretamente: o assistente recusou responder sobre seguro de automóvel, explicou seu escopo especializado e redirecionou para a SUSEP. A citação de fonte neste caso apontou para documentos de seguro rural — confirmando que o RAG não contém informações sobre seguros de automóvel e que o sistema não inventou uma resposta.

---

### 06 — Resposta com Múltiplas Fontes
![Múltiplas Fontes](evidencias/06_multiplas_fontes.png)

**Pergunta:** *"Quais são os requisitos para um perito realizar vistoria de sinistro agrícola?"*

Resposta baseada exclusivamente no **Manual de Capacitação de Peritos Rurais** (341 chunks), detalhando: gestão de capacidade em períodos de colheita, esclarecimento de dúvidas metodológicas ao segurado, determinação de percurso em colheita mecanizada e procedimentos em caso de discordância sobre a metodologia empregada.

---

### 07 — Crédito Rural e Obrigatoriedade do Seguro
![Crédito Rural](evidencias/07_credito_rural_seguro_obrigatorio.png)

**Pergunta:** *"O seguro é obrigatório quando contrato um financiamento rural pelo Pronaf?"*

O assistente confirmou a obrigatoriedade do seguro de custeio no Pronaf com base na **Base de Conhecimento AgroAssist** e no **Projeto de Lei sobre Fundo de Cobertura Suplementar**, orientando o produtor a verificar as condições específicas do financiamento.

---

### 08 — Repositório GitHub
![Repositório GitHub](evidencias/08_repositorio_github.png)

Estrutura completa do projeto versionada no GitHub, com organização profissional das pastas e histórico de commits documentando a evolução do desenvolvimento.

---

## 🛡️ Guardrails e Segurança

O AgroAssist IA implementa salvaguardas específicas para o setor de seguros:

- **Anti-alucinação:** o LLM é instruído a responder **somente** com base no contexto recuperado
- **Transparência de fonte:** toda resposta cita o documento de origem com nome amigável
- **Limitação de escopo:** perguntas fora do escopo são redirecionadas adequadamente, sem tentativa de responder sobre temas não cobertos
- **Aviso legal:** rodapé permanente orienta que o assistente não substitui corretor habilitado
- **Não afirmação de cobertura:** o sistema nunca afirma que uma apólice específica cobre ou não cobre algo, orientando sempre à verificação das condições gerais

---

## 🧰 Stack Tecnológica

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Interface | Streamlit | Deploy gratuito, rápido, ideal para PoC |
| Orquestração RAG | LangChain | Padrão de mercado, ampla documentação |
| Vector Store | FAISS (Meta) | Leve, sem servidor, arquivo único portável |
| Embeddings | HuggingFace `paraphrase-multilingual-MiniLM-L12-v2` | Gratuito, local, excelente desempenho em PT-BR |
| LLM | LLaMA 3.1 8B via Groq API | Gratuito, baixa latência, adequado para PoC |
| Loader de PDFs | PyPDFLoader (LangChain) | Extração de texto nativa, sem dependências extras |
| Deploy | Streamlit Community Cloud | Gratuito, URL pública, integração GitHub |

---

## 📁 Estrutura do Repositório

```
ai_to_so/
├── app.py                      # Interface Streamlit + lógica RAG + roteamento
├── requirements.txt            # Dependências do projeto
├── prompts.py                  # System prompts e configurações do LLM
├── .gitignore                  # Arquivos ignorados pelo Git
│
├── dados/                      # Base de conhecimento
│   ├── faq_agricola.json       # FAQ sintética (gerada via LLM + curadoria humana)
│   ├── faq_agricola.txt        # FAQ em texto legível
│   └── *.pdf                   # Documentos oficiais e técnicos (11 arquivos)
│
├── vectordb/                   # Índice vetorial gerado
│   ├── faiss_index/
│   │   ├── index.faiss         # Índice FAISS binário (1.106 chunks)
│   │   └── index.pkl           # Metadados dos chunks
│   └── chunks_metadata.json    # Rastreabilidade completa dos chunks por fonte
│
├── scripts/                    # Scripts utilitários (pipeline offline)
│   ├── ingestao.py             # Pipeline de ingestão RAG
│   ├── gerar_faq.py            # Geração de FAQ sintética via LLM (Groq)
│   └── gerar_faq_cat5.py       # Complemento da categoria 5 da FAQ
│
└── evidencias/                 # Screenshots e evidências de execução
    ├── EVIDENCIAS.md           # Descrição detalhada de cada evidência
    ├── 01_interface_inicial.png
    ├── 02_duvida_geral_PSR.png
    ├── 03_proagro_resolucao_bacen.png
    ├── 04_fluxo_sinistro_guiado.png
    ├── 05_guardrail_fora_escopo.png
    ├── 06_multiplas_fontes.png
    ├── 07_credito_rural_seguro_obrigatorio.png
    └── 08_repositorio_github.png
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- Chave de API Groq gratuita: https://console.groq.com

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/jlgsilva/ai_to_so.git
cd ai_to_so

# 2. Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
# Criar arquivo .env na raiz com:
# GROQ_API_KEY=sua_chave_aqui

# 5. (Opcional) Regenerar a base vetorial com novos documentos
python scripts/ingestao.py

# 6. Iniciar o chatbot
streamlit run app.py
```

---

## 📊 Resultados

### O que foi validado em execução

| Cenário | Resultado | Fontes utilizadas |
|---|---|---|
| Dúvida sobre PSR | ✅ Resposta correta com base regulatória | Guia CNA/MAPA · Estudo Técnico |
| Diferença PROAGRO vs. seguro privado | ✅ Distinção técnica precisa | Res. BACEN 4.418 · Modelagens Atuariais · 5 fontes |
| Sinistro por granizo | ✅ Fluxo guiado em 5 passos + alerta de prazo | Manual de Peritos · Res. BACEN 4.418 |
| Pergunta fora do escopo (seguro auto) | ✅ Guardrail ativado, redirecionamento correto | — |
| Requisitos de perito rural | ✅ Detalhamento técnico do manual oficial | Manual de Capacitação de Peritos Rurais |
| Obrigatoriedade seguro no Pronaf | ✅ Confirmação com base normativa | Base de Conhecimento · PL Fundo Suplementar |

### Limitações conhecidas

- Não acessa apólices reais ou sistemas de gestão de seguros
- Não realiza abertura formal de sinistros (apenas orienta o processo)
- Base FAQ com 16 pares indexados — pode ser expandida com dados reais de atendimento
- Sem integração com CRM ou sistemas de seguradoras
- Sem autenticação de usuário ou personalização por segurado

---

## 🔮 Trabalhos Futuros

1. **Integração com CRM** — acesso ao histórico do segurado para personalização do atendimento
2. **Abertura automatizada de sinistros** — integração via API com sistemas de seguradoras
3. **Expansão da base** — inclusão de histórico real de tickets de atendimento (anonimizado)
4. **Seguro paramétrico** — integração com dados climáticos (INMET, Climatempo) para triggers automáticos de cobertura
5. **Multimodalidade** — análise de fotos de lavoura para suporte à perícia de campo
6. **Autenticação** — identificação do produtor para acesso a informações da apólice vigente

---

## 👤 Autor

Desenvolvido por **Jefferson L. G. Silva** como atividade prática do programa
**InsurMinds | Inteligência Artificial Aplicada a Seguros**
I2A2 – Instituto de Inteligência Artificial Aplicada · Latin Re · Grupo FIT

---

## ⚠️ Aviso Legal

O AgroAssist IA é um assistente informativo desenvolvido para fins educacionais e demonstração de conceito. As respostas geradas não substituem a orientação de um corretor de seguros habilitado pela SUSEP, nem constituem proposta ou contrato de seguro. Para contratação de seguros, consulte sempre um profissional credenciado.
