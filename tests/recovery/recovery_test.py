import requests
import time
import subprocess
import os

def get_process_id_using_port(port):
    try:
        pid = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode('utf-8').strip()
        return pid
    except subprocess.CalledProcessError:
        return None

def stop_server(port):
    pid = get_process_id_using_port(port)
    if pid:
        print(f"Останавливаем сервер с PID {pid}...")
        start = time.time()
        subprocess.run(["kill", pid])
        time.sleep(5)
        duration = time.time() - start
        print(f"Сервер остановлен за {duration:.2f} сек")
        return duration
    else:
        print("Сервер не найден")
        return 0

def start_server():
    print("Запускаем сервер...")
    start = time.time()
    subprocess.Popen(["uvicorn", "src.app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    time.sleep(10)
    duration = time.time() - start
    print(f"Сервер запущен за {duration:.2f} сек")
    return duration

def measure_api_response_time(url):
    start = time.time()
    response = requests.get(url)
    duration = time.time() - start
    return response, duration

def test_recovery():
    session = requests.Session()

    print("Создаём данные до сбоя...")
    create_url = "http://localhost:8000/rest/createPlaylist?name=playlist&username=admin&u=admin&p=admin"
    response, create_time = measure_api_response_time(create_url)
    print(f"Ответ на создание плейлиста: {response.status_code}")
    print(f"Ответное тело: {response.text}")
    print(f"Время ответа API при создании: {create_time:.2f} сек")
    assert response.status_code == 200

    stop_time = stop_server(8000)

    start_time = start_server()

    print("Проверяем восстановление данных после сбоя...")
    get_url = "http://localhost:8000/rest/getPlaylists?username=admin&u=admin&p=admin"
    response, get_time = measure_api_response_time(get_url)
    print(f"Ответ на запрос получения плейлистов: {response.status_code}")
    print(f"Ответное тело: {response.text}")
    print(f"Время ответа API после восстановления: {get_time:.2f} сек")

    assert response.status_code == 200
    assert "playlist" in response.text

    total_recovery_time = stop_time + start_time
    print(f"\nВремя остановки сервера: {stop_time:.2f} сек")
    print(f"Время запуска сервера: {start_time:.2f} сек")
    print(f"Общее время восстановления: {total_recovery_time:.2f} сек")
    print(f"Время ответа API при создании: {create_time:.2f} сек")
    print(f"Время ответа API после восстановления: {get_time:.2f} сек\n")
    print("Тест восстановления прошёл успешно")

test_recovery()
