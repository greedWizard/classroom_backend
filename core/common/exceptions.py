from dataclasses import dataclass
from typing import Union


@dataclass
class ServiceError(Exception):
    status_code: int
    errors: dict[str, Union[list, dict]]
