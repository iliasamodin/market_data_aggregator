from pathlib import Path

from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from src.core.application.utils.modul_loader import ModuleLoader
from src.infrastructure.database.models.base import Base

models_path = Path(__file__).resolve().parent
ModuleLoader.load_modules(models_path)

classes_of_models: dict[str, DeclarativeAttributeIntercept] = {
    cls.class_.__tablename__: cls.class_ for cls in Base.registry.mappers if issubclass(cls.class_, Base)
}
