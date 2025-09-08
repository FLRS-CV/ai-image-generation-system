#!/usr/bin/env python3
"""
Run the API Key Manager server
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting API Key Manager Server...")
    print("📍 Server listening on: 0.0.0.0:8004")
    print("🌐 Access via: http://localhost:8004")
    print("📍 Server will be available at: http://localhost:8004")
    print("🔑 API Documentation: http://localhost:8004/docs")
    print("📖 Interactive API docs: http://localhost:8004/redoc")
    print("="*60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",# 0.0.0.0 binds all interfaces (like 127.0.0.1:8004, localhost:8004)
        port=8004,
        reload=True,
        log_level="info"
    )
