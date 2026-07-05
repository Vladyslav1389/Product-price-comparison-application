# Product Price Comparison Application

A production-ready microservices-based application designed to aggregate and compare product pricing across multiple vendor networks. The system decouples product information from dynamic dealer pricing updates, utilizing a polyglot backend design (Python + Node.js) paired with a lightweight, high-performance asynchronous frontend.

## 🚀 Architecture Overview

This application is built on a decentralized **Microservices Architecture** to ensure independent scalability, fault isolation, and flexible deployment models.

* **Frontend Microservice (Python/Flask)**: Serves the web interface and handles clientside data aggregation via asynchronous Axios calls directly to the API gateways.
* **Product Details Microservice (Python/Flask)**: Handles product listings and descriptions, exposing dedicated REST endpoints.
* **Dealer Pricing Microservice (Node.js/Express)**: Manages real-time pricing matrix data, sourcing values dynamically from an internal data store.

---

## 📁 Repository Structure

product-price-comparison-app/
├── README.md # Main project documentation
├── docker-compose.yml # Local multi-container orchestration profile
├── dealer_evaluation_backend/ # Backend core services container
│ ├── dealer_details/ # Node.js Microservice (Dealer Pricing Matrix)
│ │ ├── utils/dealers.json # Mock datastore for pricing matrices
│ │ ├── Dockerfile # Optimized Node.js environment build definition
│ │ ├── package.json # Node.js dependencies & scripts
│ │ └── server.js # Express application entrypoint (Port: 8080)
│ └── products_list/ # Python Microservice (Product Metadata)
│ ├── products.json # Mock datastore for product listings
│ ├── Dockerfile # Minimal Python environment build definition
│ ├── app.py # Flask core API handler (Port: 5000)
│ └── requirements.txt # Python dependencies (Flask, Flask-CORS)
└── dealer_evaluation_frontend/ # Frontend Microservice
    ├── html/index.html # Single Page Application UI (Axios-integrated)
    ├── Dockerfile # Web server environment configuration
    ├── app.py # Static routing controller (Port: 5001)
    └── requirements.txt # Frontend app dependencies

---

## 🛠️ Deployment Strategies

### Option 1: Local Deployment via Docker Compose (Recommended)

To spin up the entire multi-container ecosystem locally with a single command, use the provided configuration so that all network configurations, port-forwarding, and service discovery dependencies are handled automatically.

#### 1. Create a docker-compose.yml file in the root directory:

version: '3.8'
services:
  products-backend:
    build:
      context: ./dealer_evaluation_backend
      dockerfile: products_list/Dockerfile
    ports:
      - "5000:5000"
    networks:
      - app-network
  dealers-backend:
    build:
      context: ./dealer_evaluation_backend
      dockerfile: dealer_details/Dockerfile
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

#### 2. Execution:
Run the following command in the root folder so that Docker builds your isolated images and mounts the containers:
**docker-compose up --build**

Access the application locally via: http://localhost:5001

---

### Option 2: Cloud Deployment via IBM Cloud Code Engine CLI

This system is fully optimized for cloud-native deployment using serverless container runtimes like IBM Cloud Code Engine. Follow these steps to build and deploy each microservice into live production from source:

#### 1. Authenticate and Initialize the Code Engine CLI Context:
**ibmcloud login**
**ibmcloud ce project select --name your-project-name**

#### 2. Deploy the Product Details Microservice (Python Backend):
**ibmcloud ce application create --name prodlist --image us.icr.io/$(SN_ICR_NAMESPACE)/prodlist --registry-secret icr-secret --port 5000 --build-context-dir products_list --build-source [https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git](https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git)**

*Save the generated deployment URL (e.g., [https://prodlist...codeengine.appdomain.cloud/](https://prodlist...codeengine.appdomain.cloud/)) for front-end integration.*

#### 3. Deploy the Dealer Pricing Microservice (Node.js Backend):
**ibmcloud ce application create --name dealerdetails --image us.icr.io/$(SN_ICR_NAMESPACE)/dealerdetails --registry-secret icr-secret --port 8080 --build-context-dir dealer_details --build-source [https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git](https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git)**

*Save the generated deployment URL (e.g., [https://dealerdetails...codeengine.appdomain.cloud/](https://dealerdetails...codeengine.appdomain.cloud/)).*

#### 4. Configure Frontend Environment & Deploy:
Before deploying the frontend container, update the endpoint pointers inside dealer_evaluation_frontend/html/index.html with your live production backend URLs discovered above:

**let produrl = "https://prodlist.[your-subdomain].codeengine.appdomain.cloud/";**
**let dealerurl = "https://dealerdetails.[your-subdomain].codeengine.appdomain.cloud/";**

Deploy the configured frontend application targeting the local root path:
**ibmcloud ce application create --name frontend --image us.icr.io/$(SN_ICR_NAMESPACE)/frontend --registry-secret icr-secret --port 5001 --build-source .**

---

## 📡 API Reference Specifications

### 📦 Product Metadata Service (Port 5000)
* **GET /products**: Returns an array of available product types and metadata descriptors.

### 💰 Dealer Pricing Service (Port 8080)
* **GET /dealers**: Retrieves the list of all certified suppliers.
* **GET /dealers/{id}**: Returns runtime mapping parameters and pricing matrix updates for a target supplier profile.