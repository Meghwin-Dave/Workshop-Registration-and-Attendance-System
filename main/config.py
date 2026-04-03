class Config:
    def __init__(self):
        # self._base_url ="https://workshop-registration.icretegy.com"
        self._base_url ="http://127.0.0.1:8000"
    @property
    def base_url(self):
        return self._base_url
    
    @base_url.setter
    def base_url(self, value):
        self._base_url = value

config = Config()