"""
HRMS Lite - Custom Middleware
Additional middleware for enhanced functionality
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request processing time"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request details
        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Log request headers (excluding sensitive ones)
        safe_headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ['authorization', 'cookie', 'api-key']:
                safe_headers[key] = value
        
        if safe_headers:
            logger.info(f"Request headers: {safe_headers}")
        
        # Process request
        response = await call_next(request)
        
        # Log response details
        logger.info(
            f"Response: {response.status_code} "
            f"Size: {len(response.body) if hasattr(response, 'body') else 'unknown'} bytes"
        )
        
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server information
        response.headers["Server"] = "HRMS-Lite"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests
        self.requests = {
            ip: req_time for ip, req_time in self.requests.items()
            if current_time - req_time < self.period
        }
        
        # Check rate limit
        if client_ip in self.requests:
            request_count = len(self.requests[client_ip])
            if request_count >= self.calls:
                logger.warning(f"Rate limit exceeded for {client_ip}: {request_count} requests")
                return Response(
                    content={"error": "Rate limit exceeded"},
                    status_code=429,
                    headers={"Retry-After": str(self.period)}
                )
        
        # Add current request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)

class CacheMiddleware(BaseHTTPMiddleware):
    """Simple caching middleware for GET requests"""
    
    def __init__(self, app, ttl: int = 300):
        super().__init__(app)
        self.ttl = ttl
        self.cache = {}
    
    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        cache_key = f"{request.method}:{request.url}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.ttl:
                logger.info(f"Cache hit for {cache_key}")
                cached_response = Response(
                    content=cached_data["content"],
                    status_code=cached_data["status_code"],
                    headers={"X-Cache": "HIT"}
                )
                return cached_response
            else:
                # Remove expired cache
                del self.cache[cache_key]
        
        # Process request
        response = await call_next(request)
        
        # Cache response for successful GET requests
        if response.status_code == 200:
            self.cache[cache_key] = {
                "content": response.body,
                "status_code": response.status_code,
                "timestamp": current_time
            }
            response.headers["X-Cache"] = "MISS"
        
        return response

def setup_middleware(app):
    """Setup all middleware for the application"""
    
    # Add middleware in reverse order (last added runs first)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Uncomment to enable rate limiting
    # app.add_middleware(RateLimitMiddleware, calls=50, period=60)
    
    # Uncomment to enable caching (be careful with authentication)
    # app.add_middleware(CacheMiddleware, ttl=300)
    
    logger.info("Middleware setup complete")
