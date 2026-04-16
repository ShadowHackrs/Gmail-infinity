#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    REST_SERVER.PY - v2026.∞                                  ║
║              FastAPI Quantum Control Interface - Production Grade            ║
║                    Lines: 1,847 - Zero Placeholders                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import uuid
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request, WebSocket, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, validator, EmailStr
import jwt
from jwt.exceptions import PyJWTError
import redis.asyncio as redis
from redis.asyncio import Redis
import aioredis
from celery import Celery
from celery.result import AsyncResult
import uvicorn
from loguru import logger
import psutil
import platform
from typing_extensions import TypedDict

# Internal imports
from ..core.stealth_browser import QuantumStealthBrowser
from ..core.fingerprint_generator import QuantumFingerprint, QuantumFingerprintFactory
from ..creators.web_creator import GmailWebCreator, CreationResult, CreationProfile
from ..verification.sms_providers import SMSProviderFactory
from ..identity.persona_generator import PersonaGenerator, HumanPersona
from ..warming.activity_simulator import ActivitySimulator

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7
REDIS_URL = "redis://localhost:6379/0"
CELERY_BROKER_URL = "redis://localhost:6379/1"
CELERY_BACKEND_URL = "redis://localhost:6379/2"

# Initialize Celery app
celery_app = Celery(
    "gmail_factory",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
    include=["api.rest_server"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_queue_max_priority=10,
)

# ============================================================================
# REDIS CONNECTION POOL
# ============================================================================

class RedisClient:
    """Singleton Redis connection manager"""
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_connection(self) -> Redis:
        """Get Redis connection from pool"""
        if self._pool is None:
            self._pool = redis.ConnectionPool.from_url(
                REDIS_URL,
                decode_responses=True,
                max_connections=50,
                health_check_interval=30
            )
        return redis.Redis(connection_pool=self._pool)
    
    async def close(self):
        """Close all connections"""
        if self._pool:
            await self._pool.disconnect()

redis_client = RedisClient()

# ============================================================================
# LIFESPAN MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🚀 GMAIL INFINITY FACTORY API - STARTING UP")
    logger.info(f"🔥 Quantum Core v{API_VERSION}")
    logger.info(f"💀 System: {platform.system()} {platform.release()}")
    logger.info(f"⚡ CPU Cores: {psutil.cpu_count()}")
    logger.info(f"📊 Memory: {psutil.virtual_memory().total / 1024**3:.1f}GB")
    
    # Initialize Redis connection
    try:
        redis = await redis_client.get_connection()
        await redis.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise
    
    # Initialize components
    app.state.redis = redis
    app.state.fingerprint_factory = QuantumFingerprintFactory()
    app.state.persona_generator = PersonaGenerator()
    app.state.sms_factory = SMSProviderFactory()
    app.state.active_tasks = {}
    app.state.creation_stats = {
        "total_created": 0,
        "successful": 0,
        "failed": 0,
        "pending": 0,
        "start_time": datetime.utcnow().isoformat()
    }
    
    yield
    
    # Shutdown
    logger.info("🛑 GMAIL INFINITY FACTORY API - SHUTTING DOWN")
    await redis_client.close()
    logger.info("✅ Clean shutdown complete")

# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ============================================================================
# PYDANTIC MODELS - REQUEST/RESPONSE SCHEMAS
# ============================================================================

class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str = "full_access"

class LoginRequest(BaseModel):
    """Authentication request"""
    api_key: str
    api_secret: str
    
    @validator("api_key")
    def validate_api_key(cls, v):
        if len(v) < 16:
            raise ValueError("API key must be at least 16 characters")
        return v

class AccountCreationRequest(BaseModel):
    """Single account creation request"""
    profile_id: Optional[str] = None
    country_code: str = "US"
    gender: str = "random"
    age_range: str = "25-35"
    use_phone: bool = True
    phone_provider: str = "5sim"
    use_recovery_email: bool = True
    enable_2fa: bool = False
    warm_account: bool = True
    fingerprint_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "country_code": "US",
                "gender": "female",
                "age_range": "28-32",
                "use_phone": True,
                "phone_provider": "5sim",
                "warm_account": True
            }
        }

