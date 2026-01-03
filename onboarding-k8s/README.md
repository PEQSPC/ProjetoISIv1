## Local Development Onboarding Guide (WSL2)

This guide explains how to spin up the ** Simulation-as-a-Service** platform locally using the `setup-dev.sh` automation script.

### 1. Prerequisites (Windows + WSL2)

Ensure the following are installed and running before executing the script.

* **WSL2:** (Ubuntu 20.04 or 22.04 recommended).
* **Docker Desktop for Windows:**
* *Crucial Setting:* Go to Settings > Resources > WSL Integration > Enable integration for your specific distro (e.g., Ubuntu).


* **Kubectl:** The Kubernetes command-line tool.
* *Install in WSL:* `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl`


* **Kind:** Kubernetes in Docker.
* *Install in WSL:* `curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind`



---

### 2. Project Setup

Ensure your repository is cloned inside the **WSL filesystem** (e.g., `~/projects/ProjetoISIv1`), not the Windows mounted drive (`/mnt/c/...`), for significantly better Docker performance.

**Required Directory Structure:**

```text
/PEQSPC/ProjetoISIv1
├── setup-dev.sh         # The automation script
├── app/                 # Manager API code
├── simulator/           # Simulator code
└── k8s-static/          # Kubernetes YAMLs

```

---

### 3. Running the Environment

1. **Open Terminal:** Launch your WSL terminal (Ubuntu).
2. **Navigate to Repo:**
```bash
cd ~/path/to/PEQSPC/ProjetoISIv1

```


3. **Make Executable:**
```bash
chmod +x setup-dev.sh

```


4. **Run Script:**
```bash
./setup-dev.sh

```



**What the script does:**

1. Creates a Kind cluster named `isi-dev-cluster`.
2. Builds local Docker images for the API and Simulator.
3. Loads those images directly into the cluster nodes (bypassing Docker Hub).
4. Applies RBAC (permissions) and deploys the API.

---

### 4. Verification & Usage

Once the script finishes with `✅ Setup Complete!`:

**A. Check Status**

```bash
kubectl get pods -n iot-sims
# You should see 'manager-api-xxxxx' running.

```

**B. Access the API (Port Forward)**
Run this command in a **separate** WSL terminal window to open the tunnel:

```bash
kubectl port-forward svc/manager-api-service 5000:80 -n iot-sims

```

**C. Create a Simulation**
Open **PowerShell** (Windows) or stay in **WSL** and run:

```bash
curl -X POST http://localhost:5000/create-sim \
  -H "Content-Type: application/json" \
  -d '{"device_id": "test-unit-01", "duration": 60}'

```

**D. See the Result**
Back in WSL:

```bash
kubectl get pods -n iot-sims --watch

```

You will see a new pod `sim-test-unit-01-xxxx` spin up, run, and eventually terminate automatically.

---

### Common Troubleshooting

* **Error: "docker: command not found"**
* *Fix:* Docker Desktop is not running or WSL integration is disabled in Docker Settings.


* **Error: "ImagePullBackOff"**
* *Fix:* The script failed to load the image. Run `kind load docker-image peqspc/manager-api:dev --name isi-dev-cluster` manually.


* **Slow Network/IO**
* *Fix:* Ensure you are running strictly inside the Linux filesystem (`/home/user/...`), not `/mnt/c/Users/...`.



Would you like the `test-curl.sh` script to automate step 4C?