from typing import TypeAlias, Any, Union

HTTPHeaders: TypeAlias = dict[str, str]
URLParams: TypeAlias = dict[str, "Any[list['Any[str, int]'], int, str]"]


JSONItem: TypeAlias = Union[str, int, bool, float, list['JSONItem'], dict[str, 'JSONItem'], None]

HTTPData: TypeAlias = dict[str, JSONItem]
