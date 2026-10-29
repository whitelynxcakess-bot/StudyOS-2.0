import psycopg2

def connect_database():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="rag_local",
        user="postgres",
        password="159263748kornA@"
    )

    print('Conectado!')
    return conn


def insert_on_documentos(nome_arquivo, resumo, resumo_embedding):
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documentos (
            nome_arquivo,
            resumo,
            resumo_embedding
        )
        VALUES (%s, %s, %s)
        """,
        (
            nome_arquivo,
            resumo,
            resumo_embedding
        )
    )
    conn.commit() 
    print('Inserido com Sucesso!')
    cursor.close()
    conn.close()