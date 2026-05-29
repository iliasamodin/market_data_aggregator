from importlib import import_module
from pathlib import Path
from types import ModuleType

import re

from src.core.application.exceptions.modul_loader import BaseDirectoryNotFoundException, FailedToLoadModuleException


class ModuleLoader:
    """
    Utility for dynamic discovery and import of Python modules.

    Recursively walks a given directory,
    converts each .py file to a dotted import path,
    and imports it via importlib.
    """

    _BASE_DIR = "src"

    @classmethod
    def load_modules(cls, path: Path) -> list[ModuleType]:
        """
        Discovers and imports all Python modules under path.

        Walks the directory tree rooted at path,
        converts each .py file to a dotted module path
        relative to the project root,
        and imports it via importlib.

        :param path: Root directory to search for modules.

        :return: List of imported module objects.
        """

        src_dir = cls.get_src_dir()
        project_dir = src_dir.parent

        modules: list[ModuleType] = []
        for module_directory, _, names_of_modules in path.walk():
            relative_module_directory = module_directory.relative_to(project_dir)
            relative_module_directory = str(relative_module_directory).strip("\\/")
            relative_module_directory = re.sub(r"[\\/]", ".", relative_module_directory)

            for module_name in names_of_modules:
                if module_name.endswith(".py"):
                    module_name = module_name.replace(".py", "")

                    module = cls.load_module(
                        directory=relative_module_directory,
                        module_name=module_name,
                    )

                    modules.append(module)

        return modules

    @classmethod
    def get_src_dir(cls) -> Path:
        """
        Resolves the src directory path relative to this file.

        Traverses the parents of this file's resolved path
        until a directory named _BASE_DIR is found.

        :return: Absolute Path to the src directory.
        """

        current_file = Path(__file__).resolve()

        for parent in current_file.parents:
            if parent.name == cls._BASE_DIR:
                return parent

        raise BaseDirectoryNotFoundException()

    @staticmethod
    def load_module(
        directory: str,
        module_name: str,
    ) -> ModuleType:
        """
        Imports a single module by dotted path.

        Combines directory and module_name into a dotted import
        string and delegates to importlib.import_module.

        :param directory: Dotted package path (e.g. "src.core.utils").
        :param module_name: Module filename without .py extension.

        :return: Imported module object.
        """

        try:
            module = import_module(f"{directory}.{module_name}")

        except Exception:
            raise FailedToLoadModuleException()

        return module
