import os
import time
import pymysql


def get_connection():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "root")
    database = os.getenv("DB_NAME", "bookstore")

    for _ in range(30):
        try:
            return pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.MySQLError as e:
          print("MYSQL ERROR:", e)
          time.sleep(2)

    raise Exception("Could not connect to MySQL")


def init_db():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    description TEXT
                )
            """)

            cursor.execute("SELECT COUNT(*) AS count FROM books")
            result = cursor.fetchone()

            if result["count"] == 0:
                cursor.executemany(
                    """
                    INSERT INTO books (title, author, price, description)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [
                        (
                            "The Alchemist",
                            "Paulo Coelho",
                            12.99,
                            "A classic novel about following your dreams."
                        ),
                        (
                            "Atomic Habits",
                            "James Clear",
                            18.99,
                            "A practical guide to building good habits."
                        ),
                        (
                            "Clean Code",
                            "Robert C. Martin",
                            29.99,
                            "A guide to writing clean and maintainable software."
                        )
                    ]
                )

        connection.commit()

    finally:
        connection.close()