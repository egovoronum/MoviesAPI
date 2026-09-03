"""Песочница. Запуск: python -m sandbox.playground"""
import sys

from pydantic import ConfigDict, ValidationError

from sandbox import payloads
from sandbox.models import Movie, MovieDetails, MoviesPage

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8") # type: ignore[attr-defined]

def title(text):
    print(f"\n{'=' * 15} {text} {'=' * 15}")

title("1. Один вызов разбирает всё дерево")
page = MoviesPage(**payloads.MOVIES_PAGE)

print("тип page.movies         :", type(page.movies).__name__)
print("тип page.movies[0]      :", type(page.movies[0]).__name__)
print("тип page.movies[0].genre:", type(page.movies[0].genre).__name__)
print("доступ через точку      :", page.movies[0].genre.name)

title("2. Три уровня вложенности")
details = MovieDetails(**payloads.MOVIE_DETAILS)

print("фильм               :", details.name)
print("жанр (уровень 2)    :", details.genre.name)
print("автор отзыва (ур. 3):", details.reviews[0].user.fullName)
print("createdAt стал      :", type(details.createdAt).__name__)
print("location стал       :", repr(details.location))

title("3. Ошибка внутри вложенной модели")
try:
    MoviesPage(**payloads.BROKEN_TYPES)
except ValidationError as e:
    print(e)
    print("\nloc-кортежи:")
    for err in e.errors():
        print("   ", err["loc"], "->", err["type"])

        title("4. Поломка на третьем уровне")
try:
    MovieDetails(**payloads.BROKEN_DEEP)
except ValidationError as e:
    for err in e.errors():
        print("   ", ".".join(str(p) for p in err["loc"]), "->", err["msg"])

        title("5. Пропала вложенная модель")
try:
    MoviesPage(**payloads.MISSING_NESTED)
except ValidationError as e:
    for err in e.errors():
        print("   ", err["loc"], "->", err["msg"])