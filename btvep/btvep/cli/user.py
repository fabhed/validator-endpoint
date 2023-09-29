import typer
from tabulate import tabulate

from btvep.db.user import User

app = typer.Typer(help="Manage users.")

@app.callback(no_args_is_help=True)
def main():
    pass

@app.command("list")
def list_users():
    all_users = User.select()
    for user in all_users:
        print(f"id: {user.id} /admin: {user.is_admin}")

@app.command("edit")
def edit_user(
    user_id: str = typer.Argument(..., help="User ID"),
    is_admin: bool = typer.Option(..., help="Option --is-admin OR --no-is-admin"),
):
    try:
        user = User.get(User.id == user_id)
        user.is_admin = is_admin
        user.save()
        print(f"User updated.")
    except User.DoesNotExist:
        print(f"User {user_id} not found.")
