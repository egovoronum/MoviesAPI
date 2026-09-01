import requests
from custom_requester.custom_requester import CustomRequester
from constants import AUTH_URL

class UserAPI(CustomRequester):
    def __init__(self, session: requests.Session):
        super().__init__(session=session, base_url=AUTH_URL)
        self.session = session
        
    def get_user_info(self, user_id:int, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
        
    def delete_user(self, user_id:str, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint=f"/user",
            data=user_data,
            expected_status=expected_status
        )
        
