from email import message
import importlib
import importlib.util
import logging
import regex
import copy
import glob
import sys
import os

from typing import List, Dict, Any

import m42pl.commands
import m42pl.dispatchers
import m42pl.kvstores
import m42pl.encoders

from m42pl.commands import script

from m42pl.errors import *


# Module-level logger
logger = logging.getLogger('m42pl')

# Mapping of imported modules.
modules = {} # type: Dict[str, Any]

# List of modules to import by their names.
BUILTINS_MODULES_NAMES = [
    'm42pl_commands',
    'm42pl_dispatchers',
    'm42pl_kvstores',
    'm42pl_encoders'
]

# List of modules imported by their names.
IMPORTED_MODULES_NAMES = [] # type: List[str]

# List of modules imported by their paths.
IMPORTED_MODULES_PATHS = [] # type: List[str]


def command(alias: str) -> Any:
    """Returns the requested command's class.

    :param alias: Command alias
    """
    logger.info(f'requesting command: name="{alias}"')
    try:
        return m42pl.commands.ALIASES[alias]
    except KeyError:
        # raise M42PLError(f'Command not found: name="{alias}"')
        raise ObjectNotFoundError(
            kind='command',
            name=alias,
            message=f'Command not found: name="{alias}"'
        )


def dispatcher(alias: str = 'local') -> Any:
    """Returns the requested :class:`Dispatcher` class.

    :param alias:   Dispatcher alias
    """
    logger.info(f'requesting dispatcher: name="{alias}"')
    try:
        return m42pl.dispatchers.ALIASES[alias]
    except KeyError:
        # raise M42PLError(f'Dispatcher not found: name="{alias}"')
        raise ObjectNotFoundError(
            kind='dispatcher',
            name=alias,
            message=f'Dispatcher not found: name="{alias}"'
        )


def kvstore(alias: str = 'local') -> Any:
    """Returns the requested :class:`KVStore` class.

    :param alias:   KVStore alias
    """
    logger.info(f'requesting kvstore: name="{alias}"')
    try:
        return m42pl.kvstores.ALIASES[alias]
    except KeyError:
        # raise M42PLError(f'KVStore not found: name="{alias}"')
        raise ObjectNotFoundError(
            kind='KVStore',
            name=alias,
            message=f'KVStore not found: name="{alias}"'
        )


def encoder(alias: str = 'json') -> Any:
    """Returns the requested :class:`Encoder` class.

    :param alias:   encoder alias
    """
    logger.info(f'requesting encoder: name="{alias}"')
    try:
        return m42pl.encoders.ALIASES[alias]
    except KeyError:
        # raise M42PLError(f'Encoder not found: name="{alias}"')
        raise ObjectNotFoundError(
            kind='Encoder',
            name=alias,
            message=f'Encoder not found: name="{alias}"'
        )


def load_module_path(namespace: str, path: str) -> None:
    """Loads a module by path.
    
    :param namespace: Module namespace (e.g. `m42pl.commands`)
    :param path: Module path
    """
    logger.info(f'loading module by path: namespace="{namespace}", path="{path}"')
    # ---
    # Build module name from its basename
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
    module_spec = importlib.util.spec_from_file_location(
        module_name, 
        module_entrypoint
    )
    logger.debug(f'module_from_spec: module_name="{module_name}"')
    module = importlib.util.module_from_spec(module_spec) # type: ignore
    logger.debug(f'exec_module: module_name="{module_name}"')
    module_spec.loader.exec_module(module) # type: ignore
    # ---
    # Register module
    logger.info(f'registering module: module_name="{module_name}"')
    sys.modules[module_spec.name] = module # type: ignore
    IMPORTED_MODULES_PATHS.append(path)
    modules[module_name] = module


def load_module_name(name: str) -> None:
    """Load a module by name.
    
    :param name: Module name.
    """
    logger.info(f'loading module by name: name="{name}"')
    module = importlib.import_module(name)
    IMPORTED_MODULES_NAMES.append(name)
    modules[name] = module


def load_modules(search_paths: list = [], paths: list = [],
                 names: list = [], namespace: str = "m42pl") -> None:
    """Loads modules.
    
    :param search_paths: Modules search paths
    :param paths: Modules paths
    :param names: Modules names
    :param namespace: Modules namespace; Defaults to 'm42pl'
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


def find_modules(items: list = []):
    """Find modules to load.

    :param items: List of modules name, path or paths.
    """
    search_paths = []
    paths = []
    names = []
    # ---
    for item in items:
        # Add item to search path
        if os.path.isdir(item):
            search_paths.append(item)
        # Add item to paths
        elif os.path.isfile(item):
            paths.append(item)
        # Add item to names
        else:
            names.append(item)
    # ---
    load_modules(search_paths, paths, names)


def reload_modules():
    """Reloads previously imported modules.
    """
    global IMPORTED_MODULES_NAMES
    # Build modules selection regex from imported modules list
    modules_rx = regex.compile(f'({"|".join(IMPORTED_MODULES_NAMES)}).*')
    # List of modules to reload
    to_reload = copy.deepcopy(IMPORTED_MODULES_NAMES)
    # List of modules to delete
    deletable = []
    # Build list of modules to unload
    for name, module in sys.modules.items():
        if modules_rx.match(name):
            deletable.append(name)
    # Delete modules
    for name in deletable:
        logger.warning(f'unloading module: {name}')
        del sys.modules[name]
    # Delete remaining modules reference
    for name in IMPORTED_MODULES_NAMES:
        logger.warning(f'unloading module: {name}')
        del modules[name]
    IMPORTED_MODULES_NAMES = []
    # Reload modules
    # for name in BUILTINS_MODULES_NAMES:
    for name in to_reload:
        logger.warning(f'reloading module: {name}')
        load_module_name(name)
