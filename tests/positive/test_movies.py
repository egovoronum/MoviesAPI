import pytest, random
from clients.api_manager import ApiManager
from utils.time_util import iso_now
from faker import Faker
fake = Faker("ru_RU")

# Написать тест, который проверяет удаление фильмов но с ролевой моделью, 
# по доке только супер админы могут удалять так же он должен быть параметризован

@pytest.mark.parametrize("user, status", [
    ("super_admin", 200),
    ("admin_user", 403),
    ("common_user", 403),
], ids=["SUPER ADMIN", "ADMIN USER", "COMMON USER"])
def test_delete_movie_parametrized(request, super_admin, user, status):

    client = request.getfixturevalue(user)

    response = super_admin.api.movies_api.get_genres(
            expected_status=200
        )
    
    genres = response.json()
    genre = random.choice(genres)
    genre_id = genre["id"]
    
    data = {
        "name": f"{fake.word()} в {fake.word()}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 1000),
        "description": f"{fake.text(10)} не все так однозначно с {fake.text(10)}",
        "location": "MSK",
        "published": True,
        "genreId": genre_id  
    }

    response = super_admin.api.movies_api.create_movie(
        data,
        expected_status=201
    )

    created_movie = response.json()

    assert data["name"] == created_movie["name"]

    delete_response = client.api.movies_api.delete_movie(
        created_movie["id"],
        expected_status=status
    )

    if status == 200:
        deleted_movie = delete_response.json()
        assert deleted_movie["id"] == created_movie["id"]

class TestParametrizedFilters:

    @pytest.mark.parametrize("filter_parameters", [
        {
            "minPrice": 1,
            "maxPrice": 1000,
        },
        {
            "locations": "MSK"
        },
        {
            "genreId": 1
        }
    ], ids=["PRICE FILTER", "LOCATION FILTER", "GENRE FILTER"])

    def test_parametrized_movie_filters(
            self,
            common_user,
            filter_parameters
        ):

        response = common_user.api.movies_api.get_movies(
            params=filter_parameters,
            expected_status=200
        )


class TestGetMovies:

    def test_get_404movie(
            self,
            unauthenticated_api_manager: ApiManager,
            invalid_movie_id: int
        ):

        response = unauthenticated_api_manager.movies_api.get_movie(
            invalid_movie_id, 
            expected_status=404
        )

        data = response.json()

        assert "Фильм не найден" in data["message"]
        assert "Not Found" in data["error"]


    def test_get_200movie(
            self,
            unauthenticated_api_manager: ApiManager,
            grab_movie: int
        ):

        response = unauthenticated_api_manager.movies_api.get_movie(
            grab_movie,
            expected_status=200
        )

        data = response.json()

        assert "id" in data
        assert "name" in data
        assert "price" in data
        assert "description" in data
        assert "imageUrl" in data
        assert "location" in data
        assert "published" in data
        assert "rating" in data
        assert "genreId" in data
        assert "createdAt" in data
        assert "reviews" in data
        assert "genre" in data


    def test_get_movies(
            self,
            unauthenticated_api_manager: ApiManager,
            valid_filter_params: dict
        ):

        page_size = valid_filter_params["pageSize"]
        
        response = unauthenticated_api_manager.movies_api.get_movies(
            params=valid_filter_params, 
            expected_status=200
        )

        data = response.json()
        movies = data["movies"]
        
        assert len(movies) > 0, f"Returned empty list"
        assert page_size == data["pageSize"], f"pageSize mismatch"
        assert "id" in movies[0], (
            f"No ID in movies[0], did you get the correct list in response?"
        )
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


    def test_get_movies_by_price(
            self,
            unauthenticated_api_manager: ApiManager,
            valid_price_filter: dict
        ):

        params = valid_price_filter
        min_price = params["minPrice"]
        max_price = params["maxPrice"]

        response = unauthenticated_api_manager.movies_api.get_movies(
            params=params, 
            expected_status=200
        )
        
        data = response.json()
        movies = data["movies"]

        for movie in movies:
            assert movie["price"] >= min_price, (
                f"Price out of specified range. Look at min_price"
            )
            assert movie["price"] <= max_price, (
                f"Price out of specified range. Look at max_price"
            )


    def test_get_movies_asc(
            self,
            unauthenticated_api_manager: ApiManager,
            asc_filter: dict
        ):
        
        response = unauthenticated_api_manager.movies_api.get_movies(
            params=asc_filter,
            expected_status=200
        )

        data = response.json()
        movies = data["movies"]
        
        previous = "1900-05-26T11:00:15.900Z"
        
        for movie in movies:
            
            assert "createdAt" in movie, (f"No createdAt in movie.")
            current = movie["createdAt"]
            assert current >= previous, f"createdAt sorting broken: {current} < {previous}"
            previous = current


    def test_get_movies_desc(
            self,
            unauthenticated_api_manager: ApiManager,
            desc_filter: dict
        ):
        
        response = unauthenticated_api_manager.movies_api.get_movies(
            params=desc_filter,
            expected_status=200
        )

        data = response.json()
        movies = data["movies"]
        
        previous = "2500-05-26T11:00:15.900Z"
        
        for movie in movies:
            
            assert "createdAt" in movie, (f"No createdAt in movie.")
            current = movie["createdAt"]
            assert current < iso_now(), f"CreatedAt is > than current time. Double-check."
            assert current <= previous, f"createdAt sorting broken: {current} > {previous}"
            previous = current

