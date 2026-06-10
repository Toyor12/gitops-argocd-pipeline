# GitOps Product Review Pipeline — ArgoCD, Prometheus & Grafana on Kubernetes

A production-style GitOps deployment demonstrating continuous delivery, container orchestration and monitoring observability of a containerised FastAPI microservice using ArgoCD, Prometheus and Grafana on Kubernetes.

## Architecture

GitHub (source of truth) -> ArgoCD (GitOps controller) -> Kubernetes (runtime) -> FastAPI app (Docker Hub)
                                                                                -> Prometheus (metrics scraping)
                                                                                -> Grafana (monitoring dashboard)

## What This Project Demonstrates

- GitOps workflow: Git repository as the single source of truth for cluster state
- ArgoCD automated sync: any push to main triggers automatic reconciliation
- Self-healing: ArgoCD detects and corrects any drift from desired state
- Kubernetes Deployment with 2 replicas, readiness and liveness probes, resource limits
- Containerised FastAPI microservice with sentiment analysis and keyword extraction
- Prometheus metrics scraping from the FastAPI /metrics endpoint
- Grafana dashboard for visualising request counts and sentiment distribution
- CI/CD integration: image built and pushed to Docker Hub, manifest updated in Git

## Project Structure

    gitops-argocd-pipeline/
    ├── app/
    │   ├── main.py                        # FastAPI app with /metrics endpoint
    │   ├── requirements.txt               # Python dependencies
    │   └── Dockerfile                     # Container image definition
    ├── k8s/
    │   ├── deployment.yaml                # Kubernetes Deployment (2 replicas, health probes)
    │   └── service.yaml                   # Kubernetes Service (NodePort)
    ├── monitoring/
    │   ├── prometheus-config.yaml         # Prometheus ConfigMap with scrape config
    │   ├── prometheus-deployment.yaml     # Prometheus Deployment and Service
    │   └── grafana-deployment.yaml        # Grafana Deployment and Service
    ├── argocd/
    │   └── application.yaml              # ArgoCD Application manifest
    └── README.md

## GitOps Workflow

1. Developer pushes code or manifest change to GitHub
2. ArgoCD detects the change automatically
3. ArgoCD compares desired state (Git) with live state (cluster)
4. ArgoCD applies the diff automatically
5. Kubernetes pulls updated image from Docker Hub and rolls out
6. Prometheus scrapes updated metrics from the new pods
7. Grafana reflects the changes in the monitoring dashboard

## Setup

### 1. Install ArgoCD
    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

### 2. Deploy the application via ArgoCD
    kubectl apply -f argocd/application.yaml

### 3. Deploy monitoring stack
    kubectl apply -f monitoring/prometheus-config.yaml
    kubectl apply -f monitoring/prometheus-deployment.yaml
    kubectl apply -f monitoring/grafana-deployment.yaml

### 4. Verify all pods are running
    kubectl get pods -n default
    kubectl get application -n argocd

## Accessing the Services

### Port forward all services
    kubectl port-forward service/review-processor-service 8080:80
    kubectl port-forward service/prometheus-service 9090:9090
    kubectl port-forward service/grafana-service 3000:3000

### API endpoints
    curl http://localhost:8080/health
    curl http://localhost:8080/metrics
    curl -X POST http://localhost:8080/analyse \
      -H "Content-Type: application/json" \
      -d '{"review_id": 1, "product_name": "Drill", "review_text": "Brilliant and excellent product", "rating": 5}'

### Grafana
    URL: http://localhost:3000
    Username: admin
    Password: admin123
    Data source: Add Prometheus at http://prometheus-service:9090

## Metrics Exposed

The FastAPI app exposes the following Prometheus metrics at /metrics:

    requests_total                 - Total number of review analysis requests
    positive_reviews_total         - Total positive reviews processed
    negative_reviews_total         - Total negative reviews processed
    neutral_reviews_total          - Total neutral reviews processed
    processing_seconds_total       - Total seconds spent processing reviews

## Key Kubernetes Concepts Demonstrated

- Deployment with replica management and rolling updates
- Readiness and liveness probes for health monitoring
- Resource requests and limits for container scheduling
- ConfigMap for externalised Prometheus configuration
- NodePort services for external access
- Namespace isolation

## ArgoCD Self-Healing

ArgoCD is configured with automated sync and self-healing:

    syncPolicy:
      automated:
        prune: true
        selfHeal: true

If someone manually changes the cluster state, ArgoCD automatically reverts it to match the Git repository.

## Author

Oyewole Oluwatoyosi — https://github.com/Toyor12
