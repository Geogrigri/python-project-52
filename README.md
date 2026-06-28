### Hexlet tests and linter status:
[![Actions Status](https://github.com/Geogrigri/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Geogrigri/python-project-52/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Geogrigri_python-project-52&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Geogrigri_python-project-52)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Geogrigri_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Geogrigri_python-project-52)

## Task Manager

Task Manager is a Django web application for managing tasks.

### Local development

```bash
make install
make migrate
make dev
```

### Production

Render build command:

```bash
make build
```

Render start command:

```bash
make render-start
```

Deployed application: https://python-project-52-obym.onrender.com

### Error tracking

Set these environment variables in production to send errors to Rollbar:

```bash
ROLLBAR_ACCESS_TOKEN=<server access token>
ROLLBAR_ENVIRONMENT=production
```
