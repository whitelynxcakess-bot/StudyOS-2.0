import re
from typing import List, Tuple
 
BANCAS = (
    r"CESPE|CEBRASPE|FCC|FGV|VUNESP|IBFC|IDECAN|QUADRIX|CESGRANRIO|"
    r"FUNDATEC|IADES|AOCP|FEPESE|CONSULPLAN|INSTITUTO AOCP"
)
 
# Alternativas: "A)", "(A)", "a.", "A -", "e)" ...
RE_ALTERNATIVA = re.compile(r"^\s*\(?([A-Ea-e])\s*[\).\-–]\s*\S")
 
# Inícios "fortes" de questão (não precisam de confirmação)
RE_INICIO_FORTE = re.compile(
    rf"""^\s*(
        quest[aã]o\s*\d+                  # Questão 12
      | q\.?\s*\d+\s*[\-–.:)]             # Q12.  Q12)
      | Q\d{{4,}}                         # Q1234567 (TEC Concursos)
      | \(?\s*(?:{BANCAS})\b.*\b(?:19|20)\d{{2}}   # (CEBRASPE – 2023 – ...)
      | ano:\s*(?:19|20)\d{{2}}.*banca:   # Ano: 2023 Banca: ...
      | julgue\b                          # Julgue o item a seguir
    )""",
    re.IGNORECASE | re.VERBOSE,
)
 
# Linha numerada: "12.", "12)", "(12)", "12 -"
RE_NUMERADA = re.compile(r"^\s*\(?\d{1,3}\s*[\).\-–]\s+\S")
 
# Verbos/expressões típicos de comando de questão
RE_COMANDO = re.compile(
    r"\b(julgue|assinale|marque|indique|determine|considere|analise|assertiva|"
    r"alternativa|item a seguir|[ée] correto afirmar|conforme o texto|"
    r"de acordo com)\b",
    re.IGNORECASE,
)
 
RE_CABECALHO = re.compile(
    rf"^\s*\(?\s*(?:{BANCAS})\b|^\s*ano:\s*(?:19|20)\d{{2}}|^\s*Q\d{{4,}}\s*$",
    re.IGNORECASE,
)
RE_GABARITO = re.compile(r"^\s*(gabarito|resposta)\s*[:\-–]", re.IGNORECASE)
 
 
def _eh_alternativa(s: str) -> bool:
    return bool(RE_ALTERNATIVA.match(s))
 
 
def _inicia_questao(linhas: List[str], i: int) -> bool:
    s = linhas[i].strip()
    if not s:
        return False
    if RE_INICIO_FORTE.match(s):
        return True
    if RE_NUMERADA.match(s):
        # Confirma olhando as próximas linhas: precisa ter alternativas
        # ou um comando de questão na própria linha.
        if RE_COMANDO.search(s):
            return True
        alts = 0
        vistas = 0
        for prox in linhas[i + 1 :]:
            p = prox.strip()
            if not p:
                continue
            if RE_NUMERADA.match(p) or RE_INICIO_FORTE.match(p):
                break
            vistas += 1
            if _eh_alternativa(p):
                alts += 1
            if vistas >= 12:
                break
        return alts >= 2
    return False
 
 
def _proxima_nao_vazia(linhas: List[str], i: int) -> str:
    for l in linhas[i + 1 :]:
        if l.strip():
            return l.strip()
    return ""
 
 
def separar_conteudo_questoes(texto: str) -> Tuple[List[str], List[str]]:
    """Recebe o texto bruto e devolve (conteudo, questoes)."""
    linhas = texto.replace("\r\n", "\n").replace("\r", "\n").split("\n")
 
    conteudo: List[str] = []
    questoes: List[str] = []
    buf_c: List[str] = []
    buf_q: List[str] = []
    em_questao = False
    n_alt = 0
    ultima_letra = ""
 
    def fechar_conteudo():
        nonlocal buf_c
        bloco = "\n".join(buf_c).strip()
        if bloco:
            conteudo.append(bloco)
        buf_c = []
 
    def fechar_questao():
        nonlocal buf_q, em_questao, n_alt, ultima_letra
        bloco = "\n".join(buf_q).strip()
        if bloco:
            questoes.append(bloco)
        buf_q, em_questao, n_alt, ultima_letra = [], False, 0, ""
 
    for i, linha in enumerate(linhas):
        s = linha.strip()
 
        # 1) Começou uma nova questão
        if _inicia_questao(linhas, i):
            if em_questao and len(buf_q) == 1 and RE_CABECALHO.match(buf_q[0]):
                buf_q.append(s)  # cabeçalho da questão + enunciado
                continue
            if em_questao:
                fechar_questao()
            else:
                fechar_conteudo()
            em_questao = True
            buf_q = [s]
            continue
 
        # 2) Dentro de uma questão
        if em_questao:
            if not s:
                if len(buf_q) == 1 or RE_CABECALHO.match(buf_q[-1]) \
                        or re.match(r"^\s*julgue\b", buf_q[-1], re.I):
                    continue
                prox = _proxima_nao_vazia(linhas, i)
                if n_alt >= 2:
                    fechar_questao()
                elif n_alt == 0 and not _eh_alternativa(prox) \
                        and not buf_q[-1].rstrip().endswith((":", ",")):
                    # item autocontido (ex.: Certo/Errado) terminou
                    fechar_questao()
                continue
 
            if RE_GABARITO.match(s):
                buf_q.append(s)
                fechar_questao()
                continue
 
            if _eh_alternativa(s):
                n_alt += 1
                ultima_letra = RE_ALTERNATIVA.match(s).group(1).lower()
                buf_q.append(s)
                continue
 
            if n_alt >= 2:
                # Linha comum depois das alternativas: continuação da última
                # alternativa (quebra de linha do PDF) ou volta do conteúdo?
                anterior = buf_q[-1].rstrip()
                terminou = anterior.endswith((".", ";", "?", "!", ":"))
                if s[0].isupper() and (terminou or ultima_letra == "e"):
                    fechar_questao()
                    buf_c.append(s)
                else:
                    buf_q.append(s)
                continue
 
            buf_q.append(s)
            continue
 
        # 3) Conteúdo normal
        buf_c.append(s)
 
    if em_questao:
        fechar_questao()
    fechar_conteudo()
    return conteudo, questoes