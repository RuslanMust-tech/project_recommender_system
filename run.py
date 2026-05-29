#!/usr/bin/env python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,  # Автоматическая перезагрузка при изменениях
        log_level="info"
    )