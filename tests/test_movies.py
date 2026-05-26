import pytest

class TestMoviesAPI:
# GET MOVIES // testing first movie in the list
    def test_get_movies(self, filter_movies):
        movies = filter_movies["movies"]
        assert len(movies) > 0, "Returned an empty movies list"
        assert "id" in movies[0], "No ID in movies[0]"
        assert "genreId" in movies[0], "No genreId in movies[0]"
        assert "imageUrl" in movies[0], "No imageUrl in movies[0]"
        assert "price" in movies[0], "No price in movies[0]"
        assert "rating" in movies[0], "No rating in movies[0]"
        assert "location" in movies[0], "No location in movies[0]"
        assert "published" in movies[0], "No published in movies[0]"
        assert "createdAt" in movies[0], "No createdAt in movies[0]"
        assert "genre" in movies[0], "No genre object in movies[0]"
        assert "name" in movies[0]["genre"], "No genre.name in movies[0]"

# GET MOVIES // testing price filter
    def test_get_movies_by_price(self, filter_movies_by_price):
        movies = filter_movies_by_price["movies"]
        for movie in movies:
            assert 200 <= movie["price"] <= 500, "Price filter test failed"

# testing pageSize, location, price filter combo
    def test_get_movies_filter_combo(self, filter_combo):
        movies = filter_combo["movies"]
        assert filter_combo["pageSize"] == 12, "PageSize filter test failed in combo filter"
        assert filter_combo["page"] == 1, "Page number mismatch"

        for movie in movies:
            assert 1 <= movie["price"] <= 1000, "Price filter test failed in combo filter"
            assert movie["location"] == "MSK", "Location filter test failed in combo filter"
        
# GET MOVIES // negative testing for price filter and negative value

    def test_invalid_price(self, filter_by_invalid_price):
        response = filter_by_invalid_price
        assert response["statusCode"] == 400, f"Expected 400, got {response["statusCode"]}"

# GET MOVIES // negative testing for page (-1 value)

    def test_invalid_page(self, filter_by_invalid_page):
        response = filter_by_invalid_page
        assert response["statusCode"] == 400, f"Expected 400, got {response["statusCode"]}"
        assert "Поле page имеет минимальную величину 1" in response["message"], f"Expected to see an error description in `message` but got {response["message"]}"