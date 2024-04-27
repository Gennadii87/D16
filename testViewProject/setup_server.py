import asyncio
import os
import subprocess
import sys


async def setup_server():
    # Путь к интерпретатору Python внутри виртуальной среды
    python_interpreter = sys.executable

    # Путь к manage.py
    manage_py_path = os.path.join(os.getcwd(), "manage.py")

    print("Запускаем сервер Django для создания файла базы данных...")
    django_server = await asyncio.create_subprocess_exec(
        python_interpreter, manage_py_path, "runserver",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    await asyncio.sleep(5)
    django_server.terminate()
    await django_server.wait()

    print("Файл db.sqlite3 обнаружен. Создаем миграции...")
    subprocess.run([python_interpreter, manage_py_path, "makemigrations"])
    print("Миграции созданы.")
    print("Применяем миграции...")
    subprocess.run([python_interpreter, manage_py_path, "migrate"])

    print("Создаем суперпользователя...")
    # Задаем пароль суперпользователя через переменную окружения
    os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"
    subprocess.run(
        [python_interpreter, manage_py_path, "createsuperuser", "--username", "admin", "--email", "admin@example.com", "--noinput"]
    )
    print("Суперпользователь создан. Логин: admin, Пароль: admin")

    print("Запускаем сервер Django снова...")
    subprocess.run([python_interpreter, manage_py_path, "runserver"])


async def main():
    await setup_server()

if __name__ == "__main__":
    asyncio.run(main())
