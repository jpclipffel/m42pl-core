import importlib
import importlib.util
import logging
import glob
import sys
import os

from typing import List, Dict, Any

import m42pl.commands
import m42pl.dispatchers
import m42pl.kvstores
from m42pl.errors import *


# Module-level logger
logger = logging.getLogger('m42pl')

# Mapping of imported modules.
modules = {} # type: Dict[str, Any]

# List of modules to import by their names.
BUILTINS_MODULES_NAMES = [
    "m42pl_commands",
    "m42pl_dispatchers",
    "m42pl_kvstores"
]

# List of modules imported by their names.
IMPORTED_MODULES_NAMES = [] # type: List[str]

# List of modules imported by their paths.
IMPORTED_MODULES_PATHS = [] # type: List[str]


def command(alias: str) -> Any:
    """Returns the requested :class:`Command` class.

    :param alias:   Command alias.
    """
    logger.info(f'requesting command: name="{alias}"')
    try:
        return m42pl.commands.ALIASES[alias]
    except KeyError:
        raise M42PLError(f'Command not found: name="{alias}"')


def dispatcher(alias: str = 'local') -> Any:
    """Returns the requested :class:`Dispatcher` class.

    :param alias:   Dispatcher alias.
    """
    logger.info(f'requesting dispatcher: name="{alias}"')
    try:
        return m42pl.dispatchers.ALIASES[alias]
    except KeyError:
        raise M42PLError(f'Dispatcher not found: name="{alias}"')


def kvstore(alias: str = 'local') -> Any:
    """Returns the requested :class:`KVStore` class.

    :param alias:   KVStore alias.
    """
    logger.info(f'requesting kvstore: name="{alias}"')
    try:
        return m42pl.kvstores.ALIASES[alias]
    except KeyError:
        raise M42PLError(f'KVStore not found: name="{alias}"')


def load_module_path(namespace: str, path: str) -> None:
    """Loads a module by path.
    
    :param namespace:   Module namespace (e.g. `m42pl.commands`)
    :param path:        Module path
    """
    logger.info(f'loading module by path: namespace="{namespace}", path="{path}"')
    # ---
    # Build module name for its basename
    module_name = f'''{namespace}.{os.path.basename(path).split('.')[0].replace(' ', '_').replace('-', '_')}'''
    logger.debug(f'module_name="{module_name}"')
    # ---
    # Get module entry point
    if os.path.isdir(path):
        module_entrypoint = os.path.join(path, '__init__.py')
    else:
        module_entrypoint = path
    logger.debug(f'module_entrypoint="{module_entrypoint}"')
    # ---
    # Load module
    logger.debug(f'spec_from_file_location: module_name="{module_name}"')
    module_spec = importlib.util.spec_from_file_location(module_name, module_entrypoint)
    logger.debug(f'module_from_spec: module_name="{module_name}"')
    module = importlib.util.module_from_spec(module_spec)
    logger.debug(f'exec_module: module_name="{module_name}"')
    module_spec.loader.exec_module(module) # type: ignore
    # ---
    # Register module
    logger.info(f'registering module: module_name="{module_name}"')
    sys.modules[module_spec.name] = module
    IMPORTED_MODULES_PATHS.append(path)
    modules[module_name] = module


def load_module_name(name: str) -> None:
    """Load a module by name.
    
    :param name:    Module name.
    """
    logger.info(f'loading module by name: name="{name}"')
    module = importlib.import_module(name)
    IMPORTED_MODULES_NAMES.append(name)
    modules[name] = module


def load_modules(search_paths: list = [], paths: list = [],
                 names: list = [], namespace: str = "m42pl") -> None:
    """Loads modules.
    
    :param search_paths:    Modules search paths
    :param paths:           Modules paths
    :param names:           Modules names
    :param namespace:       Modules namespace; Defaults to 'm42pl'
    """
    # ---
    # Load modules found in search paths.
    for path in search_paths:
        for item in glob.glob(os.path.join(path, '*')):
            if os.path.basename(item) not in [ "__pycache__", ]:
                load_module_path(namespace=namespace, path=item)
    # ---
    # Load module specified by path.
    for path in paths:
        load_module_path(namespace=namespace, path=path)
    # ---
    # Load modules specified by name.
    for name in set(BUILTINS_MODULES_NAMES + names):
        load_module_name(name=name)


def reload_modules():
    """Reloads previously imported modules.

    Returns the name of reloaded modules.
    """
    reloaded = []
    for name, module in modules.items():
        importlib.reload(module)
        reloaded.append(name)
    return reloaded
