import json

from bot_handler.models import StorageTable


# todo another with dynamic table creation))))
class StorageC(dict):
    def __init__(self, name=None, user=None, peer=None, cmd=None, load=True, obj=None, obj_field='data'):
        self.loaded = 0
        self.name = name
        self.user = user
        self.peer = peer
        self.cmd = cmd
        self.obj_field = obj_field
        self.storage_table = None
        if obj:
            self.storage_table = obj
            self.is_created = False

        super(StorageC, self).__init__({})

        if load:
            self._load()

    def _load(self):
        if not self.storage_table:
            self.storage_table, self.is_created = StorageTable.objects.get_or_create(name=self.name, user=self.user,
                                                                                     peer=self.peer,
                                                                                     cmd=self.cmd)
        data = self.storage_table.__getattribute__(self.obj_field)
        if not data:
            data = {}
        else:
            data = json.loads(data)
        super(StorageC, self).clear()
        super(StorageC, self).update(data)
        self.loaded = 1
        return 1

    def save(self):
        self.storage_table.__setattr__(self.obj_field, json.dumps(super(StorageC, self).copy()))
        self.storage_table.save(update_fields=[self.obj_field])

    def delete(self):
        self.storage_table.delete()

    def refresh_from_db(self):
        if not self.loaded:
            return self._load()
        self.storage_table.refresh_from_db(fields=[self.obj_field])
        data = self.storage_table.data
        if not data:
            data = {}
        else:
            data = json.loads(data)
        super(StorageC, self).clear()
        super(StorageC, self).update(data)
        return 1
