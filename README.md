# Project Atlas: Unified Multi-Service Platform

Project Atlas is a cloud-native GitOps deployment platform designed to host multiple independent backend services as a single Google Cloud Run service using a multi-container (sidecar) architecture.

## Architecture

The platform centralizes deployment management, reduces infrastructure costs, and eliminates cold starts for individual projects by grouping them under a single unified Cloud Run instance.

### Core Components
- **Atlas Gateway**: The main ingress container. It routes incoming requests (e.g., `/chess`, `/keysentry`) to the respective backend sidecars via `localhost` network routing and provides centralized authentication.
- **Authentication**: We use a standalone self-hosted **GoTrue** instance for authentication, entirely decoupling from Supabase. The Gateway handles JWT validation using the `GOTRUE_JWT_SECRET`.
- **Database**: Backend services connect to a standalone PostgreSQL database running on a self-hosted server, bypassing Supabase data APIs.
- **Sidecars (Microservices)**: Independent repositories (like `keysentry-api` and `chess-api`) running as distinct containers alongside the gateway within the same Cloud Run instance.
- **Service Manifest (`service-manifest.yaml`)**: The GitOps source of truth. It dictates which GitHub repositories, branches, and exact versions to deploy as sidecars.
- **GitHub Actions (CI/CD)**: A dynamic pipeline that reads the manifest, pulls the external sub-service repositories, builds the Docker images, pushes them to Google Container Registry (GCR), and orchestrates the deployment.
- **Google Secret Manager (GSM)**: Securely stores and dynamically injects sensitive environment variables (like database credentials and GoTrue secrets) directly into the Cloud Run containers at runtime.

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
├── gateway/                    # The FastAPI application gateway
│   └── main.py                 # Main application and routing logic
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
