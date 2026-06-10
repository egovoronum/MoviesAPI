from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT, AUTH_URL
from custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    
    def __init__(self, session, base_url):
        super().__init__(
            session=session, 
            base_url=AUTH_URL
        )
    
    def register_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            base_url=AUTH_URL,
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )
        
    def login_user(self, login_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            base_url=AUTH_URL,
            data=login_data,
            expected_status=expected_status
        )
        
            
