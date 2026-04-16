#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    API/__INIT__.PY - v2026.∞                                 ║
║                  Gmail Infinity Factory - Quantum API Core                   ║
║                         Author: ARCHITECT-GMAIL                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

"""
GMAIL INFINITY FACTORY - API LAYER

This quantum API core provides:
    🔥 RESTful control interface (FastAPI)
    🔥 Real-time WebSocket status streaming
    🔥 Interactive monitoring dashboard (Streamlit)
    🔥 Distributed task queue (Celery + Redis)
    🔥 JWT authentication & rate limiting
    🔥 Live creation statistics & analytics

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │                    LOAD BALANCER                        │
    └─────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┬─────────────┬──────────┐
        │                           │             │          │
    ┌───▼───┐                  ┌────▼────┐   ┌───▼───┐  ┌───▼───┐
    │ FastAPI│                  │WebSocket│   │Streamlit│  │Celery │
    │ REST  │                  │  Realtime│   │Dashboard│  │Worker │
    └───┬───┘                  └────┬────┘   └───┬───┘  └───┬───┘
        │                           │             │          │
        └───────────────────────────┼─────────────┼──────────┘
                                    │             │
                            ┌───────▼─────────────▼───────┐
                            │         REDIS CACHE         │
                            └───────┬─────────────────────┘
                                    │
                            ┌───────▼───────┐
                            │   POSTGRES    │
                            │   DATABASE    │
                            └───────────────┘

All endpoints are rate-limited and JWT-protected.
Creation tasks are distributed across worker nodes.
"""

try:
    from .rest_server import app, start_api_server, get_task_status, cancel_task
except ImportError:
    app = start_api_server = get_task_status = cancel_task = None

try:
    from .websocket_handler import websocket_endpoint, manager, ConnectionManager
except ImportError:
    websocket_endpoint = manager = ConnectionManager = None

try:
    from .dashboard import create_dashboard, run_dashboard
except ImportError:
    create_dashboard = run_dashboard = None

__version__ = "2026.∞.1"
__author__ = "ARCHITECT-GMAIL"
__license__ = "Quantum Proprietary"

__all__ = [
    # FastAPI application
    "app",
    "start_api_server",
    "get_task_status",
    "cancel_task",
    
    # WebSocket handlers
    "websocket_endpoint",
    "manager",
    "ConnectionManager",
    
    # Dashboard
    "create_dashboard",
    "run_dashboard",
]

# API configuration constants
API_TITLE = "GMAIL INFINITY FACTORY - QUANTUM API"
API_VERSION = "2026.∞"
API_DESCRIPTION = """
## 🔥 Gmail Creation at Quantum Speed

This API provides programmatic access to the Gmail Infinity Factory.

### 🚀 Features:
- **Account Creation** - Create Gmail accounts with quantum stealth
- **Bulk Operations** - Mass generation with intelligent rate limiting
- **Real-time Status** - WebSocket streaming for live progress
- **Analytics** - Comprehensive creation statistics
- **Proxy Management** - Automatic proxy health checking
- **Fingerprint Rotation** - 50,000+ unique device signatures

### 🔐 Authentication:
All endpoints require JWT Bearer token authentication.
Obtain your token via the `/auth/login` endpoint.

### 📊 Rate Limits:
- Free tier: 10 requests/minute
- Premium: 100 requests/minute
- Enterprise: Unlimited

### 💎 Response Format:
All responses follow JSON:API specification.
"""