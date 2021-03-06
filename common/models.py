from tortoise import (
    fields,
    models,
)


class TimeStampAbstract(models.Model):
    created_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AuthorAbstract(models.Model):
    author = fields.ForeignKeyField(
        'models.User',
        on_delete=fields.RESTRICT,
        related_name=False,
    )
    updated_by = fields.ForeignKeyField(
        'models.User',
        on_delete=fields.RESTRICT,
        related_name=False,
    )

    class Meta:
        abstract = True
