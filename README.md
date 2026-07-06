# Cloud-Native Product Price Comparison Application

A multi-tier asynchronous microservices application engineered with the **utmost** focus on scalability to aggregate product data and evaluate live dealer pricing. The ecosystem is fully containerised and deployed using a serverless orchestration pattern on IBM Cloud Code Engine.  

Historically, tightly coupled architectures **fell short** when managing dynamic vendor updates. This project avoids those **mediocre** limitations by decoupling static catalog management from live pricing evaluation into separate runtimes.  

---

## 🏗️ System Architecture & Component Breakdown

The application consists of three autonomous microservices deployed independently **so that** any structural failure or upgrade in one layer does not disrupt the entire system. The asynchronous communication pattern ensures that data delivery takes **atmost** a few moments to sync across the non-blocking UI.

### 📦 Microservices Ecosystem

| Service Name | Runtime / Framework | Port | Functional Description |
| :--- | :--- | :--- | :--- |
| **Product Details Microservice** | Python / Flask | `5000` | Manages static inventory definitions and serves API endpoints to fetch metadata for products like Headphones, Laptops, and Printers. |
| **Dealer Pricing Microservice** | Node.js / Express | `8080` | Tracks distributed dealer structures (e.g., Binglee, DXC Electronics, Bobay) and calculates specific product offers. |
| **Frontend User Interface** | HTML5 / JavaScript / Axios | `5001` | Consumes public cloud endpoints asynchronously **so that** users can compare baseline prices or query individual dealer rates on a non-blocking UI. |

---

## 📁 Repository Structure

```text
product-price-comparison-app/
├── README.md
├── docker-compose.yml
├── dealer_evaluation_backend/
│   ├── dealer_details/                  # Node.js microservice (Dealer Pricing)
│   │   ├── utils/dealers.json          # Mock pricing datastore
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   └── server.js                   # Express app (Port 8080)
│   └── products_list/                  # Python microservice (Product Metadata)
│       ├── products.json               # Mock product datastore
│       ├── Dockerfile
│       ├── app.py                      # Flask API (Port 5000)
│       └── requirements.txt
└── dealer_evaluation_frontend/
    ├── html/index.html                 # SPA UI (Axios integrated)
    ├── Dockerfile
    ├── app.py                          # Static file server (Port 5001)
    └── requirements.txt
```
---

## 🛠️ Local Deployment (Docker Compose)

### System Requirements
* **Docker** ≥ 20.x
* **Docker Compose** ≥ v2.x

### 1. Environment Configuration (docker-compose.yml)
Create a docker-compose.yml file in the root directory with the following configuration:

```yaml
version: '3.8'

services:
  products-backend:
    build:
      context: ./dealer_evaluation_backend/products_list
    ports:
      - "5000:5000"
    networks:
      - app-network

  dealers-backend:
    build:
      context: ./dealer_evaluation_backend/dealer_details
    ports:
      - "8080:8080"
    networks:
      - app-network

  frontend:
    build:
      context: ./dealer_evaluation_frontend
    ports:
      - "5001:5001"
    environment:
      - PROD_LIST_URL=http://localhost:5000/
      - DEALER_DETAILS_URL=http://localhost:8080/
    networks:
      - app-network
    depends_on:
      - products-backend
      - dealers-backend

networks:
  app-network:
    driver: bridge
```

### 2. Execution
Run the build command in the root folder to deploy the infrastructure:
**docker-compose up --build**

### 3. Access the Application
After successful container initialisation, navigate to the following address in your browser:
**http://localhost:5001**

---

## ☁️ Cloud Deployment (IBM Cloud Code Engine)

This project is fully optimised for serverless container runtimes such as IBM Cloud Code Engine.

### 1. Authenticate and Target Project
**ibmcloud login**
**ibmcloud ce project select --name your-project-name**

### 2. Deploy Product Metadata Service (Python Backend)
**ibmcloud ce application create --name prodlist --image us.icr.io/$(SN_ICR_NAMESPACE)/prodlist --registry-secret icr-secret --port 5000 --build-context-dir products_list --build-source https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git**

*Make sure to copy and save the generated application URL.*

### 3. Deploy Dealer Pricing Service (Node.js Backend)
**ibmcloud ce application create --name dealerdetails --image us.icr.io/$(SN_ICR_NAMESPACE)/dealerdetails --registry-secret icr-secret --port 8080 --build-context-dir dealer_details --build-source https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git**

*Make sure to copy and save the generated application URL.*

### 4. Configure Frontend Environment & Deploy
Before building the frontend, update the endpoints inside dealer_evaluation_frontend/html/index.html to point to the newly generated cloud service URLs:

**let produrl = "https://prodlist.[your-subdomain].codeengine.appdomain.cloud/";**
**let dealerurl = "https://dealerdetails.[your-subdomain].codeengine.appdomain.cloud/";**

Launch the frontend server deployment from the root directory:
**ibmcloud ce application create --name frontend --image us.icr.io/$(SN_ICR_NAMESPACE)/frontend --registry-secret icr-secret --port 5001 --build-source .**

---

## 📡 API Reference

### 📦 Product Metadata Service (Port 5000)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/products` | Returns a complete list of products and metadata records. |

#### Response Schema Example:
[
  {
    "id": 1,
    "name": "Laptop",
    "category": "Electronics"
  }
]

### 💰 Dealer Pricing Service (Port 8080)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/dealers` | Retrieves a complete list of active suppliers. |
| **GET** | `/dealers/{id}` | Fetches the complete pricing matrix metrics mapped to a specific dealer. |

#### Response Schema Example:
{
  "dealer": "TechCorp",
  "pricing": {
    "Laptop": 899,
    "Monitor": 199
  }
}

---

## 📜 License

This project is licensed under the terms of the **MIT License**. Feel free to use, modify, and distribute it as needed.
