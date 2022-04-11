import os

for i in range(0, 25):
    os.system("curl -X POST http://localhost:8000/al-wars/persisted/" + str(i))
