# Supply Chain Management (SCM) System

This repository contains a Supply Chain Management system with a Django backend and React frontend. The application follows a modular architecture with separate services for different aspects of supply chain management.

## Project Structure

### Backend (Django)

The backend is organized using a domain-driven design approach with the following core modules:

- **accounts**: User authentication and authorization
- **projects**: Project management functionality
- **materials**: Material definitions and specifications
- **request**: Material requests from users
- **procurement**: Supplier and purchase order management
- **inventory**: Inventory tracking and management
- **quality**: Quality control processes
- **accounting**: Financial tracking
- **notifications**: System notifications
- **attachments**: File attachments
- **dashboard**: Dashboard and reporting

Each module follows a consistent architecture pattern:
- **models.py**: Data models
- **repositories.py**: Data access layer
- **services.py**: Business logic
- **api/**: API endpoints and serializers

### Frontend (React)

The frontend is built with React, TypeScript, and Material-UI. It uses Redux for state management and React Router for navigation. The structure follows a feature-based organization:

- **features/**: Feature modules (auth, procurement, inventory, etc.)
- **components/**: Shared UI components
- **app/**: Application configuration
- **hooks/**: Custom React hooks

## Docker Deployment

The application can be deployed using Docker containers. The following files are provided for containerization:

- **Dockerfile**: For the Django backend
- **frontend/Dockerfile**: For the React frontend
- **docker-compose.yml**: Orchestrates all services

### Prerequisites

- Docker and Docker Compose installed on your system
- Git to clone the repository

### Deployment Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd scm
   ```

2. Create a `.env.docker` file in the `.envs` directory (you can copy from the provided `.env.docker` template)

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Initialize the database (first time only):
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

5. Access the applications:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:8080
   - API Documentation: http://localhost:8000/swagger/

## Development Notes

### Backend-Frontend Communication

The frontend communicates with the backend through RESTful APIs. Authentication is handled using JWT tokens. The main API endpoints are:

- `/api/accounts/login/`: User authentication
- `/api/accounts/profile/`: User profile information
- `/api/projects/`: Project management
- `/api/request/`: Material requests
- `/api/procurement/`: Procurement management

### Modular Functionality

The system is designed to be modular, allowing individual components to function independently. For example:

- User authentication and profile management work as a standalone module
- Material request functionality can operate independently of other modules
- Project management has its own complete workflow

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000 and 8080 are available on your system
2. **Database migrations**: If you encounter database errors, try running migrations again
3. **Frontend-backend connection**: Check CORS settings if the frontend cannot connect to the backend

### Logs

To view logs for troubleshooting:

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.