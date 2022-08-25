def action(method):
    def inner(self, *args, **kwargs):
        previous_action, self.action = self.action, method.__name__

        method_result = method(self, *args, **kwargs)

        if previous_action:
            self.action = previous_action
        return method_result
    return inner
