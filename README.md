# 📚 Online Book Store

A Flask + MySQL web app for managing a book catalog (add, edit, delete, search), containerized with Docker, deployed on Kubernetes, and shipped through a GitHub Actions CI/CD pipeline. Cluster health is tracked with **Prometheus** and **Grafana**.

Built as a hands-on DevOps project covering the full lifecycle: code → container → cluster → automated deployment → monitoring.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL 8.0 |
| Frontend | HTML, CSS (Jinja2) |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes |
| CI/CD | GitHub Actions, Docker Hub |
| Monitoring | Prometheus, Grafana |

---

## 🏗️ Architecture

```mermaid
flowchart TB
    User([User]):::user -->|HTTP, NodePort| Service[Service: bookstore-service<br/>port 80 to 5000]:::network
    Service --> Pod1[Pod: bookstore-deployment<br/>Flask app]:::app
    Service --> Pod2[Pod: bookstore-deployment<br/>Flask app]:::app

    Pod1 --> ConfigMap[(ConfigMap)]:::config
    Pod1 --> Secret[(Secret)]:::config
    Pod2 --> ConfigMap
    Pod2 --> Secret

    Pod1 -->|SQL| MySQLSvc[Service: mysql-service<br/>port 3306]:::network
    Pod2 -->|SQL| MySQLSvc
    MySQLSvc --> MySQLPod[Pod: mysql-deployment<br/>MySQL 8.0]:::db
    MySQLPod --> PVC[(PVC)]:::storage
    PVC --> PV[(PersistentVolume)]:::storage

    Prometheus[Prometheus<br/>scrapes pod metrics]:::monitor -->|metrics| Grafana[Grafana<br/>dashboards]:::monitor
    Prometheus -.->|scrape| Pod1
    Prometheus -.->|scrape| Pod2
    Prometheus -.->|scrape| MySQLPod

    classDef user fill:#FFD166,stroke:#333,stroke-width:1px,color:#000
    classDef network fill:#06D6A0,stroke:#333,stroke-width:1px,color:#000
    classDef app fill:#118AB2,stroke:#333,stroke-width:1px,color:#fff
    classDef db fill:#EF476F,stroke:#333,stroke-width:1px,color:#fff
    classDef config fill:#8338EC,stroke:#333,stroke-width:1px,color:#fff
    classDef storage fill:#FB5607,stroke:#333,stroke-width:1px,color:#fff
    classDef monitor fill:#3A86FF,stroke:#333,stroke-width:1px,color:#fff
```

The Flask app runs as 2 replicas behind a `bookstore-service` (`NodePort`), reachable directly on the node's IP and port — no Ingress is used in this setup. Config comes from a `ConfigMap` and `Secret`. MySQL runs as a single pod backed by a `PersistentVolume` so data survives restarts. Liveness/readiness probes hit `/health`. Prometheus scrapes metrics from the running pods, and Grafana visualizes them (pod count, CPU, memory).

---

## 🛠️ How This Project Was Built

```mermaid
flowchart LR
    A[1. Build the App]:::step --> B[2. Connect Database]:::step
    B --> C[3. Containerize]:::step
    C --> D[4. Kubernetes Manifests]:::step
    D --> E[5. Push & Deploy]:::step
    E --> F[6. Automate with CI/CD]:::step
    F --> G[7. Add Monitoring]:::step

    classDef step fill:#118AB2,stroke:#333,stroke-width:1px,color:#fff
```

### 1. Build the Flask app
Started with the core app — routes to list, search, add, edit, and delete books — plus a `/health` route that Kubernetes uses later to check if the app is alive.
```python
@app.route("/health")
def health():
    return {"status": "healthy"}, 200
```

### 2. Connect MySQL
Used `PyMySQL` to connect to the database. Since the app and MySQL can start at the same time, the app retries the connection instead of crashing:
```python
for _ in range(30):
    try:
        return pymysql.connect(host=host, user=user, password=password, database=database)
    except pymysql.MySQLError:
        time.sleep(2)
```

### 3. Containerize with Docker
```bash
docker build -t online-book-store .
docker compose up --build
```
`docker-compose.yml` runs the app and MySQL together locally with one command.

### 4. Write Kubernetes manifests
Split the setup into separate files instead of one big config:
- `Namespace` — groups all resources
- `Deployment` — runs 2 replicas with CPU/memory limits and `/health` probes
- `Service` (`NodePort`) — exposes the app
- `ConfigMap` / `Secret` — app config and DB password
- `PV` / `PVC` — persistent storage for MySQL

### 5. Push the image and deploy
```bash
docker tag online-book-store <dockerhub-user>/online-book-store:latest
docker push <dockerhub-user>/online-book-store:latest

kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/
```

### 6. Automate with CI/CD
A GitHub Actions workflow runs on every push to `main`:
```bash
docker build -t $DOCKER_USERNAME/online-book-store:$GITHUB_SHA .
docker push $DOCKER_USERNAME/online-book-store:$GITHUB_SHA
kubectl set image deployment/bookstore-deployment bookstore=$DOCKER_USERNAME/online-book-store:$GITHUB_SHA
kubectl rollout status deployment/bookstore-deployment -n bookstore
```

### 7. Add monitoring
Deployed Prometheus to scrape pod metrics, and Grafana on top to visualize pod count, CPU, and memory usage.

---

## 🚀 Running the Project

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/online-book-store.git
cd online-book-store
```

### 2️⃣ Run locally with Docker Compose
```bash
docker compose up --build
```
App runs at `http://localhost:5001`.

### 3️⃣ Deploy to Kubernetes
```bash
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/
```

### 4️⃣ Check pod and service status
```bash
kubectl get pods -n bookstore
kubectl get svc -n bookstore
```
Since the service is `NodePort`, access the app at `http://<node-ip>:<node-port>`.

If you're using **Minikube**, the easiest way is:
```bash
minikube service bookstore-service -n bookstore
```
This opens the app directly in your browser.

### 🔧 Environment Variables
| Variable | Default |
|---|---|
| `DB_HOST` | `localhost` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | `root` |
| `DB_NAME` | `bookstore` |
| `PORT` | `5000` |

---

## 🖼️ Screenshots

**Website**

<img width="955" height="503" alt="image" src="https://github.com/user-attachments/assets/dcd2f5c8-b5ba-4708-a963-65efc45c0609" />


**CI/CD Pipeline — Successful Run**

<img width="937" height="350" alt="image" src="https://github.com/user-attachments/assets/7bd0d9c1-b728-438d-9de9-066e1af5e982" />

## 📊 Monitoring (Prometheus + Grafana)

**Pod Count**

<!-- Paste your pod count / Grafana panel screenshot here -->
![Pod status and count](screenshots/pods-status.png)

**CPU Usage**

<!-- Paste your Grafana CPU usage graph here -->
![CPU usage](screenshots/cpu-usage.png)

**Memory Usage**

<!-- Paste your Grafana memory usage graph here -->
![Memory usage](screenshots/memory-usage.png)

Resource limits per pod (from `kubernetes/deployment.yml`):

| Resource | Request | Limit |
|---|---|---|
| CPU | 200m | 500m |
| Memory | 256Mi | 512Mi |

---

## 👤 Author

**Nisha Shakoor** — self-directed DevOps learning project
