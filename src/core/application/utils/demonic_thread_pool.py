from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.thread import _global_shutdown_lock, _python_exit, _threads_queues, _worker
from typing import Any
from weakref import ReferenceType

import threading
import concurrent.futures.thread

from src.core.application.types import ThreadWorkQueueType

_threading_atexits = threading._threading_atexits  # type: ignore
_register_atexit = threading._register_atexit  # type: ignore


def python_exit_without_joins():
    with _global_shutdown_lock:
        concurrent.futures.thread._shutdown = True

    thread_queues = list(_threads_queues.values())
    for thread_queue in thread_queues:
        thread_queue.put(None)


class DemonicThreadPoolExecutor(ThreadPoolExecutor):
    """
    Thread pool optionally utilizing daemon threads
    for task execution.
    """

    def __init__(
        self,
        max_workers: int | None = None,
        thread_name_prefix: str = "",
        initializer: Callable[..., Any] | None = None,
        initargs: tuple = tuple(),
        daemon: bool = False,
    ):
        self._work_queue: ThreadWorkQueueType
        self._threads: set[threading.Thread]
        super().__init__(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=initializer,
            initargs=initargs,
        )

        self._daemon = daemon
        if self._daemon:
            self._replace_python_exit()

    def _adjust_thread_count(self):
        if self._idle_semaphore.acquire(timeout=0):
            return

        def weakref_cb(_, q: ThreadWorkQueueType = self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = f"{self._thread_name_prefix or self}_{num_threads}"
            thread = threading.Thread(
                name=thread_name,
                target=_worker,
                args=(
                    ReferenceType(self, weakref_cb),
                    self._work_queue,
                    self._initializer,
                    self._initargs,
                ),
                daemon=self._daemon,
            )

            thread.start()
            self._threads.add(thread)

            _threads_queues[thread] = self._work_queue  # type: ignore

    def _replace_python_exit(self):
        for lambda_func in _threading_atexits:
            if lambda_func.__closure__:
                for cell in lambda_func.__closure__:
                    if cell.cell_contents is _python_exit:
                        _threading_atexits.remove(lambda_func)

        _register_atexit(python_exit_without_joins)