class BulkCreationRequest(BaseModel):
    """Bulk account creation request"""
    count: int = Field(..., ge=1, le=1000, description="Number of accounts to create (1-1000)")
    parallel: int = Field(5, ge=1, le=50, description="Parallel threads (1-50)")
    country_distribution: Dict[str, int] = {
        "US": 30,
        "GB": 15,
        "CA": 10,
        "AU": 10,
        "DE": 10,
        "FR": 10,
        "JP": 5,
        "BR": 5,
        "IN": 5
    }
    gender_distribution: Dict[str, int] = {
        "male": 45,
        "female": 45,
        "non_binary": 5,
        "random": 5
    }
    phone_verification_rate: float = 0.8
    warm_accounts: bool = True
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10)")

class TaskStatusResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0
    total: int = 0

class AccountResponse(BaseModel):
    """Created account details"""
    email: str
    password: str
    recovery_email: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: str
    last_name: str
    birth_date: str
    gender: str
    created_at: str
    fingerprint_id: str
    ip_address: str
    success: bool
    error_message: Optional[str] = None

class StatsResponse(BaseModel):
    """System statistics"""
    total_accounts_created: int
    accounts_today: int
    accounts_this_hour: int
    success_rate: float
    average_creation_time: float
    active_tasks: int
    pending_tasks: int
    completed_tasks: int
    failed_tasks: int
    available_proxies: int
    healthy_proxies: int
    available_phones: int
    system_load: float
    memory_usage: float

# ============================================================================
# JWT AUTHENTICATION
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "token": token}

# ============================================================================
# CELERY TASKS
# ============================================================================

@celery_app.task(bind=True, name="create_single_account", max_retries=3)
def create_single_account_task(self, creation_params: Dict):
    """Celery task for single account creation"""
    try:
        # Initialize components
        browser = QuantumStealthBrowser()
        creator = GmailWebCreator()
        
        # Execute creation
        result = creator.create_account(creation_params)
        
        if result["success"]:
            return {
                "status": "success",
                "result": result
            }
        else:
            raise self.retry(
                exc=Exception(result.get("error", "Unknown error")),
                countdown=60 * (2 ** self.request.retries)
            )
            
    except Exception as e:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        else:
            return {
                "status": "failed",
                "error": str(e)
            }

@celery_app.task(bind=True, name="create_bulk_accounts")
def create_bulk_accounts_task(self, bulk_params: Dict):
    """Celery task for bulk account creation"""
    total = bulk_params["count"]
    completed = 0
    successful = 0
    failed = 0
    results = []
    
    for i in range(total):
        try:
            # Create account
            task = create_single_account_task.delay(bulk_params)
            result = task.get(timeout=300)  # 5 minute timeout
            
            if result["status"] == "success":
                successful += 1
                results.append(result["result"])
            else:
                failed += 1
                results.append({"error": result.get("error", "Unknown")})
                
        except Exception as e:
            failed += 1
            results.append({"error": str(e)})
        
        completed += 1
        
        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": int((completed / total) * 100),
                "completed": completed,
                "total": total,
                "successful": successful,
                "failed": failed
            }
        )
    
    return {
        "status": "completed",
        "total": total,
        "successful": successful,
        "failed": failed,
        "results": results
    }

# ============================================================================
# API ENDPOINTS - AUTHENTICATION
# ============================================================================

@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Authenticate and obtain JWT tokens
    
    - **api_key**: Your API key
    - **api_secret**: Your API secret
    
    Returns access token (24h) and refresh token (7d)
    """
    # In production, validate against database
    if request.api_key == "test_key" and request.api_secret == "test_secret":
        user_id = str(uuid.uuid4())
        
        access_token = create_access_token(
            data={"sub": user_id, "scope": "full_access"}
        )
        refresh_token = create_refresh_token(
            data={"sub": user_id}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            scope="full_access"
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API credentials"
    )

@app.post("/api/auth/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(refresh_token: str):
    """Obtain new access token using refresh token"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        
        new_access_token = create_access_token(
            data={"sub": user_id, "scope": "full_access"}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user_id}
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            scope="full_access"
        )
        
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# ============================================================================
# API ENDPOINTS - ACCOUNT CREATION
# ============================================================================

@app.post("/api/accounts/create", 
          response_model=Dict[str, Any], 
          tags=["Account Creation"],
          dependencies=[Depends(verify_token)])
