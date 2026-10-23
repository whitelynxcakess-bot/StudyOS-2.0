import fitz  # PyMuPDF
import numpy as np
from limpador_textual import separar_conteudo_questoes
from modelo_e_prompt import resumir_texto, gerar_embedding
from sklearn.metrics.pairwise import cosine_similarity

def extrair_texto_pdf(caminho_pdf):
    texto = ""

    with fitz.open(caminho_pdf) as pdf:
        for pagina in pdf:
            texto += pagina.get_text()

    return texto

texto_redes = extrair_texto_pdf("./venv/src/segurança da informação.pdf")
texto_lgpd = extrair_texto_pdf("./venv/src/intro_lgpd.pdf")
texto_rlog = extrair_texto_pdf("./venv/src/intro_logica.pdf")

conteudo_redes, questoes_redes = separar_conteudo_questoes(texto_redes)
conteudo_lgpd, questoes_lgpd = separar_conteudo_questoes(texto_lgpd)
conteudo_rlog, questoes_rlog = separar_conteudo_questoes(texto_rlog)

texto_final_redes = resumir_texto(conteudo_redes)
texto_final_lgpd = resumir_texto(conteudo_lgpd)
texto_final_rlog = resumir_texto(conteudo_rlog)

#with open("./arquivo_final.txt", "w", encoding="utf-8") as f:
#    f.write(texto_final)

embedding_resumo_redes = gerar_embedding(texto_final_redes)
embedding_resumo_lgpd = gerar_embedding(texto_final_lgpd)
embedding_resumo_rlog = gerar_embedding(texto_final_rlog)

print(f'Total de números (redes): {len(embedding_resumo_redes)}\n')
print(f'Total de números (lgpd): {len(embedding_resumo_lgpd)}\n')
print(f'Total de números (rlog): {len(embedding_resumo_rlog)}\n')

vetores = np.array([embedding_resumo_redes, embedding_resumo_lgpd, embedding_resumo_rlog])

matriz = cosine_similarity(vetores)

print(matriz)