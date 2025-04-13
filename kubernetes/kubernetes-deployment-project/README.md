### Step 1: Directory Structure

Create a new directory for your Kubernetes manifests. You can structure it as follows:

```
projet_cloud/
├── k8s/
│   ├── db-deployment.yaml
│   ├── db-service.yaml
│   ├── ingestion-api-deployment.yaml
│   ├── ingestion-api-service.yaml
│   ├── sensor-deployment.yaml
│   ├── detection-deployment.yaml
│   ├── dashboard-deployment.yaml
│   ├── dashboard-service.yaml
│   ├── persistent-volume.yaml
│   └── persistent-volume-claim.yaml
```

### Step 2: Create Kubernetes Manifests

#### 1. Persistent Volume and Claim

Create a file named `persistent-volume.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pgdata
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/pgdata  # Change this to your desired path on the host
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pgdata-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

#### 2. Database Deployment and Service

Create a file named `db-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: db
        image: postgres:latest
        env:
          - name: POSTGRES_DB
            value: "plant_monitoring"
          - name: POSTGRES_USER
            value: "postgres"
          - name: POSTGRES_PASSWORD
            value: "postgres"
        ports:
          - containerPort: 5432
        volumeMounts:
          - mountPath: /var/lib/postgresql/data
            name: pgdata
      volumes:
        - name: pgdata
          persistentVolumeClaim:
            claimName: pgdata-claim
```

Create a file named `db-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  ports:
    - port: 5432
  selector:
    app: db
```

#### 3. Ingestion API Deployment and Service

Create a file named `ingestion-api-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingestion-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ingestion-api
  template:
    metadata:
      labels:
        app: ingestion-api
    spec:
      containers:
      - name: ingestion-api
        image: your-ingestion-api-image:latest  # Replace with your actual image
        env:
          - name: DATABASE_URL
            value: "postgresql://postgres:postgres@db:5432/plant_monitoring"
          - name: TZ
            value: "Europe/Paris"
        ports:
          - containerPort: 8000
```

Create a file named `ingestion-api-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ingestion-api
spec:
  ports:
    - port: 8000
  selector:
    app: ingestion-api
```

#### 4. Sensor Deployment

Create a file named `sensor-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sensor
spec:
  replicas: 2  # Adjust based on your needs
  selector:
    matchLabels:
      app: sensor
  template:
    metadata:
      labels:
        app: sensor
    spec:
      containers:
      - name: sensor
        image: your-sensor-image:latest  # Replace with your actual image
        env:
          - name: SERVER_URL
            value: "http://ingestion-api:8000/ingest"
          - name: SENSOR_ID
            value: "FR-001"  # Change as needed
          - name: SENSOR_VERSION
            value: "FR-v8"  # Change as needed
          - name: PLANT_ID
            value: "1"  # Change as needed
          - name: TZ
            value: "Europe/Paris"
          - name: INTERVAL
            value: "10"  # Change as needed
```

#### 5. Detection Deployment

Create a file named `detection-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: detection
spec:
  replicas: 1
  selector:
    matchLabels:
      app: detection
  template:
    metadata:
      labels:
        app: detection
    spec:
      containers:
      - name: detection
        image: your-detection-image:latest  # Replace with your actual image
        env:
          - name: DB_HOST
            value: "db"
          - name: DB_NAME
            value: "plant_monitoring"
          - name: DB_USER
            value: "postgres"
          - name: DB_PASSWORD
            value: "postgres"
          - name: TZ
            value: "Europe/Paris"
```

#### 6. Dashboard Deployment and Service

Create a file named `dashboard-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dashboard
  template:
    metadata:
      labels:
        app: dashboard
    spec:
      containers:
      - name: dashboard
        image: your-dashboard-image:latest  # Replace with your actual image
        ports:
          - containerPort: 8501
```

Create a file named `dashboard-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: dashboard
spec:
  ports:
    - port: 8502
      targetPort: 8501
  selector:
    app: dashboard
```

### Step 3: Deploy to Kubernetes

1. **Install Kubernetes**: Ensure you have a Kubernetes cluster running. You can use Minikube, Docker Desktop, or a cloud provider like GKE, EKS, or AKS.

2. **Apply the Manifests**: Navigate to the `k8s` directory and run the following command to deploy all resources:

   ```bash
   kubectl apply -f .
   ```

3. **Check the Status**: You can check the status of your deployments and services using:

   ```bash
   kubectl get deployments
   kubectl get services
   ```

### Step 4: Access the Application

- For services like the dashboard, you may need to set up port forwarding or use a LoadBalancer service type depending on your Kubernetes setup.

### Conclusion

This guide provides a basic setup for deploying your application using Kubernetes. You may need to adjust the configurations based on your specific requirements, such as scaling, resource limits, and environment variables.