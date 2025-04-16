import psycopg2

def create_db(dbname: str, user: str, password: str, host: str = "localhost", port: str = "5432"):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,

    )
