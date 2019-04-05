from ..table import Table

from typing import List, Dict, Optional


class MemoryDatabase:
    """In memory implementation of the AutoDB interface."""

    def __init__(self) -> None:
        self.class_map: Dict[object, Table] = {}

    def __len__(self):
        return sum((len(table) for table in self.class_map.values()))

    def insert(self, complex_object: object):
        class_type = type(complex_object)
        if class_type not in self.class_map:
            self.class_map.update({class_type: Table()})
        self.class_map[class_type].insert(complex_object)

    def retrieve(self, class_type=None, **kwargs) -> List[object]:
        if class_type is None:
            results = []
            for table in self.class_map.values():
                try:
                    table_results = table.retrieve(**kwargs)
                except IndexError:
                    continue
                if table_results is not None:
                    results.extend(table_results)
            if results:
                return results
        else:
            if class_type not in self.class_map:
                raise IndexError
            return self.class_map[class_type].retrieve(**kwargs)
