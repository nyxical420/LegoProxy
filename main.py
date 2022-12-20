from os import system
system("uvicorn server:app --reload --port 443 --host 0.0.0.0")
