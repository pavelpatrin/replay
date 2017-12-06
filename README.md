# Replay
Simple access log player

Usage:

    python -m replay --target 'http://127.0.0.1:8000' --log-file access.json
    python -m replay --target 'http://127.0.0.1:8000' --log-file access.json --logging DEBUG
    python -m replay --target 'http://127.0.0.1:8000' --log-file access.json --parallel 10
    python -m replay --target 'http://127.0.0.1:8000' --log-file access.json --filters '{"user_id":123456}'