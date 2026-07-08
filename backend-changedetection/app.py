"""
CAIsat Backend API

FastAPI service that serves satellite imagery metadata and images from S4 storage
to the frontend application.
"""

# Assisted by: cursor, claude

import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

# Configuration from environment variables
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:7480")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "caisat-access-key")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "caisat-secret-key-change-in-production")
S3_BUCKET = os.getenv("S3_BUCKET", "satellite-images")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]

# Initialize FastAPI app
app = FastAPI(
    title="CAIsat API",
    description="Backend API for CAIsat satellite imagery change detection platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

print("CAIsat Backend API starting...")
print(f"  S3 Endpoint: {S3_ENDPOINT}")
print(f"  S3 Bucket: {S3_BUCKET}")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "CAIsat Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "areas": "/api/areas",
            "stats": "/api/areas/{location}/stats",
            "images": "/api/areas/{location}/images/{date}",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        s3_client.list_buckets()
        return {
            "status": "healthy",
            "s3_connection": "ok",
            "bucket": S3_BUCKET,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "s3_connection": "failed",
            "error": str(exc),
        }


@app.get("/api/areas")
async def get_areas() -> dict[str, Any]:
    """Get list of all monitored areas with summary statistics."""
    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key="metadata/areas.json",
        )
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=404,
                detail="Areas metadata not found. Run analysis pipeline first.",
            ) from exc
        raise HTTPException(status_code=500, detail=f"S3 error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching areas: {exc}") from exc


@app.get("/api/areas/{location}/stats")
async def get_location_stats(location: str) -> dict[str, Any]:
    """Get detailed statistics for a specific location."""
    valid_locations = ["las_vegas", "dubai", "death_valley", "phoenix"]
    if location not in valid_locations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location. Must be one of: {', '.join(valid_locations)}",
        )

    try:
        response = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key=f"metadata/{location}-stats.json",
        )
        return json.loads(response["Body"].read().decode("utf-8"))
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=404,
                detail=f"Statistics not found for {location}. Run analysis pipeline first.",
            ) from exc
        raise HTTPException(status_code=500, detail=f"S3 error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {exc}") from exc


@app.get("/api/areas/{location}/images/{date}")
async def get_location_image(location: str, date: str):
    """Get satellite image for a specific location and date."""
    valid_locations = ["las_vegas", "dubai", "death_valley", "phoenix"]
    if location not in valid_locations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location. Must be one of: {', '.join(valid_locations)}",
        )

    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD (e.g., 2024-05-15)",
        )

    try:
        image_key = f"{location}-{date}.png"
        response = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key=image_key,
        )
        image_data = response["Body"].read()
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",
                "Content-Disposition": f'inline; filename="{location}-{date}.png"',
            },
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=404,
                detail=f"Image not found for {location} on {date}",
            ) from exc
        raise HTTPException(status_code=500, detail=f"S3 error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {exc}") from exc


@app.get("/api/areas/{location}/images")
async def list_location_images(location: str) -> list[str]:
    """List all available image dates for a location."""
    valid_locations = ["las_vegas", "dubai", "death_valley", "phoenix"]
    if location not in valid_locations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location. Must be one of: {', '.join(valid_locations)}",
        )

    try:
        prefix = f"{location}-"
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefix,
        )

        if "Contents" not in response:
            return []

        dates = []
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".png"):
                dates.append(key.replace(f"{location}-", "").replace(".png", ""))

        return sorted(dates)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error listing images: {exc}") from exc
