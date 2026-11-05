"""
RFC-7807 Problem Details & Request Correlation Middleware
Provides standardized, structured error responses and attaches correlation request IDs
across all incoming and outgoing API traffic.
Ported and adapted from Smart-Ingredient-Analyzer.
"""

import uuid
import time
from datetime import datetime, timezone
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.services.input_validator import RefusalError

class RequestIdAndErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract incoming correlation request ID
        req_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        request.state.request_id = req_id

        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response

        except RefusalError as re:
            # Ladder of Refusals structured error
            return JSONResponse(
                status_code=re.status_code,
                headers={"X-Request-ID": req_id},
                content={
                    "ok": False,
                    "type": "https://labelx.ai/errors/refusal",
                    "title": "Request Refused by Security Gate",
                    "status": re.status_code,
                    "code": re.code,
                    "detail": re.message,
                    "instance": str(request.url.path),
                    "requestId": req_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        except HTTPException as he:
            detail_val = he.detail
            code = "HTTP_ERROR"
            message = str(detail_val)
            if isinstance(detail_val, dict):
                code = detail_val.get("code", "HTTP_ERROR")
                message = detail_val.get("message", str(detail_val))

            return JSONResponse(
                status_code=he.status_code,
                headers={"X-Request-ID": req_id},
                content={
                    "ok": False,
                    "type": f"https://labelx.ai/errors/{code.lower()}",
                    "title": "HTTP Processing Error",
                    "status": he.status_code,
                    "code": code,
                    "detail": message,
                    "instance": str(request.url.path),
                    "requestId": req_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

        except Exception as exc:
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                headers={"X-Request-ID": req_id},
                content={
                    "ok": False,
                    "type": "https://labelx.ai/errors/internal-server-error",
                    "title": "Internal Server Error",
                    "status": 500,
                    "code": "INTERNAL_SERVER_ERROR",
                    "detail": "An unexpected error occurred during processing. Refer to requestId in support inquiries.",
                    "instance": str(request.url.path),
                    "requestId": req_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