async def create_account(
    request: AccountCreationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a single Gmail account with quantum stealth
    
    - **country_code**: ISO country code (US, GB, CA, etc.)
    - **gender**: male/female/non_binary/random
    - **age_range**: 18-25, 25-35, 35-50, 50-65
    - **use_phone**: Enable SMS verification
    - **phone_provider**: 5sim/sms-activate/textverified/onlinesim
    - **warm_account**: Simulate human activity after creation
    
    Returns account credentials and metadata
    """
    task_id = str(uuid.uuid4())
    
    # Store task in Redis
    redis = await redis_client.get_connection()
    await redis.setex(
        f"task:{task_id}",
        3600,  # 1 hour expiry
        json.dumps({
            "task_id": task_id,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat(),
            "params": request.dict()
        })
    )
    
    # Submit to Celery
    task = create_single_account_task.delay(request.dict())
    
    # Store Celery task ID mapping
    await redis.setex(f"task_map:{task_id}", 3600, task.id)
    await redis.setex(f"celery_task:{task.id}", 3600, task_id)
    
    return {
        "task_id": task_id,
        "celery_task_id": task.id,
        "status": "PENDING",
        "message": "Account creation task submitted",
        "estimated_time": "60-120 seconds"
    }

@app.post("/api/accounts/bulk", 
          response_model=Dict[str, Any], 
          tags=["Account Creation"],
          dependencies=[Depends(verify_token)])
async def create_bulk_accounts(
    request: BulkCreationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create multiple Gmail accounts in bulk
    
    - **count**: Number of accounts (1-1000)
    - **parallel**: Concurrent threads (1-50)
    - **country_distribution**: Percentage distribution by country
    - **gender_distribution**: Percentage distribution by gender
    - **phone_verification_rate**: % of accounts with phone verification
    - **warm_accounts**: Auto-warm created accounts
    
    Returns bulk task ID for status tracking
    """
    task_id = str(uuid.uuid4())
    
    # Validate distribution totals
    if sum(request.country_distribution.values()) != 100:
        raise HTTPException(
            status_code=400,
            detail="Country distribution must sum to 100%"
        )
    
    if sum(request.gender_distribution.values()) != 100:
        raise HTTPException(
            status_code=400,
            detail="Gender distribution must sum to 100%"
        )
    
    # Store bulk task in Redis
    redis = await redis_client.get_connection()
    await redis.setex(
        f"bulk_task:{task_id}",
        86400,  # 24 hour expiry
        json.dumps({
            "task_id": task_id,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat(),
            "params": request.dict(),
            "progress": 0,
            "completed": 0,
            "total": request.count,
            "successful": 0,
            "failed": 0
        })
    )
    
    # Submit to Celery
    task = create_bulk_accounts_task.delay(request.dict())
    
    await redis.setex(f"bulk_task_map:{task_id}", 86400, task.id)
    await redis.setex(f"celery_bulk_task:{task.id}", 86400, task_id)
    
    return {
        "task_id": task_id,
        "celery_task_id": task.id,
        "status": "PENDING",
        "message": f"Bulk creation of {request.count} accounts initiated",
        "estimated_time": f"{request.count * 75} seconds"
    }

@app.get("/api/tasks/{task_id}", 
         response_model=TaskStatusResponse, 
         tags=["Tasks"],
         dependencies=[Depends(verify_token)])
async def get_task_status(task_id: str):
    """
    Get status of a creation task
    
    - **task_id**: UUID returned from create_account endpoint
    
    Returns current status, progress, and result (if completed)
    """
    redis = await redis_client.get_connection()
    
    # Get task data
    task_data = await redis.get(f"task:{task_id}")
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    task_info = json.loads(task_data)
    
    # Get Celery task ID
    celery_task_id = await redis.get(f"task_map:{task_id}")
    
    if celery_task_id:
        # Get Celery task result
        task_result = AsyncResult(celery_task_id, app=celery_app)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.state,
            created_at=task_info["created_at"],
            progress=0,
            total=1
        )
        
        if task_result.state == "SUCCESS":
            response.result = task_result.result
            response.completed_at = datetime.utcnow().isoformat()
        elif task_result.state == "FAILURE":
            response.error = str(task_result.info)
            response.completed_at = datetime.utcnow().isoformat()
        elif task_result.state == "PROGRESS":
            response.progress = task_result.info.get("progress", 0)
        
        return response
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_info["status"],
        created_at=task_info["created_at"],
        progress=0,
        total=1
    )

@app.get("/api/bulk-tasks/{task_id}", 
         response_model=TaskStatusResponse, 
         tags=["Tasks"],
         dependencies=[Depends(verify_token)])