class TestEditMovies:   

    def test_create_movie(self, create_test_movie):

        assert "id" in create_test_movie
        assert "name" in create_test_movie
        assert "price" in create_test_movie
        assert "description" in create_test_movie
        assert "imageUrl" in create_test_movie
        assert "location" in create_test_movie
        assert "published" in create_test_movie
        assert "rating" in create_test_movie
        assert "genreId" in create_test_movie
        assert "createdAt" in create_test_movie
        assert "genre" in create_test_movie


    def test_patch_random_movie(
            self,
            admin_api_manager: ApiManager,
            grab_movie: int, 
            patch_movie: dict
        ):

        response = admin_api_manager.movies_api.patch_movie(
            patch_movie,
            grab_movie,
            expected_status=200
        )

        data = response.json()

        assert "name" in data, f"No name field in response."
        assert data["name"] == patch_movie["name"], (
            f"Name hasn't been patched."
        )
        assert "price" in data, f"No price field in response."
        assert data["price"] == patch_movie["price"], (
            f"Price hasn't been patched."
        )    

    def test_delete_random_movie(
            self,
            admin_api_manager: ApiManager,
            grab_movie: int
        ):

        response = admin_api_manager.movies_api.delete_movie(
            grab_movie,
            expected_status=200
        )

        data = response.json()

        assert grab_movie == data["id"]

class TestGenres:

    def test_get_genres(
            self,
            get_genres: dict
        ):

        genres = get_genres

        for genre in genres:
            assert "id" in genre
            assert "name" in genre


    #* test get random genre
    def test_get_random_genre(
            self,
            unauthenticated_api_manager: ApiManager,
            random_genre: int,
        ):

        response = unauthenticated_api_manager.movies_api.get_genre(
            random_genre,
            expected_status=200
        )

        data = response.json()

        assert "id" in data, f"No ID in data"
        assert "name" in data, f"No name in data"


    #* test genre creation
    def test_create_random_genre(
            self,
            admin_api_manager:ApiManager,
            genre_data:dict
        ):

        response = admin_api_manager.movies_api.create_genre(
            genre_data,
            expected_status=201
        )

        data = response.json()
        
        assert "id" in data
        assert "name" in data

        genre_data["id"] = data["id"]


    #* test genre deletion
    def test_delete_random_genre(
            self,
            admin_api_manager: ApiManager,
            random_genre: int
        ):

        genre_id = random_genre

        response = admin_api_manager.movies_api.delete_genre(
            genre_id,
            expected_status=200
        )

        data = response.json()

        assert "id" in data, f"No ID in data"
        assert "name" in data, f"No name in data"

class TestReviews:

    def test_post_movie_review_as_admin(
            self,
            admin_api_manager: ApiManager,
            movie_id: int,
            generate_review: dict
        ):

        response = admin_api_manager.movies_api.post_review(
            movie_id=movie_id,
            data = generate_review,
            expected_status=201
        )

        data = response.json()

        assert "userId" in data
        assert generate_review["text"] == data["text"]
        assert generate_review["rating"] == data["rating"]
        assert "createdAt" in data
        assert "user" in data

        generate_review["movieId"] = movie_id
        generate_review["userId"] = data["userId"]

    def test_movie_review_as_user(
            self,
            user_api_manager: ApiManager,
            movie_id: int,
            generate_review: dict
        ):

        response = user_api_manager.movies_api.post_review(
            movie_id=movie_id,
            data = generate_review,
            expected_status=201
        )

        data = response.json()

        assert "userId" in data
        assert generate_review["text"] == data["text"]
        assert generate_review["rating"] == data["rating"]
        assert "createdAt" in data
        assert "user" in data
        generate_review["movieId"] = movie_id
        generate_review["userId"] = data["userId"]