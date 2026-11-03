from pymodm import MongoModel, fields


class Image(MongoModel):
    check_id = fields.ListField(field=fields.CharField(), default=list)
    document_id = fields.CharField(blank=True)
    caption = fields.CharField(default='')
    image_data = fields.BinaryField(blank=True)
    image_size = fields.ListField(blank=True)
    text = fields.CharField(blank=True)
    page = fields.IntegerField(blank=True)
    checksum = fields.CharField(blank=True)
    laplacian_score = fields.FloatField(blank=True)
    entropy_score = fields.FloatField(blank=True)
    text_density = fields.FloatField(blank=True)
    symbols_percentage = fields.FloatField(blank=True)

    @property
    def active_check_id(self):
        return getattr(self, '_active_check_id', None)

    @active_check_id.setter
    def active_check_id(self, check_id):
        self._active_check_id = str(check_id)

    class Meta:
        collection_name = 'images'
        final = True
