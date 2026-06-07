"""Module with security issues for testing."""

import subprocess

api_key = "sk-1234567890abcdef1234567890abcdef"
password = "supersecretpassword123"
secret = "my_secret_token_value_1234"


def run_command(user_input):
    """Run a shell command unsafely."""
    subprocess.call(user_input, shell=True)


def get_data(user_id):
    """Unsafe SQL query construction."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query


def process(code):
    """Use of eval."""
    return eval(code)


def another_sql(name):
    """Another SQL injection via .format()."""
    query = "SELECT * FROM users WHERE name = '{}'".format(name)
    return query
