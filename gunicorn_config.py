# gunicorn_config.py
import multiprocessing

bind = "127.0.0.1:9000"  # Or your desired IP and port
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
timeout = 60
