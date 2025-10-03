from pymilvus import connections
import time

for attempt in range(15):
    try:
        connections.connect('default', host='127.0.0.1', port='19530', timeout=20)
        print('Connected successfully')
        break
    except Exception as e:
        print(f'Attempt {attempt + 1} failed: {e}')
        time.sleep(10)
else:
    print('Failed to connect after 15 attempts')
