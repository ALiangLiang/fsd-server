class User:
    def __init__(self, name: str, rating: int, account: str):
        self.name = name
        self.rating = rating
        self.account = account


class Bot(User):
    def __init__(self):
        super().__init__('A bot', 4)
