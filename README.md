# Product Price Comparison Application

A production-ready microservices-based system designed to aggregate and compare product pricing across multiple vendor networks. The architecture separates static product metadata from dynamic dealer pricing updates and uses a polyglot backend (Python + Node.js) with a lightweight asynchronous frontend.

## 🚀 Architecture Overview

The application follows a decentralized **Microservices Architecture**, enabling independent scaling, fault isolation, and flexible deployment models.

* **Frontend Microservice (Python / Flask)**: Serves the Single Page Application (SPA) interface and performs asynchronous Axios calls to backend services.
* **Product Details Service (Python / Flask)**: Provides product listings and metadata via dedicated REST endpoints.
* **Dealer Pricing Service (Node.js / Express)**: Supplies real-time pricing matrices sourced dynamically from an internal datastore.

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
Создай файл docker-compose.yml в корневой директории со следующей конфигурацией:

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

### 2. Execution
Запусти команду сборки в корневой папке для развертывания инфраструктуры:
**docker-compose up --build**

### 3. Access the Application
После успешной инициализации контейнеров перейди по адресу:
**http://localhost:5001**

---

## ☁️ Cloud Deployment (IBM Cloud Code Engine)

This project is fully optimised for serverless container runtimes such as IBM Cloud Code Engine.

### 1. Authenticate and Target Project
**ibmcloud login**
**ibmcloud ce project select --name your-project-name**

### 2. Deploy Product Metadata Service (Python Backend)
**ibmcloud ce application create --name prodlist --image us.icr.io/$(SN_ICR_NAMESPACE)/prodlist --registry-secret icr-secret --port 5000 --build-context-dir products_list --build-source https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git**

*Обязательно скопируй и сохрани сгенерированный URL-адрес приложения.*

### 3. Deploy Dealer Pricing Service (Node.js Backend)
**ibmcloud ce application create --name dealerdetails --image us.icr.io/$(SN_ICR_NAMESPACE)/dealerdetails --registry-secret icr-secret --port 8080 --build-context-dir dealer_details --build-source https://github.com/ibm-developer-skills-network/dealer_evaluation_backend.git**

*Обязательно скопируй и сохрани сгенерированный URL-адрес приложения.*

### 4. Configure Frontend Environment & Deploy
Перед сборкой фронтенда обнови эндпоинты внутри dealer_evaluation_frontend/html/index.html на полученные адреса облачных сервисов:

**let produrl = "https://prodlist.[your-subdomain].codeengine.appdomain.cloud/";**
**let dealerurl = "https://dealerdetails.[your-subdomain].codeengine.appdomain.cloud/";**

Запусти деплой фронтенд-сервера из корневой папки:
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
