# filename: /code/quiz-app/backend/app/validate_openapi.py

from fastapi.openapi.utils import get_openapi

from backend.app.main import \
    app  # Adjust the import based on your actual app file and instance


def validate_openapi_schema():
    try:
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        print("OpenAPI schema generated successfully!")
        print(openapi_schema)
    except Exception as e:
        print("Error generating OpenAPI schema:")
        print(e)

if __name__ == "__main__":
    validate_openapi_schema()
