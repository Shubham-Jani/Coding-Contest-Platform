<p align="center">
  <a href="" rel="noopener">
 <img  src="https://github.com/Shubham-Jani/Coding-Contest-Platform/blob/main/codingContestPlatformLogo.png" alt="Project logo"></a>
</p>

<h3 align="center">Coding Contest Platform</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()

</div>

---
## 📝 Table of Contents

- [📝 Table of Contents](#-table-of-contents)
- [🧐 About ](#-about-)
  - [Prerequisites](#prerequisites)
- [🚀 Deployment ](#-deployment-)
- [⛏️ Built Using ](#️-built-using-)
- [✍️ Authors ](#️-authors-)
- [🎉 Acknowledgements ](#-acknowledgements-)

## 🧐 About <a name = "about"></a>

Coding-Competition-Platform" is an open-source Django project designed for hosting coding competitions and contests. It's easy to set up using Docker, making it suitable for educational institutions and coding clubs. The platform supports custom problem creation and competition rounds, and future plans include test case support.

### Prerequisites

Before you begin using "Coding-Competition-Platform," make sure you have the following prerequisites installed on your system:

1. **Linux Operating System:** This platform is designed to work best on Linux-based systems.

2. **Docker:** You'll need Docker installed on your system to efficiently manage containers. If you don't have Docker installed, you can find installation instructions for various Linux distributions [here](https://docs.docker.com/get-docker/).

3. **Docker Compose:** Docker Compose simplifies the process of managing multi-container Docker applications. Make sure you have Docker Compose installed; installation details can be found [here](https://docs.docker.com/compose/install/).

Once you have these prerequisites in place, you'll be ready to set up and run "Coding-Competition-Platform" with ease.



## 🚀 Deployment <a name = "deployment"></a>

1. Clone the Repository

```bash
git clone https://github.com/Shubham-Jani/Coding-Contest-Platform.git
cd Coding-Competition-Platform

```

2. Configure Environment Variables

In the project's root directory, create two `.env` files: `.env.prod` and `.env.prod.db`, and set the necessary environment variables in each.

.env.prod

```env
DEBUG=False
SECRET_KEY=your
DJANGO_ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=your
SQL_USER=your
SQL_PASSWORD=your
SQL_HOST=your
SQL_PORT=5432
DATABASE=postgres

```

.env.prod.db

```env
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password

```

3. Build and Run the Docker Containers

Use Docker Compose to build and run the containers defined in `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up --build -d

```
4. You need to Build and run the Judge0 docker Containers as well to run code from users:
   
```bash
docker-compose -f judge/judge0-v1.13.0/docker-compose.yml up --build -d

``` 

1. Initialize the Database

Run database migrations and create a superuser:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

```

5. Access the Application

Once the containers are up and running, you can access the Coding-Competition-Platform at `localhost:1337`.

## ⛏️ Built Using <a name = "built_using"></a>

- [Django](https://www.djangoproject.com/) - Web Framework
- [Tailwind-CSS](https://tailwindcss.com/) -FrontEnd
  

## ✍️ Authors <a name = "authors"></a>

- [@Shubham-Jani](https://github.com/Shubham-Jani)



## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Judge0
