from django.shortcuts import render

# Create your views here.


from html import escape

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.middleware.csrf import get_token

from .models import Book



def page(content, request, title="Book Store"):
    token = get_token(request)

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{escape(title)}</title>
    </head>

    <body>
        <header>
            <h1><a href="/">Book Store</a></h1>
            <nav>
                <a href="/">Каталог</a>
                <a href="/cart/">Корзина</a>
            </nav>
        </header>
        
        <main>
            {content}
        </main>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                background: #f4f6fb;
                color: #202943;
                font-family: Arial, sans-serif;
            }}

            header {{
                background: #172554;
                color: white;
                padding: 22px 7%;
            }}

            header h1 {{
                margin: 0;
                font-size: 28px;
            }}

            header a {{
                color: white;
                text-decoration: none;
            }}

            nav {{
                margin-top: 14px;
            }}

            nav a {{
                color: #dbeafe;
                text-decoration: none;
                margin-right: 22px;
            }}

            main {{
                max-width: 1100px;
                margin: 35px auto;
                padding: 0 20px;
            }}

            h2 {{
                font-size: 28px;
                margin-bottom: 25px;
            }}

            h3 {{
                font-size: 19px;
                margin-top: 12px;
            }}

            img {{
                width: 150px;
                height: 210px;
                object-fit: contain;
                background: #f8fafc;
                border-radius: 8px;
            }}

            form {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                margin: 5px 4px 5px 0;
            }}

            input[type="number"] {{
                width: 55px;
                padding: 9px 4px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                text-align: center;
            }}

            button {{
                border: none;
                border-radius: 8px;
                padding: 11px 16px;
                background: #1d4ed8;
                color: white;
                font-weight: bold;
                cursor: pointer;
            }}

            button:hover {{
                background: #1e40af;
            }}

            button[type="button"] {{
                min-width: 38px;
                padding: 10px;
                background: #e2e8f0;
                color: #172554;
                font-size: 18px;
            }}

            button[type="button"]:hover {{
                background: #cbd5e1;
            }}

            hr {{
                border: 0;
                border-top: 1px solid #e2e8f0;
                margin: 24px 0;
            }}

            p {{
                line-height: 1.6;
            }}

            @media (max-width: 600px) {{
                header {{
                    padding: 20px;
                }}

                main {{
                    margin: 22px auto;
                    padding: 0 16px;
                }}

                h2 {{
                    font-size: 23px;
                }}
            }}
        </style>
    </body>
    </html>
    """

    return HttpResponse(html.replace(
        "<!--CSRF-->",
        f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">'
    ))



def book_list(request):
    books = Book.objects.all()
    cart = request.session.get("cart", {})

    content = "<h2>Каталог книг</h2>"

    for book in books:
        quantity = cart.get(str(book.id), 0)

        content += f"<h3>{escape(book.title)}</h3>"
        content += f"<p>Цена: {book.price:,} сум</p>"

        if book.image:
            content += (
                f'<img src="{escape(book.image)}" '
                f'alt="{escape(book.title)}" width="150">'
            )

        content += f"""
        <form method="post" action="/cart/add/{book.id}/">
            <!--CSRF-->
            <button type="button"
                onclick="let q=this.parentElement.quantity;
                if(q.value>1)q.value--;">−</button>

            <input type="number" name="quantity"
                value="{max(1, quantity)}" min="1" max="99">

            <button type="button"
                onclick="let q=this.parentElement.quantity;
                if(q.value<99)q.value++;">+</button>

            <button type="submit">В корзину</button>
        </form>
        <p>В корзине: {quantity}</p>
        <hr>
        """

    return page(content, request)


def add_to_cart(request, book_id):
    if request.method != "POST":
        return redirect("/")

    book = get_object_or_404(Book, id=book_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1

    quantity = max(1, min(quantity, 99))

    cart = request.session.get("cart", {})
    key = str(book.id)

    cart[key] = cart.get(key, 0) + quantity
    request.session["cart"] = cart

    return redirect("/")


def cart_view(request):
    cart = request.session.get("cart", {})
    content = "<h2>Корзина</h2>"
    total = 0

    for book_id, quantity in list(cart.items()):
        book = Book.objects.filter(id=book_id).first()

        if book is None:
            cart.pop(book_id, None)
            continue

        subtotal = book.price * quantity
        total += subtotal

        content += f"""
        <h3>{escape(book.title)}</h3>
        <p>Цена: {book.price:,} сум</p>
        <p>Количество: {quantity}</p>
        <p>Сумма: {subtotal:,} сум</p>

        <form method="post" action="/cart/minus/{book.id}/">
            <!--CSRF-->
            <button type="submit">−</button>
        </form>

        <form method="post" action="/cart/plus/{book.id}/">
            <!--CSRF-->
            <button type="submit">+</button>
        </form>

        <form method="post" action="/cart/remove/{book.id}/">
            <!--CSRF-->
            <button type="submit">Убрать</button>
        </form>
        <hr>
        """

    request.session["cart"] = cart

    if not cart:
        content += "<p>Корзина пустая.</p>"

    content += f"<h2>Итого: {total:,} сум</h2>"

    return page(content, request, "Корзина")


def plus_cart(request, book_id):
    if request.method != "POST":
        return redirect("/cart/")

    get_object_or_404(Book, id=book_id)

    cart = request.session.get("cart", {})
    key = str(book_id)
    cart[key] = min(cart.get(key, 0) + 1, 99)

    request.session["cart"] = cart
    return redirect("/cart/")


def minus_cart(request, book_id):
    if request.method != "POST":
        return redirect("/cart/")

    cart = request.session.get("cart", {})
    key = str(book_id)

    if key in cart:
        cart[key] -= 1

        if cart[key] <= 0:
            del cart[key]

    request.session["cart"] = cart
    return redirect("/cart/")


def remove_from_cart(request, book_id):
    if request.method != "POST":
        return redirect("/cart/")

    cart = request.session.get("cart", {})
    cart.pop(str(book_id), None)

    request.session["cart"] = cart
    return redirect("/cart/")


def books_api(request):
    books = Book.objects.all()

    data = []

    for book in books:
        data.append({
            "id": book.id,
            "title": book.title,
            "price": book.price,
            "image": book.image,
            "category": book.category.name if book.category else None,
        })

    return JsonResponse({"books": data})
