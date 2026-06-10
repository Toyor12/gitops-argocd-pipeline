# GitOps Product Review Pipeline — ArgoCD on Kubernetes

A production-style GitOps deployment demonstrating continuous delivery of a containerised FastAPI microservice using ArgoCD on Kubernetes.

## Architecture

GitHub (source of truth) -> ArgoCD (GitOps controller) -> Kubernetes (runtime) -> FastAPI app (Docker Hub)

## What This Project Demonstrates

- GitOps workflow: Git repository as the single source of truth for cluster state
- ArgoCD automated sync: any push to main triggers automatic reconciliation
- Kubernetes deployment with 2 replicas, readiness/liveness probes, and resource limits
- Containerised FastAPI microservice with sentiment analysis and keyword extraction
- Self-healing: ArgoCD detects and corrects any drift from the desired state
- CI/CD integration: image built and pushed to Docker Hub, manifest updated in Git

## Project Structure

    gitops-argocd-pipeline/
    ├── app/
    │   ├── main.py              # FastAPI review processor with sentiment analysis
    │   ├── requirements.txt     # Python dependencies
    │   └── Dockerfile           # Container image definition
    ├── k8s/
    │   ├── deployment.yaml      # Kubernetes Deployment (2 replicas, health probes)
    │   └── service.yaml         # Kubernetes Service (NodePort)
    ├── argocd/
    │   └── application.yaml     # ArgoCD Application manifest
    └── README.md

## GitOps Workflow

1. Developer pushes code or manifest change to GitHub
2. ArgoCD detects the change automatically
3. ArgoCD compares desired state (Git) with live state (cluster)
4. ArgoCD applies the diff automatically
5. Kubernetes pulls updated image from Docker Hub and rolls out

## Setup

### 1. Install ArgoCD
    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

### 2. Deploy the application
    kubectl apply -f argocd/application.yaml

### 3. Verify deployment
    kubectl get application -n argocd
    kubectl get pods -n default

## API Endpoints

### Health check
    curl http://localhost:8080/health

Response:
    {"status": "healthy", "service": "product-review-processor"}

### Analyse a review
    curl -X POST http://localhost:8080/analyse \
      -H "Content-Type: application/json" \
      -d '{"review_id": 1, "product_name": "Drill", "review_text": "Brilliant and excellent product", "rating": 5}'

Response:
    {"review_id": 1, "product_name": "Drill", "sentiment": "positive", "sentiment_score": 1.0, "keywords": ["brilliant", "excellent"]}

### Port forward to access locally
    kubectl port-forward service/review-processor-service 8080:80

## Key Kubernetes Concepts Demonstrated

- Deployment with replica management and rolling updates
- Readiness and liveness probes for health monitoring
- Resource requests and limits for container scheduling
- NodePort service for external access
- Namespace isolation

## ArgoCD Self-Healing

ArgoCD is configured with automated sync and self-healing. If someone manually changes the cluster state, ArgoCD will automatically revert it to match the Git repository.

## Author

Oyewole Oluwatoyosi — https://github.com/Toyor12