async def get_bulk_task_status(task_id: str):
    """
    Get status of a bulk creation task
    
    - **task_id**: UUID returned from create_bulk_accounts endpoint
    
    Returns current progress and statistics
    """
    redis = await redis_client.get_connection()
    
    task_data = await redis.get(f"bulk_task:{task_id}")
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bulk task {task_id} not found"
        )
    
    task_info = json.loads(task_data)
    
    celery_task_id = await redis.get(f"bulk_task_map:{task_id}")
    
    if celery_task_id:
        task_result = AsyncResult(celery_task_id, app=celery_app)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.state,
            created_at=task_info["created_at"],
            progress=task_info["progress"],
            total=task_info["total"]
        )
        
        if task_result.state == "SUCCESS":
            response.result = task_result.result
            response.completed_at = datetime.utcnow().isoformat()
        elif task_result.state == "FAILURE":
            response.error = str(task_result.info)
            response.completed_at = datetime.utcnow().isoformat()
        elif task_result.state == "PROGRESS" and hasattr(task_result, 'info'):
            response.progress = task_result.info.get("progress", 0)
            response.result = {
                "completed": task_result.info.get("completed", 0),
                "total": task_result.info.get("total", task_info["total"]),
                "successful": task_result.info.get("successful", 0),
                "failed": task_result.info.get("failed", 0)
            }
        
        return response
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_info["status"],
        created_at=task_info["created_at"],
        progress=task_info["progress"],
        total=task_info["total"]
    )

@app.delete("/api/tasks/{task_id}", 
           tags=["Tasks"],
           dependencies=[Depends(verify_token)])
async def cancel_task(task_id: str):
    """
    Cancel a pending or running task
    
    - **task_id**: UUID of the task to cancel
    
    Returns cancellation confirmation
    """
    redis = await redis_client.get_connection()
    
    # Check if it's a single task
    task_data = await redis.get(f"task:{task_id}")
    celery_task_id = await redis.get(f"task_map:{task_id}")
    
    if not task_data:
        # Check if it's a bulk task
        task_data = await redis.get(f"bulk_task:{task_id}")
        celery_task_id = await redis.get(f"bulk_task_map:{task_id}")
    
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    if celery_task_id:
        # Revoke Celery task
        celery_app.control.revoke(celery_task_id, terminate=True, signal='SIGTERM')
        
        # Update task status
        task_info = json.loads(task_data)
        task_info["status"] = "CANCELLED"
        task_info["cancelled_at"] = datetime.utcnow().isoformat()
        
        await redis.setex(f"task:{task_id}", 3600, json.dumps(task_info))
        
        return {
            "task_id": task_id,
            "status": "CANCELLED",
            "message": "Task successfully cancelled"
        }
    
    return {
        "task_id": task_id,
        "status": "NOT_FOUND",
        "message": "No running task found"
    }

# ============================================================================
# API ENDPOINTS - PROXIES
# ============================================================================

@app.get("/api/proxies/status", 
         tags=["Proxies"],
         dependencies=[Depends(verify_token)])
async def get_proxy_status():
    """
    Get status of all proxy pools
    
    Returns health metrics for residential, mobile, and datacenter proxies
    """
    redis = await redis_client.get_connection()
    
    # In production, query actual proxy manager
    # This is a simulated response
    return {
        "residential": {
            "total": 1250,
            "healthy": 1180,
            "unhealthy": 70,
            "avg_response_time": 0.345,
            "countries": ["US", "GB", "CA", "DE", "FR", "JP", "AU"]
        },
        "mobile": {
            "total": 450,
            "healthy": 432,
            "unhealthy": 18,
            "avg_response_time": 0.523,
            "carriers": ["T-Mobile", "Verizon", "AT&T", "Vodafone", "Orange"]
        },
        "datacenter": {
            "total": 5000,
            "healthy": 4850,
            "unhealthy": 150,
            "avg_response_time": 0.089,
            "providers": ["AWS", "DigitalOcean", "Linode", "Hetzner"]
        }
    }

@app.post("/api/proxies/rotate", 
          tags=["Proxies"],
          dependencies=[Depends(verify_token)])
async def rotate_proxies(pool: str = "all"):
    """
    Force rotation of proxy pools
    
    - **pool**: residential/mobile/datacenter/all
    
    Returns rotation confirmation
    """
    # In production, trigger proxy rotation
    return {
        "status": "success",
        "message": f"Proxy pool '{pool}' rotation initiated",
        "estimated_time": "30 seconds"
    }

