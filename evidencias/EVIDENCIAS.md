# 📸 Evidências de Execução — AgroAssist IA

Este documento descreve as evidências de execução do chatbot AgroAssist IA,
organizadas por cenário de teste. Cada evidência demonstra um aspecto distinto
da solução implementada.

---

## 🖥️ Acesso ao Chatbot

**URL pública:** https://agro-assist-seguro-rural.streamlit.app/

---

## Evidência 01 — Interface Inicial e Boas-vindas

**Arquivo:** `01_interface_inicial.png`

**O que demonstra:**
- Interface do AgroAssist IA carregada com sucesso no Streamlit Cloud
- Mensagem de boas-vindas personalizada
- Painel de exemplos de perguntas expandido
- Aviso legal no rodapé

**Pergunta utilizada:** *(nenhuma — apenas a tela inicial)*

---

## Evidência 02 — Dúvida Geral com Citação de Fonte Oficial

**Arquivo:** `02_duvida_geral_PSR.png`

**O que demonstra:**
- Fluxo de dúvida geral funcionando via RAG
- Recuperação de contexto de documentos oficiais
- Citação de fonte ao final da resposta
- Resposta tecnicamente correta sobre política pública

**Pergunta utilizada:**
> "O que é o PSR e quem tem direito à subvenção?"

**Fonte esperada na resposta:** Guia dos Seguros Rurais — CNA/MAPA ou Lei 10.823/2003

---

## Evidência 03 — PROAGRO com Base Regulatória

**Arquivo:** `03_proagro_resolucao_bacen.png`

**O que demonstra:**
- Recuperação de contexto da Resolução BACEN 4.418 (regulamentação do PROAGRO)
- Resposta baseada em norma regulatória, não em conhecimento genérico do LLM
- Diferenciação entre PROAGRO e seguro rural privado

**Pergunta utilizada:**
> "Qual a diferença entre o PROAGRO e o seguro agrícola privado?"

---

## Evidência 04 — Fluxo Guiado de Sinistro

**Arquivo:** `04_fluxo_sinistro_guiado.png`

**O que demonstra:**
- Classificação de intenção identificando "sinistro"
- Fluxo conversacional guiado com coleta progressiva de informações
- Orientação sobre prazos de comunicação (ponto crítico em seguros)
- Tom acolhedor adequado a momento de estresse do produtor

**Pergunta utilizada:**
> "Perdi minha lavoura de soja por granizo ontem. O que devo fazer?"

---

## Evidência 05 — Fluxo Guiado de Cotação

**Arquivo:** `05_fluxo_cotacao_guiado.png`

**O que demonstra:**
- Classificação de intenção identificando "cotação"
- Coleta estruturada: cultura → município → área → financiamento
- Encaminhamento adequado para corretor habilitado
- Informação sobre tipos de cobertura disponíveis

**Pergunta utilizada:**
> "Quero fazer um seguro para minha lavoura de milho no Mato Grosso"

---

## Evidência 06 — Guardrail: Pergunta Fora do Escopo

**Arquivo:** `06_guardrail_fora_escopo.png`

**O que demonstra:**
- Identificação correta de pergunta fora do domínio do assistente
- Redirecionamento educado sem tentar responder inadequadamente
- Oferta de ajuda dentro do escopo especializado
- Maturidade de engenharia: o sistema sabe o que não sabe

**Pergunta utilizada:**
> "Quero fazer um seguro de carro, quanto custa?"

---

## Evidência 07 — Resposta com Múltiplas Fontes

**Arquivo:** `07_multiplas_fontes.png`

**O que demonstra:**
- Recuperação de contexto de múltiplos documentos simultaneamente (k=6)
- Síntese de informações de fontes distintas em resposta coerente
- Citação de múltiplas fontes na resposta
- Capacidade do RAG de cruzar informações de documentos diferentes

**Pergunta utilizada:**
> "Quais são os requisitos para um perito realizar vistoria de sinistro agrícola?"

---

## Evidência 08 — Crédito Rural e Obrigatoriedade do Seguro

**Arquivo:** `08_credito_rural_seguro_obrigatorio.png`

**O que demonstra:**
- Resposta sobre tema técnico-regulatório (MCR — Manual de Crédito Rural)
- Distinção entre seguro obrigatório e facultativo no financiamento rural
- Base em resolução do Banco Central (CMN 4.902/2021 ou CMN 5.220/2025)

**Pergunta utilizada:**
> "O seguro é obrigatório quando contrato um financiamento rural pelo Pronaf?"

---

## Evidência 09 — Pipeline de Ingestão RAG (execução local)

**Arquivo:** `09_pipeline_ingestao.png`

**O que demonstra:**
- Execução do script `ingestao.py` no Spyder
- Carregamento de 11 PDFs + FAQ JSON
- Geração de 1.106 chunks
- Criação e salvamento do índice FAISS
- Teste automático de recuperação ao final

**Como capturar:** Screenshot do terminal do Spyder com o output completo do `ingestao.py`

---

## Evidência 10 — Geração de FAQ Sintética (execução local)

**Arquivo:** `10_geracao_faq_sintetica.png`

**O que demonstra:**
- Execução do script `gerar_faq.py` no Spyder
- Geração de pares Q&A via LLM para 5 categorias temáticas
- Metodologia de dados sintéticos para enriquecimento da base

**Como capturar:** Screenshot do terminal do Spyder com o output do `gerar_faq.py`

---

## Evidência 11 — Repositório GitHub

**Arquivo:** `11_repositorio_github.png`

**O que demonstra:**
- Estrutura completa do projeto versionada no GitHub
- Organização profissional das pastas (dados, scripts, vectordb, evidencias)
- Histórico de commits documentando a evolução do desenvolvimento

**URL:** https://github.com/jlgsilva/ai_to_so

---

## Evidência 12 — App Online no Streamlit Cloud

**Arquivo:** `12_streamlit_cloud_deploy.png`

**O que demonstra:**
- Dashboard do Streamlit Cloud com o app deployado
- Status "Running" confirmando disponibilidade pública
- Integração com repositório GitHub (CI/CD automático)

---

## 📋 Checklist de Capturas

| # | Evidência | Capturado? |
|---|---|---|
| 01 | Interface inicial | ☐ |
| 02 | Dúvida geral — PSR | ☐ |
| 03 | PROAGRO — base regulatória | ☐ |
| 04 | Fluxo sinistro guiado | ☐ |
| 05 | Fluxo cotação guiado | ☐ |
| 06 | Guardrail fora de escopo | ☐ |
| 07 | Múltiplas fontes | ☐ |
| 08 | Crédito rural obrigatoriedade | ☐ |
| 09 | Pipeline ingestão RAG | ☐ |
| 10 | Geração FAQ sintética | ☐ |
| 11 | Repositório GitHub | ☐ |
| 12 | Deploy Streamlit Cloud | ☐ |

---

## 💡 Dica para as capturas

Use **Windows + Shift + S** para captura parcial da tela no Windows.
Salve todos os arquivos nesta pasta (`evidencias/`) com os nomes indicados acima
antes de fazer o `git push` final.
