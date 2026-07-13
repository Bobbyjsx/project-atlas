# Project Atlas: Unified Multi-Service Platform

Project Atlas is a cloud-native deployment platform designed to host multiple independent backend services on a single Google Cloud Run service.

## Architecture

The platform acts as a modular monolith. It centralizes deployment management, reduces infrastructure costs, and eliminates cold starts for individual hobby projects by grouping them under a single unified API Gateway.

### Core Components
- **Atlas Gateway**: Built with FastAPI, it routes incoming requests (e.g., `/chess`, `/keysentry`) to the respective backend services and provides centralized authentication.
- **Service Manifest**: The `service-manifest.yaml` acts as the source of truth for the platform's composition. It pins the exact version of each independent service to be deployed.
- **Deployment Pipeline**: CI/CD processes resolve the manifest and install the listed sub-services as internal Python packages during the Docker build.

## Directory Structure

```text
.
├── Dockerfile                  # Instructions to build the unified platform image
├── README.md                   # Project documentation
├── deployment/                 # Deployment scripts and utilities
│   └── parse_manifest.py       # Script to generate requirements from the manifest
├── gateway/                    # The FastAPI application gateway
│   ├── __init__.py
│   └── main.py                 # Main application and routing logic
├── requirements.txt            # Base dependencies for the gateway platform
└── service-manifest.yaml       # Configuration detailing which sub-services to deploy
```

## Getting Started

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the gateway:**
   ```bash
   uvicorn gateway.main:app --reload
   ```

3. **Check the health endpoint:**
   Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) in your browser.

### Managing Services

To add or update a sub-service:
1. Update the version in `service-manifest.yaml`.
2. The CI pipeline will automatically parse the manifest using `deployment/parse_manifest.py`, install the specified package version, and redeploy the platform.

*(Note: During initial local setup without a package registry configured, sub-service packages should be installed locally or mocked in the gateway.)*
