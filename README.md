# **🚗 Auto Shop Management API**

A robust, production-ready RESTful API serving as the backend foundation for a full-stack automotive repair management system. Built to handle complex relational data, this API manages customers, mechanics, inventory parts, and comprehensive service tickets.

This project demonstrates scalable backend architecture, secure authentication, automated testing, and continuous deployment, designed seamlessly for future integration with a modern frontend framework like React.

## **🔗 Live Demo & Documentation**

Interact with the live API via the interactive Swagger UI:

👉 [**Auto Shop API Live Documentation**](https://autoshop-api-render.onrender.com/docs)

*(Note: The database spins down after periods of inactivity on the free tier, so the first request may take \~30 seconds to wake the server.)*

## **✨ Core Features**

* **Secure Authentication:** JWT (JSON Web Token) implementation for protected routes, ensuring only authorized customers can view their service history.  
* **Complex Relational Mapping:** Advanced SQLAlchemy models managing One-to-Many and Many-to-Many relationships (e.g., Service Tickets linked to both multiple Mechanics and multiple Parts).  
* **Performance Optimization:** Redis/SimpleCache implementation for high-traffic routes (like mechanic directory) to reduce database load.  
* **API Security:** Route-specific rate limiting to prevent brute-force attacks and abuse.  
* **Data Validation:** Strict payload parsing and serialization using Marshmallow schemas.  
* **Interactive Documentation:** Fully integrated Swagger UI auto-generated from route docstrings.

## **🛠️ Tech Stack**

* **Language & Framework:** Python 3, Flask  
* **Database & ORM:** PostgreSQL (Production), SQLite (Testing), Flask-SQLAlchemy  
* **Serialization:** Marshmallow  
* **Authentication:** Flask-JWT-Extended  
* **Package Management:** uv by Astral (for ultra-fast dependency resolution)  
* **CI/CD:** GitHub Actions (Automated Unit Testing)  
* **Deployment:** Render (Gunicorn WSGI Server)

## **🏗️ Architecture & Design Patterns**

The application is structured using the **Flask Application Factory** pattern and **Blueprints**. This modular design ensures that the codebase remains highly maintainable and scalable as new features are added.

* app/customer/ \- Account creation, login, and user profile management.  
* app/mechanic/ \- Employee management and workload tracking.  
* app/inventory/ \- Parts catalog and pricing management.  
* app/service\_ticket/ \- The core domain tying customers, mechanics, and parts into a single transactional record.

## **🚀 CI/CD Pipeline**

This repository utilizes **GitHub Actions** for Continuous Integration and Continuous Deployment.

1. Pushing to the main or master branch triggers the automated workflow.  
2. A secure virtual environment is created using uv.  
3. The unittest suite validates core CRUD operations, authentication logic, and edge cases.  
4. Upon passing all tests, a deployment webhook is triggered, updating the live PostgreSQL-backed service on Render with zero downtime.

## **💻 Local Installation**

To run this project locally for development or testing:

1. **Clone the repository:**  
   git clone https://github.com/rkoss-dev/autoshop-api-Render.git  
   cd autoshop-api

2. **Create a virtual environment and install dependencies (using uv):**  
   uv venv  
   source .venv/bin/activate  \# On Windows use: .venv\\Scripts\\activate  
   uv pip install \-r requirements.txt

3. **Set up environment variables:**  
   Create a .env file in the root directory:  
   SECRET\_KEY=your\_super\_secret\_key  
   DATABASE\_URL=sqlite:///autoshop.db

4. **Run the application:**  
   python flask\_app.py

   Navigate to http://127.0.0.1:5000/docs to view the local Swagger UI.

## **🌐 Full-Stack Integration Readiness**

This API was purposefully designed with frontend consumption in mind. It provides clean, predictable JSON responses, standardized error handling (400, 401, 403, 404), and stateless JWT authentication, making it perfectly primed for a robust client-side architecture (such as a React/Redux SPA) to handle state management and user interface rendering.