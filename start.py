from uvicorn import run

if __name__ == "__main__":
    run("server:app", host="0.0.0.0", port=443, reload=True)
