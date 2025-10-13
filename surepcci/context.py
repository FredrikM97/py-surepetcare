import asyncio
import functools
import json
import os
from typing import Optional

import click

from surepcio.client import SurePetcareClient

SESSION_FILE = os.path.expanduser("~/.surepcci_session")


class Context:
    """Context for CLI commands."""

    household_id: int
    client: SurePetcareClient
    token: Optional[str]
    device_id: Optional[str]

    def __init__(self, home=None):
        self.home = os.path.abspath(home or ".")

    def __enter__(self):
        """Initialize context, load session if available."""
        session = self.load_session()
        if not session:
            raise click.ClickException("No session active")

        self.token = session.get("token")
        self.device_id = session.get("device_id")
        self.household_id = session.get("household_id")

        if self.token and self.device_id:
            self.client = SurePetcareClient()
            try:
                self.client._token = self.token
                self.client._device_id = self.device_id
            except Exception as e:
                click.echo(f"Failed to auto-login: {e}")
                raise click.ClickException("Not logged in.")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """Cleanup context, close client if needed."""
        asyncio.run(self.client.close())

    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        if self.client is None or not getattr(self.client, "_token", None):
            click.echo("You are not logged in. Please run: surepcci login <email> <password>")
            raise click.ClickException("Not logged in.")
        return True

    @staticmethod
    def save_session(**kwargs) -> None:
        """Save session data to file."""
        session = {}
        # Load existing session if it exists
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE) as f:
                session = json.load(f)
        # Update with new values
        session.update(**kwargs)
        with open(SESSION_FILE, "w") as f:
            json.dump(session, f)

    @staticmethod
    def load_session():
        """Load session data from file."""
        with open(SESSION_FILE) as f:
            return json.load(f)

    @staticmethod
    def clear_session(key: Optional[str] = None) -> None:
        """Clear a specific key or the entire session file."""
        if not os.path.exists(SESSION_FILE):
            return
        if key is None:
            os.remove(SESSION_FILE)
        else:
            with open(SESSION_FILE) as f:
                session = json.load(f)
            session.pop(key, None)
            with open(SESSION_FILE, "w") as f:
                json.dump(session, f)


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """SurePetcare CLI root."""
    ctx.obj = ctx.with_resource(Context(SESSION_FILE))


def async_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def print_table(rows, headers):
    """Reusable function to print a compact, aligned table."""
    col_widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
    header_line = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    click.echo(header_line)
    click.echo("-" * len(header_line))
    for row in rows:
        click.echo(" | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row))))
