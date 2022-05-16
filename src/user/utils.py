import hashlib


def get_registration_complete_email_template(
    activation_link: str,
):
    # TODO: мб добавить жинжу сюда? Пока впадлу
    return '<h2>Thank you for registring in our service! ' \
        f'<a href="{activation_link}">Click here</a> to activate your profile</h2>'


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()
