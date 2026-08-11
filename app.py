import os
from flask import Flask, render_template, request, redirect, url_for
from database import get_connection, init_db

app = Flask(__name__)


@app.route("/health")
def health():
    return {"status": "healthy"}, 200

@app.route("/")
def index():
    search = request.args.get("search", "")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            if search:
                cursor.execute(
                    """
                    SELECT * FROM books
                    WHERE title LIKE %s OR author LIKE %s
                    ORDER BY id DESC
                    """,
                    (f"%{search}%", f"%{search}%")
                )
            else:
                cursor.execute("SELECT * FROM books ORDER BY id DESC")

            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template("index.html", books=books, search=search)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]
        description = request.form["description"]

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO books (title, author, price, description)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (title, author, price, description)
                )

            connection.commit()

        finally:
            connection.close()

        return redirect(url_for("index"))

    return render_template("add_book.html")


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            if request.method == "POST":
                title = request.form["title"]
                author = request.form["author"]
                price = request.form["price"]
                description = request.form["description"]

                cursor.execute(
                    """
                    UPDATE books
                    SET title=%s, author=%s, price=%s, description=%s
                    WHERE id=%s
                    """,
                    (title, author, price, description, book_id)
                )

                connection.commit()

                return redirect(url_for("index"))

            cursor.execute(
                "SELECT * FROM books WHERE id=%s",
                (book_id,)
            )

            book = cursor.fetchone()

    finally:
        connection.close()

    return render_template("edit_book.html", book=book)


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM books WHERE id=%s",
                (book_id,)
            )

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )