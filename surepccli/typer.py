import asyncio
import functools
import inspect
import os
from functools import partial
from functools import wraps
from typing import Any
from typing import Callable

import typer

from surepccli.const import Envs


class AsyncTyper(typer.Typer):
    def __init__(self, login_required: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_required = login_required

    @staticmethod
    def maybe_run_async(decorator: Callable, func: Callable) -> Any:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            def runner(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(func(*args, **kwargs))

            decorator(runner)
        else:
            decorator(func)
        return func

    def callback(self, *args: Any, **kwargs: Any) -> Any:
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args: Any, login_required=False, **kwargs: Any) -> Any:
        decorator = super().command(*args, **kwargs)

        def wrap_func(func):
            if self.login_required or login_required:
                func = self.require_login(func)
            return decorator(func)

        return partial(self.maybe_run_async, wrap_func)

    def require_login(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not os.getenv(Envs.TOKEN):
                typer.echo("You are not logged in. Please run: surepccli account login <email> <password>")
                raise typer.Exit(code=1)
            return func(*args, **kwargs)

        return wrapper
