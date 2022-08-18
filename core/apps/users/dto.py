from dataclasses import dataclass


@dataclass
class UserTokenResultDTO:
    timed_token: str
    activation_token: str
    user_email: str
