import os
from typing import Dict

from autodb.abc.database import Database
from ..errors import DatabaseNotFound
from ..table import PersistentTable
from ..utils.path import load_tables


class DiskDatabase(Database):

    """Persistent implementation of the AutoDB interface."""

    def __init__(self, directory: str):
        self.tables: Dict[object, PersistentTable] = {}
        self.directory = directory
        if not os.path.exists(directory):
            os.mkdir(directory)
        if os.path.exists(directory):
            try:
                for table in load_tables(directory):
                    table = PersistentTable._from_file(table)
                    self.tables.update({table.table_type: table})
            except DatabaseNotFound:
                pass

    def __iter__(self):
        """Returns the various table types that this database contains."""
        return iter(self.tables.keys())

    def __len__(self):
        """Returns the number of objects contained in this database."""
        return sum(len(table) for table in self.tables.values())

    def __repr__(self):
        return f"DiskDatabase({self.directory})"

    def insert(self, item: object) -> None:
        """Inserts an arbitrary Python class into the database. Do not use this
        database to store raw types."""
        class_name = type(item)
        try:
            self.tables[class_name]._insert(item)
        except KeyError:
            self.tables.update(
                {class_name: PersistentTable._new(os.path.join(self.directory, hex(abs(hash(class_name)))),
                                                  table_type=class_name)})
            self.tables[class_name]._insert(item)

    def batch_insert(self, items: list) -> None:
        """Inserts a list of similar Python class into the database."""
        if len(items) == 0:
            return
        else:
            first_item_type = type(items[0])
            try:
                self.tables[first_item_type]._batch_insert(items)
            except KeyError:
                self.tables.update(
                    {first_item_type: PersistentTable._new(os.path.join(self.directory, first_item_type.__name__),
                                                           table_type=first_item_type)})
                self.tables[first_item_type]._batch_insert(items)

    def select(self, cls):
        """Retrieves the table that contains classes of the given type."""
        if cls in self.tables:
            return self.tables[cls]
        else:
            raise KeyError(f"No table of {cls} exists in this database!")
