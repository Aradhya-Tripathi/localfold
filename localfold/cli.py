import configparser
import os
import shlex
import subprocess

import fire
import requests


def check_dir() -> None:
    in_directory = False
    for file in os.scandir("."):
        if file.name == "server":
            in_directory = True
            break

    return in_directory


class Manager:
    def __init__(self) -> None:
        self.config_path = "server-config.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

    def save_config(self) -> None:
        with open(self.config_path, "w+") as f:
            self.config.write(f)

    def start_django(self) -> None:
        """Start django processing server"""

        if self.config.has_option("DJANGO", "pid"):
            print("Django server is running!")
            return

        django_out = open("./log-django.log", "w+")
        django_error = open("./log-error-django.log", "w+")

        process = subprocess.Popen(
            shlex.split("python server/manage.py runserver"),
            stdout=django_out,
            stderr=django_error,
        )
        if not self.config.has_section("DJANGO"):
            self.config.add_section("DJANGO")

        self.config["DJANGO"]["pid"] = str(process.pid)
        self.save_config()

    def start_celery(self) -> None:
        if self.config.has_option("CELERY", "pid"):
            print("Celery server is running!")
            return

        celery_out = open("./log-celery.log", "w+")
        celery_error = open("./log-error-celery.log", "w+")

        process = subprocess.Popen(
            shlex.split(
                "celery -A core worker --pool=prefork --loglevel=INFO -n AF-Predictions -Q AF-Predictions-Queue"
            ),
            stdout=celery_out,
            stderr=celery_error,
            cwd="./server",
        )
        if not self.config.has_section("CELERY"):
            self.config.add_section("CELERY")

        self.config["CELERY"]["pid"] = str(process.pid)
        self.save_config()

    def start_client(self) -> None:
        """Currently starting the client using dev"""
        check_server = True
        self.start_django()
        self.start_celery()

        while check_server:
            try:
                requests.get("http://localhost:8000/get-tasks")
                check_server = False
            except requests.exceptions.ConnectionError:
                pass

        if self.config.has_option("CLIENT", "pid"):
            print(("Instance of the app is already running"))
            return

        client_out = open("./log-client.log", "w+")
        client_error = open("./log-error-client.log", "w+")

        # This process is automatically closed when the client side is closed
        subprocess.Popen(
            shlex.split("npm run dev"),
            stdout=client_out,
            stderr=client_error,
            cwd="../ui",
        )

    def kill_django(self) -> None:
        if not self.config.has_option("DJANGO", "pid"):
            print("Django server not running")
            return

        subprocess.call(["kill", self.config["DJANGO"]["pid"]])
        print(f"Killed django server running on: {self.config['DJANGO']['pid']}")
        self.config.remove_option("DJANGO", "pid")
        self.save_config()

    def kill_celery(self) -> None:
        if not self.config.has_option("CELERY", "pid"):
            print("Celery server not running")
            return

        subprocess.call(["kill", self.config["CELERY"]["pid"]])
        print(f"Killed celery server running on: {self.config['CELERY']['pid']}")
        self.config.remove_option("CELERY", "pid")
        self.save_config()

    def clear_logs(self) -> None:
        for file in os.scandir("."):
            if file.name.endswith(".log"):
                os.remove(file.path)

    def list(self) -> None:
        if self.config.has_option("DJANGO", "pid"):
            print(f"Django Running on: {self.config['DJANGO']['pid']}")

        if self.config.has_option("CELERY", "pid"):
            print(f"Celery Running on: {self.config['CELERY']['pid']}")

    def kill_all(self) -> None:
        self.kill_django()
        self.kill_celery()


def main():
    if not check_dir():
        print("Foul Exiting!")
        return

    manager = Manager()
    fire.Fire(
        {
            # "start-django": manager.start_django,
            "kill-django": manager.kill_django,
            # "start-celery": manager.start_celery,
            "kill-celery": manager.kill_celery,
            "clear-logs": manager.clear_logs,
            "start-client": manager.start_client,
            "kill-all": manager.kill_all,
            "list": manager.list,
        }
    )


if __name__ == "__main__":
    main()