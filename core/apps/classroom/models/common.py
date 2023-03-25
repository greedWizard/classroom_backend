class AttachmentsCountMixin:
    @property
    def attachments_count(self) -> int:
        return len(self.attachments)
