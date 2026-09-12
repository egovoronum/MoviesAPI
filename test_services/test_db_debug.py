def test_db_requests(db_helper, created_test_dbuser):
    assert created_test_dbuser == db_helper.get_user_by_id(created_test_dbuser.id)
    assert db_helper.user_exists_by_email("api1@gmail.com")

def test_movie_db_deletion(db_helper, db_movie_data):
    assert db_movie_data == db_helper.get_movie_by_id(db_movie_data.id)
