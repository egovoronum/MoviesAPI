# collections, roles, statuses, fixed strings, limits, timeouts, default values

# DONT PUT SESITIVE DATA IN constants or .env, I do this for training purposes only
BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
MOVIES_ENDPOINT = "/movies"
LOGOUT_ENDPOINT = "/logout"
