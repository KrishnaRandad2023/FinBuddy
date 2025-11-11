"""
API Gateway - Main entry point for all FinBuddy services
Routes requests to appropriate microservices
Port: 8000
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger('api_gateway')

# Service registry
SERVICES = {
    "user": settings.USER_SERVICE_URL,
    "portfolio": settings.PORTFOLIO_SERVICE_URL,
    "news": settings.NEWS_SERVICE_URL,
    "ai": settings.AI_SERVICE_URL,
    "risk": settings.RISK_SERVICE_URL,
    "learning": settings.LEARNING_SERVICE_URL
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("🚪 API Gateway starting on port 8000...")
    logger.info(f"📡 Registered services: {list(SERVICES.keys())}")
    yield
    # Shutdown
    logger.info("🛑 API Gateway shutting down...")

app = FastAPI(
    title="FinBuddy API Gateway",
    version="2.0.0",
    description="Main entry point for all FinBuddy microservices",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "FinBuddy API Gateway",
        "version": "2.0.0",
        "status": "operational",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health():
    """Check health of gateway and all services"""
    health_status = {"gateway": "healthy", "services": {}}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=3.0)
                health_status["services"][service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except httpx.TimeoutException:
                health_status["services"][service_name] = "timeout"
            except httpx.ConnectError:
                health_status["services"][service_name] = "unreachable"
            except Exception as e:
                logger.warning(f"Health check failed for {service_name}: {e}")
                health_status["services"][service_name] = "error"
    
    return health_status

@app.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(service_name: str, path: str, request: Request):
    """Route requests to appropriate microservice"""
    
    # Map service names
    service_mapping = {
        "users": "user",
        "auth": "user",
        "investments": "portfolio",
        "portfolio": "portfolio",
        "prices": "portfolio",
        "news": "news",
        "ai": "ai",
        "chat": "ai",
        "risk": "risk",
        "fraud": "risk",
        "learning": "learning",
        "modules": "learning"
    }
    
    mapped_service = service_mapping.get(service_name, service_name)
    
    if mapped_service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    service_url = SERVICES[mapped_service]
    target_url = f"{service_url}/{path}"
    
    # Forward the request
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Get request body if present
            body = await request.body()
            
            # Forward request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=body,
                params=dict(request.query_params)
            )
            
            return JSONResponse(
                content=response.json() if response.text else {},
                status_code=response.status_code
            )
        
        except httpx.RequestError as e:
            logger.error(f"Error forwarding request to {service_name}: {e}")
            raise HTTPException(status_code=503, detail=f"Service '{service_name}' unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
