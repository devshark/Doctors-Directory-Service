# Doctor List API

A RESTful API server exposing a Doctor List API for front-end applications to present doctor information to customers.

## Features

- Doctor listings with detailed information
- Filtering by category, district, language and consultation fee range
- Bulk creation of doctor records
- Supports three languages: English, Traditional Chinese (zh-hant), and Simplified Chinese (zh-hans) via Accept-Language header
- Soft delete functionality (doctors are marked inactive rather than removed)

## Technology Stack

- **Language**: Python 3.8+
- **Framework**: Django & Django REST Framework
- **Database**: SQLite
- **Server**: Gunicorn (WSGI HTTP Server)
- **Containerization**: Docker & Compose

## API Endpoints

### Doctors

- `GET /doctor/` - List all active doctors

  - Query Parameters:
    - `search`: Search by category name, district name, or language
    - `category`: Filter by category ID
    - `district`: Filter by district ID
    - `language`: Filter by language (en, mandarin, cantonese)
    - `min_consultation_fee`: Minimum consultation fee
    - `max_consultation_fee`: Maximum consultation fee

- `GET /doctor/{id}/` - Get details for a specific doctor
- `POST /doctor/` - Create a new doctor
- `POST /doctor/bulk_create/` - Create multiple doctors in a single request

### Categories and Districts

- `GET /category/` - List all categories
- `GET /category/{id}/` - Get a specific category
- `GET /district/` - List all districts
- `GET /district/{id}/` - Get a specific district

## Setup

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

### Local Development

1. Clone the repository:

   ```sh
   git clone git@github.com:devshark/Anthony_Lim_Senior_Backend_Software_Engineer_Technical_Assessment.git
   cd Anthony_Lim_Senior_Backend_Software_Engineer_Technical_Assessment
   ```

2. Create your `.env` file. You can copy from [the sample env file](.env.example) and customize the values as needed.

3. Set up the environment using the Makefile:

   ```sh
   make init
   ```

   This will create a virtual environment and install dependencies.

4. Initialize the database:

   ```sh
   make migrate
   ```

5. Load initial data (optional):

   ```sh
   make loaddata
   ```

6. Start the development server:
   ```sh
   make run
   ```

### Running with Docker

1. Build and run using the Makefile:

   ```sh
   make run-docker
   ```

2. The API should be available at [http://localhost:8000](http://localhost:8000)

### Admin Interface

1. Create a superuser:

   ```sh
   python manage.py createsuperuser --username admin --email admin@example.com
   ```

2. Access the admin interface at [http://localhost:8000/admin](http://localhost:8000/admin)

## Internationalization

The API supports three languages:

- English (`en`)
- Traditional Chinese (`zh-hant`)
- Simplified Chinese (`zh-hans`)

Set the `Accept-Language` header in your API requests to use a specific language.

## Testing

Run the test suite with:

```sh
make test
```

## Deployment Considerations

- **Security**: Use Nginx as a reverse proxy in production
- **Scaling**: Consider using a load balancer like HAProxy for distributing traffic
- **Database**: For production, consider migrating to a more robust database like PostgreSQL
- **Environment**: Use environment variables for configuration in production
- **Monitoring**: Implement health checks and monitoring for the service

## Design Decisions

### Why SQLite?

- Lightweight and perfect for microservice running on a local server
- ACID compliant, preventing data corruption on application crashes
- No need for a separate database server

### Why Django & Django REST Framework?

- Comprehensive, "batteries included" framework with battle-tested ORM
- Built-in support for internationalization
- Robust authentication and permission system
- Excellent documentation and community support

### Potential Improvements

- Structured contact details for better data analysis
- Implement authentication and rate limiting
- Add Swagger/OpenAPI documentation
- Enhance search capabilities with full-text search
- Add pagination for large result sets
- Transform the models with truly localizable fields
- Implement a more robust logging system

## Troubleshooting

- **Docker Issues**: If Docker container fails to start, check logs:
  ```sh
  docker logs [container-name]
  ```

## License

[MIT License](LICENSE)

## Author

Anthony Lim - Senior Backend Software Engineer