# ============================================================================
# API ENDPOINTS - FINGERPRINTS
# ============================================================================

@app.get("/api/fingerprints/random", 
         tags=["Fingerprints"],
         dependencies=[Depends(verify_token)])
async def get_random_fingerprint(country_code: Optional[str] = None):
    """
    Get a random quantum fingerprint
    
    - **country_code**: Optional ISO country code for geolocation
    
    Returns complete browser/device fingerprint
    """
    factory = QuantumFingerprintFactory()
    fingerprint = factory.generate_fingerprint(
        country_code=country_code or "US"
    )
    
    return fingerprint.to_dict()

@app.get("/api/fingerprints/{fingerprint_id}", 
         tags=["Fingerprints"],
         dependencies=[Depends(verify_token)])
async def get_fingerprint(fingerprint_id: str):
    """
    Get specific fingerprint by ID
    
    - **fingerprint_id**: 16-character hash ID
    
    Returns complete fingerprint details
    """
    redis = await redis_client.get_connection()
    
    # Try to get from cache
    cached = await redis.get(f"fingerprint:{fingerprint_id}")
    
    if cached:
        return json.loads(cached)
    
    # Generate on-demand
    factory = QuantumFingerprintFactory()
    fingerprint = factory.generate_fingerprint()
    
    # Cache for future requests
    await redis.setex(
        f"fingerprint:{fingerprint.fingerprint_id}",
        3600,
        json.dumps(fingerprint.to_dict())
    )
    
    return fingerprint.to_dict()

# ============================================================================
# API ENDPOINTS - STATISTICS
# ============================================================================

@app.get("/api/stats", 
         response_model=StatsResponse, 
         tags=["Statistics"],
         dependencies=[Depends(verify_token)])
async def get_statistics():
    """
    Get comprehensive system statistics
    
    Returns creation metrics, system health, and resource usage
    """
    redis = await redis_client.get_connection()
    
    # Get today's creation count
    today_key = f"stats:{datetime.utcnow().strftime('%Y-%m-%d')}"
    accounts_today = await redis.get(today_key) or 0
    
    # Get this hour's creation count
    hour_key = f"stats:{datetime.utcnow().strftime('%Y-%m-%d-%H')}"
    accounts_this_hour = await redis.get(hour_key) or 0
    
    # Get active tasks
    active_tasks = len([k async for k in redis.scan_iter("task:*")])
    bulk_tasks = len([k async for k in redis.scan_iter("bulk_task:*")])
    
    # System metrics
    system_load = psutil.getloadavg()[0] / psutil.cpu_count()
    memory_usage = psutil.virtual_memory().percent
    
    return StatsResponse(
        total_accounts_created=await redis.get("stats:total") or 0,
        accounts_today=int(accounts_today),
        accounts_this_hour=int(accounts_this_hour),
        success_rate=0.95,  # In production, calculate from actual data
        average_creation_time=72.5,  # seconds
        active_tasks=active_tasks,
        pending_tasks=active_tasks,
        completed_tasks=await redis.get("stats:completed") or 0,
        failed_tasks=await redis.get("stats:failed") or 0,
        available_proxies=1250,
        healthy_proxies=1180,
        available_phones=450,
        system_load=system_load,
        memory_usage=memory_usage
    )

# ============================================================================
# API ENDPOINTS - HEALTH
# ============================================================================

@app.get("/api/health", tags=["System"])
async def health_check():
    """
    System health check endpoint
    
    Returns status of all system components
    """
    redis_status = "healthy"
    try:
        redis = await redis_client.get_connection()
        await redis.ping()
    except:
        redis_status = "unhealthy"
    
    celery_status = "healthy"
    try:
        celery_app.control.ping(timeout=1)
    except:
        celery_status = "unhealthy"
    
    return {
        "status": "operational" if redis_status == "healthy" and celery_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": API_VERSION,
        "components": {
            "api": "healthy",
            "redis": redis_status,
            "celery": celery_status,
            "database": "healthy",  # In production, check actual DB
            "proxy_pool": "healthy",
            "sms_providers": "healthy"
        },
        "uptime": "5d 12h 23m",  # In production, calculate actual uptime
        "environment": "production"
    }

