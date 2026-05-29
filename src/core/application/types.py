from concurrent.futures.thread import _WorkItem
from queue import SimpleQueue
from typing import Any, TypeAlias

ThreadWorkQueueType: TypeAlias = SimpleQueue[_WorkItem[Any] | None]
