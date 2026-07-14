# Project Atlas: Unified Multi-Service Platform

Project Atlas is a cloud-native GitOps deployment platform designed to host multiple independent backend services as a single Google Cloud Run service using a multi-container (sidecar) architecture.

## Architecture

The platform centralizes deployment management, reduces infrastructure costs, and eliminates cold starts for individual projects by grouping them under a single unified Cloud Run instance.

### Core Components
- **Atlas Gateway**: The main ingress container. It routes incoming requests (e.g., `/chess`, `/keysentry`) to the respective backend sidecars and enforces project-level access control via the `X-Atlas-Api-Key` header.
- **Data & Auth Agnostic**: The Gateway is fully decoupled from any specific authentication provider (like GoTrue). It relies entirely on infrastructure-level API Keys. Client applications pass the `X-Atlas-Api-Key` to get through the gateway, and can pass a separate `Authorization` header directly to the underlying service.
- **Sidecars (Microservices)**: Independent repositories (like `keysentry-api` and `chess-api`) running as distinct containers alongside the gateway within the same Cloud Run instance.
- **Service Manifest (`service-manifest.yaml`)**: The GitOps source of truth. It dictates which GitHub repositories, branches, and exact versions to deploy as sidecars.
- **GitHub Actions (CI/CD)**: A dynamic pipeline that reads the manifest, pulls the external sub-service repositories, builds the Docker images, pushes them to Google Container Registry (GCR), and orchestrates the deployment.
- **Google Secret Manager (GSM)**: Securely stores and dynamically injects sensitive environment variables (like API Keys and database URLs) directly into the Cloud Run containers at runtime.

### Generating an Atlas API Key
To create a secure API key for a new service on the platform, you can run the following command in your terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# or using openssl:
# openssl rand -base64 32
```
Save this key in Google Secret Manager as `API_KEY_<SERVICE>` (e.g., `API_KEY_KEYSENTRY`) and pass it in the `X-Atlas-Api-Key` header when making requests to the Gateway.

## Directory Structure

```text
.
├── Dockerfile                  # Instructions to build the unified platform image
├── README.md                   # Project documentation
├── .env.example                # Template for local environment and GSM secrets
├── .github/
│   └── workflows/
│       └── sidecar-ci.yml      # The dynamic GitOps CI/CD pipeline
├── deployment/                 
│   └── cloudrun-service.yaml   # Cloud Run multi-container topology definition
├── gateway/                    # The Modular FastAPI application gateway
│   ├── main.py                 # Main application entry point
│   ├── core/                   # Configuration and security logic
│   └── api/                    # API router aggregator and route definitions
├── requirements.txt            # Base dependencies for the gateway platform
└── service-manifest.yaml       # Configuration detailing which sidecars to deploy
```

## Getting Started

### Local Development

1. **Environment Setup:**
   Copy `.env.example` to `.env` and fill in the required values for your local development.
   ```bash
   cp .env.example .env
   ```

2. **Run the gateway locally:**
   ```bash
   pip install -r requirements.txt
   uvicorn gateway.main:app --reload
   ```

### Managing & Deploying Services (GitOps)

To add or update a sidecar service:
1. Update the `version`, `repo`, and `branch` in `service-manifest.yaml`.
2. Commit and push to `main`.
3. The GitHub Actions pipeline will automatically:
   - Check if the image version exists in GCR.
   - If not, check out the specific sidecar repository and build the Docker image.
   - Inject the new image tags and `GCP_PROJECT_ID` into `deployment/cloudrun-service.yaml` using `envsubst`.
   - Deploy the updated multi-container topology to Google Cloud Run.

### Secrets Management

This project uses **Google Secret Manager (GSM)** for production secrets to ensure GitHub Actions never touches sensitive data. 

When adding a new secret:
1. Add it to your local `.env` file for local development.
2. Go to the **Google Cloud Console > Secret Manager**.
3. Create a new secret (e.g., `keysentry-db-url`).
4. Reference it in `deployment/cloudrun-service.yaml` using `valueFrom.secretKeyRef`.

*Ensure your Cloud Run service account has the **Secret Manager Secret Accessor** IAM role.*