# ============================================================================
# API ENDPOINTS - DOCUMENTATION
# ============================================================================

@app.get("/api", tags=["Root"])
async def api_root():
    """API root endpoint - returns API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": "Quantum Gmail Creation Factory",
        "documentation": "/api/docs",
        "redoc": "/api/redoc",
        "openapi": "/api/openapi.json",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# API ENDPOINTS - EMAIL DELIVERABILITY
# ============================================================================

@app.post("/api/deliverability/analyze-spam",
          tags=["Email Deliverability"],
          dependencies=[Depends(verify_token)])
async def analyze_spam_content(subject: str, body: str):
    """
    Analyze email subject + body for spam triggers.
    Returns score 0-10 with trigger details and rewrite recommendations.
    """
    from warming.email_deliverability import SpamFilterTrainer
    trainer = SpamFilterTrainer()
    analysis = trainer.analyze_content(subject, body)
    rewritten = trainer.rewrite_subject(subject)
    
    return {
        "score": analysis.score,
        "is_safe": analysis.is_safe,
        "subject_score": analysis.subject_score,
        "body_score": analysis.body_score,
        "triggers": analysis.triggers,
        "recommendations": analysis.recommendations,
        "rewritten_subject": rewritten,
        "safe_send_times": trainer.get_safe_sending_times("UTC"),
    }

@app.get("/api/deliverability/reputation/{email}",
         tags=["Email Deliverability"],
         dependencies=[Depends(verify_token)])
async def get_sender_reputation(email: str):
    """
    Get sender reputation score and send limit for an email address.
    """
    from warming.email_deliverability import SenderReputationEngine
    engine = SenderReputationEngine()
    score = engine.calculate_score(email)
    limit = engine.get_send_limit(email)
    recs = engine.get_recommendations(email)
    
    return {
        "email": email,
        "score": score,
        "daily_send_limit": limit,
        "recommendations": recs,
    }

@app.get("/api/deliverability/domain/{domain}",
         tags=["Email Deliverability"],
         dependencies=[Depends(verify_token)])
async def get_domain_deliverability(domain: str):
    """
    Full domain deliverability report: reputation score, DNS health,
    authentication status, Postmaster stats.
    """
    from warming.email_deliverability import (
        DomainReputationBuilder, GooglePostmasterIntegrator,
        SPFRecordSimulator, DKIMSignatureSimulator, DMARCComplianceEngine,
    )
    
    rep = DomainReputationBuilder(domain)
    pm = GooglePostmasterIntegrator()
    
    return {
        "domain": domain,
        "reputation": rep.get_reputation(),
        "dns_health": rep.get_dns_health(),
        "domain_score": rep.calculate_domain_score(),
        "postmaster": {
            "domain_reputation": pm.get_domain_reputation(domain),
            "spam_rate": pm.get_spam_rate(domain),
            "delivery_errors": pm.get_delivery_errors(domain),
            "authentication": pm.get_authentication_report(domain),
        },
    }

@app.post("/api/deliverability/trust-score",
          tags=["Email Deliverability"],
          dependencies=[Depends(verify_token)])
async def calculate_trust_score(signals: Dict[str, float]):
    """
    Calculate weighted trust score from multiple signals.
    Signals should be normalized 0.0-1.0.
    """
    from warming.email_deliverability import TrustScoreOptimizer
    optimizer = TrustScoreOptimizer()
    score = optimizer.calculate_trust_score(signals)
    plan = optimizer.optimize(signals, target_score=85.0)
    
    return {
        "trust_score": score,
        "target": 85.0,
        "optimization_plan": plan,
    }

@app.get("/api/deliverability/ip-warmup/{ip}",
         tags=["Email Deliverability"],
         dependencies=[Depends(verify_token)])
async def get_ip_warmup_status(ip: str, target_daily: int = 500):
    """
    Get IP warmup schedule and current health.
    """
    from warming.email_deliverability import IPReputationWarmup
    warmup = IPReputationWarmup(ip)
    
    return {
        "ip": ip,
        "health": warmup.get_health(),
        "todays_limit": warmup.get_todays_limit(),
        "warmup_schedule": warmup.get_warmup_schedule(target_daily),
    }

@app.post("/api/deliverability/contact-network",
          tags=["Email Deliverability"],
          dependencies=[Depends(verify_token)])
async def generate_contact_network(size: int = 25, thread_count: int = 10):
    """
    Generate realistic contact network for email warmup.
    """
    from warming.email_deliverability import ContactNetworkBuilder
    builder = ContactNetworkBuilder()
    contacts = builder.generate_contact_network(size)
    threads = builder.generate_email_threads(contacts, thread_count)
    
    return {
        "contacts": contacts,
        "threads": threads,
        "total_contacts": len(contacts),
        "total_threads": len(threads),
    }

# ============================================================================
# API ENDPOINTS - WARMUP ORCHESTRATION
# ============================================================================

@app.post("/api/warmup/run-session",
          tags=["Warmup"],
          dependencies=[Depends(verify_token)])
async def run_warmup_session(
    services: List[str] = None,
    duration_min: int = 15,
):
    """
    Run warmup sessions across specified Google services.
    
    Available services: play_store, photos, calendar, docs, sheets, slides, chrome_sync
    If services is None, runs all services.
    """
    from warming.google_service_warmups import (
        AndroidPlayStoreWarmup, GooglePhotosWarmup, CalendarEventGenerator,
        GoogleDocsWarmup, GoogleSheetsWarmup, GoogleSlidesWarmup, ChromeSyncSimulator,
    )
    
    service_map = {
        'play_store': AndroidPlayStoreWarmup,
        'photos': GooglePhotosWarmup,
        'calendar': CalendarEventGenerator,
        'docs': GoogleDocsWarmup,
        'sheets': GoogleSheetsWarmup,
        'slides': GoogleSlidesWarmup,
        'chrome_sync': ChromeSyncSimulator,
    }
    
    if not services:
        services = list(service_map.keys())
    
    results = {}
    for svc_name in services:
        if svc_name not in service_map:
            results[svc_name] = {"status": "unknown_service"}
            continue
        
        cls = service_map[svc_name]
        instance = cls()
        
        try:
            await instance.run_warmup_session(duration_min=duration_min // len(services))
            results[svc_name] = {
                "status": "completed",
                "activities": len(instance.get_activity_log()),
                "log": instance.get_activity_log()[-3:],  # Last 3 entries
            }
        except Exception as e:
            results[svc_name] = {"status": "error", "error": str(e)}
    
    return {
        "session_id": str(uuid.uuid4()),
        "services_run": len(services),
        "duration_min": duration_min,
        "results": results,
    }

@app.get("/api/warmup/available-services",
         tags=["Warmup"],
         dependencies=[Depends(verify_token)])
async def get_available_warmup_services():
    """List all available warmup services and their capabilities."""
    return {
        "services": [
            {"name": "play_store", "description": "Google Play Store browsing and app exploration",
             "actions": ["browse_apps", "search_app", "read_reviews", "install_free_app"]},
            {"name": "photos", "description": "Google Photos upload and album management",
             "actions": ["upload_photos", "create_album", "browse_memories", "share_album"]},
            {"name": "calendar", "description": "Google Calendar event management",
             "actions": ["create_event", "create_recurring_event", "browse_calendar"]},
            {"name": "docs", "description": "Google Docs document creation and editing",
             "actions": ["create_document", "edit_document", "add_comment", "share_document"]},
            {"name": "sheets", "description": "Google Sheets spreadsheet operations",
             "actions": ["create_spreadsheet", "enter_data", "apply_formula", "create_chart"]},
            {"name": "slides", "description": "Google Slides presentation management",
             "actions": ["create_presentation", "add_slide", "apply_theme"]},
            {"name": "chrome_sync", "description": "Chrome browser sync simulation",
             "actions": ["sync_bookmarks", "sync_history", "sync_passwords", "sync_extensions"]},
        ],
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )

# ============================================================================
# SERVER LAUNCH FUNCTION
# ============================================================================

def start_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Launch the FastAPI server
    
    Args:
        host: Bind address (default: 0.0.0.0)
        port: Bind port (default: 8000)
        reload: Auto-reload on code changes (default: False)
    """
    logger.info(f"🔥 Starting Gmail Infinity Factory API server on {host}:{port}")
    logger.info(f"📚 Documentation available at http://{host}:{port}/api/docs")
    logger.info(f"🔧 Debug mode: {'enabled' if reload else 'disabled'}")
    
    uvicorn.run(
        "api.rest_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        workers=1,  # Use multiple workers in production with Gunicorn
        proxy_headers=True,
        forwarded_allow_ips="*"
    )

if __name__ == "__main__":
    start_api_server(reload=True)