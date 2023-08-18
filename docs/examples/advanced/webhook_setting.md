```python
import os

# получать обновления через webhook
USE_WEBHOOK = os.getenv('USE_WEBHOOK', '').lower() == 'true'

# номер порта, на котором будет прослушиваться входящий трафик
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5000'))

# IP-адрес или имя хоста, на котором будет работать сервер
WEBHOOK_LISTEN = os.getenv('WEBHOOK_LISTEN', 'example.com')

# путь, по которому Telegram будет отправлять обновления боту
WEBHOOK_URL_PATH = os.getenv('WEBHOOK_URL_PATH', '')

# (опционально) полный URL, который Telegram будет использовать для отправки обновлений
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://example.com')
```
