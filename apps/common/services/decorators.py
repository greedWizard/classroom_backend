def action(method):
    def inner(self, *args, **kwargs):
        self.action = method.__name__
        return method(self, *args, **kwargs)

    return inner
