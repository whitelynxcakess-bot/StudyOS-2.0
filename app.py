import fitz  # PyMuPDF
import numpy as np
from limpador_textual import separar_conteudo_questoes
from modelo_e_prompt import resumir_texto, gerar_embedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
from insert_on_database import insert_on_documentos

def extrair_texto_pdf(caminho_pdf):
    texto = ""

    with fitz.open(caminho_pdf) as pdf:
        for pagina in pdf:
            texto += pagina.get_text()

    return texto

local_arquivo = "./venv/src/segurança da informação.pdf"

texto_redes = extrair_texto_pdf(local_arquivo)

conteudo_redes, questoes_redes = separar_conteudo_questoes(texto_redes)

texto_resumo_redes = resumir_texto(conteudo_redes)

#with open("./arquivo_final.txt", "w", encoding="utf-8") as f:
#    f.write(texto_final)

embedding_resumo_redes = gerar_embedding(texto_resumo_redes)

print(f'Total de números (redes): {len(embedding_resumo_redes)}\n')

vector_str = "[" + ",".join(map(str, embedding_resumo_redes)) + "]"

print(len(conteudo_redes))

quantidade = len(conteudo_redes[0].split())

print(quantidade)

#insert_on_documentos(local_arquivo,texto_resumo_redes,vector_str)

texto_final_conteudo = "".join(
    texto
    for sublista in conteudo_redes
    for texto in sublista
)

print(texto_final_conteudo[:10])

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " "
    ]
)

chunks = splitter.split_text(texto_final_conteudo)

print(vector_str[:10])
print(len(questoes_redes))
print(len(chunks))
print(type(chunks))


