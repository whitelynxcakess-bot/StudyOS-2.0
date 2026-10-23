import numpy as np
from ollama import Client
import json

HOST = "http://127.0.0.1:11434"
MODELO = "gemma3:4b"
MODEL_EMBEDDING = "mxbai-embed-large:latest"

client = Client(host=HOST, trust_env=False)


SCHEMA = {
    "type": "object",
    "properties": {"resumo": {"type": "string"}},
    "required": ["resumo"],
}

SYSTEM = (
    "Você resume textos de estudo. Responda SEMPRE em português do Brasil, "
    "com um único parágrafo curto, em texto corrido, sem listas, sem markdown "
    "e sem perguntas ou ofertas no final."
)

EXEMPLO = (
    "O texto trata de redes de computadores, explicando o modelo OSI e suas sete "
    "camadas, com destaque para as funções de roteamento na camada de rede e de "
    "transporte confiável no TCP, além de comparar TCP e UDP."
)


def resumir_texto(texto: str) -> str:
    prompt = f"""
    Resuma o conteúdo abaixo em um único parágrafo de 40 a 80 palavras, em português do Brasil.
    Cite o assunto principal, os conceitos-chave (com os termos exatos do texto) e os tópicos abordados.
    Ignore contatos, redes sociais, propaganda e despedidas.

    Exemplo de estilo (outro assunto):
    {EXEMPLO}

    <conteudo>
    {texto}
    </conteudo>

    Agora escreva o resumo em português do Brasil, em um único parágrafo, no campo "resumo".
    """

    resp = client.chat(
        model=MODELO,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        format=SCHEMA,
        options={"temperature": 0.2, "num_ctx": 8192, "num_predict": 250},
        keep_alive="30m",
    )

    try:
        print('teve campo resumo')
        resumo = json.loads(resp["message"]["content"])["resumo"]
    except (json.JSONDecodeError, KeyError):
        print('não teve campo resumo')
        resumo = resp["message"]["content"]
    return " ".join(resumo.split())


def gerar_embedding(texto: str):
    """
    Compatível com Ollama mais novo e mais antigo.
    """

    try:
        resp = client.embed(
            model=MODEL_EMBEDDING,
            input=texto
        )

        return np.array(resp["embeddings"][0])

    except AttributeError:
        resp = client.embeddings(
            model=MODEL_EMBEDDING,
            prompt=texto
        )

        return np.array(resp["embedding"])