import time
from datetime import datetime

current_timestamp = int(time.time())
human_readable_timestamp = datetime.utcfromtimestamp(current_timestamp).strftime('%Y-%m-%d-%H')
print(human_readable_timestamp)
