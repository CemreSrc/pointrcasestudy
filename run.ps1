param(
    [string]$AppHost = "127.0.0.1",
    [int]$AppPort = 8000
)

# Use the interpreter from your venv
& "C:/Users/asus/Desktop/pointr_Cemre/pointr/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload --host $AppHost --port $AppPort
