from custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru")
        self.session = session
        
    def get_user_info(self, user_id, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
        
    def delete_user(self, user_id, expected_status=200):
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
        
        
