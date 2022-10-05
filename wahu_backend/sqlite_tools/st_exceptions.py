class SqliteTableEditingError(Exception):
    pass


class SqliteTableEditingKeyError(SqliteTableEditingError):

    def __init__(self, supplied_keys: list[str], table_heads: list[str]):
        self.supplied_keys = supplied_keys
        self.table_heads = table_heads

    def __str__(self):
        return f'键 {self.supplied_keys} 不包含在该表的表头 {self.table_heads} 中'


class SqliteTableEditingMutateIndex(SqliteTableEditingError):

    def __init__(self, index_name: str):
        self.index_name = index_name

    def __str__(self):
        return f'试图更改索引列 {self.index_name} 的值'


class SqliteTableDoesntExist(SqliteTableEditingError):

    def __init__(self, requested_name: str, available: list[str]):
        self.requested_name = requested_name
        self.available = available

    def __str__(self):
        return f'向 SqliteTableEditors 请求了不存在的表 {self.requested_name}\n' \
               f'可用的表： {self.available}'


class SqliteTableStoreConfigError(SqliteTableEditingError):
    def __init__(self, msg: str):
        self.msg = msg
    
    def __str__(self) -> str:
        return self.msg
