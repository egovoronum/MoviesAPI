# Ответ GET /movies?pageSize=2
MOVIES_PAGE = {
    "movies": [
        {
            "id": 110,
            "name": "Network soon.",
            "description": "Kind good stuff case shake dream scientist small.",
            "genreId": 9,
            "imageUrl": "https://placekitten.com/716/584",
            "price": 130,
            "rating": 0,
            "location": "SPB",
            "published": True,
            "createdAt": "2025-05-08T11:17:38.758Z",
            "genre": {"name": "Анимация"},
        },
        {
            "id": 589,
            "name": "Movie name",
            "description": "Movie description",
            "genreId": 4,
            "imageUrl": "https://image.url",
            "price": 100,
            "rating": 0,
            "location": "SPB",
            "published": True,
            "createdAt": "2025-05-20T20:59:56.997Z",
            "genre": {"name": "Криминал"},
        },
    ],
    "count": 2840,
    "page": 1,
    "pageSize": 2,
    "pageCount": 1420,
}

# Ответ GET /movies/110 - тот же фильм, но с отзывами
MOVIE_DETAILS = {
    "id": 110,
    "name": "Network soon.",
    "description": "Kind good stuff case shake dream scientist small.",
    "genreId": 9,
    "imageUrl": "https://placekitten.com/716/584",
    "price": 130,
    "rating": 0,
    "location": "SPB",
    "published": True,
    "createdAt": "2025-05-08T11:17:38.758Z",
    "genre": {"name": "Анимация"},
    "reviews": [
        {
            "userId": "359e1a10-9220-47cd-a420-cdad5096c98c",
            "text": "Отличный фильм",
            "rating": 1,
            "createdAt": "2025-12-13T16:40:33.003Z",
            "user": {"fullName": "Melissa Ellis"},
        }
    ],
}

# --- Намеренно сломанные варианты для упражнений ---

# 1. У второго фильма price пришёл нечисловой строкой, а rating вышел за диапазон 0..5
BROKEN_TYPES = {
    **MOVIES_PAGE,
    "movies": [
        MOVIES_PAGE["movies"][0],
        {**MOVIES_PAGE["movies"][1], "price": "сто тридцать", "rating": 99},
    ],
}

# 2. У первого фильма пропала вложенная модель genre
MISSING_NESTED = {
    **MOVIES_PAGE,
    "pageSize": 1,
    "movies": [
        {k: v for k, v in MOVIES_PAGE["movies"][0].items() if k != "genre"},
    ],
}

# 3. Бэкенд добавил поля, которых нет в наших моделях
WITH_EXTRA_FIELDS = {
    **MOVIES_PAGE,
    "totalRevenue": 999999,
    "pageSize": 1,
    "movies": [
        {**MOVIES_PAGE["movies"][0], "ageRating": "18+", "isPromoted": True},
    ],
}

# 4. Поломка на третьем уровне: внутри отзыва испорчен автор
BROKEN_DEEP = {
    **MOVIE_DETAILS,
    "reviews": [
        {**MOVIE_DETAILS["reviews"][0], "rating": 10, "user": {"fullName": 12345}},
    ],
}