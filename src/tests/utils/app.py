from core.factory import AppFactory


app = AppFactory.create_app(test_mode=True)
