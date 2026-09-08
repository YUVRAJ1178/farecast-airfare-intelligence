"""
Runner script for Airfare Intelligence Platform with Windows SelectorEventLoop
to prevent IOCP WinError 64 connection resets.
"""
import sys, os, asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, log_level="info")
