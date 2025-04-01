from src.config import settings
from src.globals import (
    create_service_container,
)
from src.providers import generate_components

pipe_components = generate_components(settings.components)
service_container = create_service_container(pipe_components, settings)
print(service_container)
