"""Server for hosting the game."""

from __future__ import annotations

__all__ = tuple()

import logging

from starlette.applications import Starlette
from starlette.config import Config
import uvicorn

logger = logging.getLogger(__name__)

app = Starlette(debug=Config('.env').get('DEBUG', bool, False))


if __name__ == '__main__':
    uvicorn.run(f'{__name__}:app',
                host='127.0.0.1',
                port=5000,
                log_level='debug',
                reload=Config('.env').get('DEBUG', bool, False))
