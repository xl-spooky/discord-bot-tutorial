from __future__ import annotations

__version__ = "1.0-0"
__author__ = "Spooky devs"

import importlib.util
import os
import pkgutil
from collections import abc
from traceback import format_exception
from typing import Any, cast

import disnake
from disnake.ext import commands
from disnake.ext.commands import CommandSyncFlags
from loguru import logger


class TutorialBot(commands.Bot):
    """A subclass of `commands.Bot` that provides automatic discovery and loading of extensions.

    This bot implementation adds utilities for recursively finding and loading
    command extensions from a specified root module or directory. It simplifies
    extension management by allowing developers to point to a single package path
    and have all submodules with commands or a `setup` function automatically loaded.
    """

    def __init__(
        self,
        *,
        command_prefix: str | list[str] | tuple[str, ...],
        intents: disnake.Intents,
        command_sync_flags: CommandSyncFlags = CommandSyncFlags.default(),
        **kwargs: Any,
    ) -> None:
        """Initialize the TutorialBot instance.

        Args
        ----
            command_prefix (str | list[str] | tuple[str, ...]):
                The prefix or list of prefixes under which the bot will respond to commands.
            intents (disnake.Intents):
                The Discord Gateway intents that the bot will subscribe to.
            command_sync_flags (CommandSyncFlags, optional):
                A `CommandSyncFlags` object to control slash-command syncing behavior.
                Defaults to `CommandSyncFlags.default()`.
            **kwargs (Any):
                Additional keyword arguments to pass to the base `commands.Bot` initializer,
                such as `allowed_mentions`, `activity`, `status`, etc.
        """
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            command_sync_flags=command_sync_flags,
            **kwargs,
        )

    def find_extensions(
        self,
        root_module: str,
        *,
        package: str | None = None,
        ignore: abc.Iterable[str] | abc.Callable[[str], bool] | None = None,
    ) -> abc.Sequence[str]:
        """Find all extensions within a given module, including sub-packages.

        The function converts file paths to module names if needed, resolves the root module,
        and then traverses the package to yield extension names.

        Args
        ----
            root_module (str): 
                The root module name or file path containing extensions.
            package (str | None, optional): 
                An optional package name to assist in resolving the module.
            ignore (Iterable[str] | Callable[[str], bool] | None, optional): 
                Patterns or a callable to ignore certain modules.

        Returns
        -------
            Sequence[str]: 
                A tuple of extension module names.
        
        Raises
        ------
            commands.ExtensionError: 
                If the root module is not found or is not a package.
        """
        if "/" in root_module or "\\" in root_module:
            path = os.path.relpath(root_module)
            if ".." in path:
                raise ValueError(
                    "Paths outside the cwd are not supported. Try using the module name instead."
                )
            root_module = path.replace(os.sep, ".")

        # Resolve the root module name using a custom error handling.
        root_module = self._resolve_name(root_module, package)

        if not (spec := importlib.util.find_spec(root_module)):
            raise commands.ExtensionError(
                f"Unable to find root module '{root_module}'", name=root_module
            )

        if not (paths := spec.submodule_search_locations):
            raise commands.ExtensionError(
                f"Module '{root_module}' is not a package", name=root_module
            )

        return tuple(_walk_modules(paths, prefix=f"{spec.name}.", ignore=ignore))

    def load_extensions(
        self,
        root_module: str,
        *,
        package: str | None = None,
        ignore: abc.Iterable[str] | abc.Callable[[str], bool] | None = None,
        load_callback: abc.Callable[[str], None] | None = None,
    ) -> None:
        """Load all extensions from a given module, traversing sub-packages.

        Iterates through the list of found extensions and loads each extension. If an extension
        fails to load, an error is logged and the process continues with the next extension. 
        Optionally, a callback can be invoked for each successfully loaded extension.

        Args
        ----
            root_module (str): 
                The root module name or file path containing extensions.
            package (str | None, optional): 
                An optional package name to assist in resolving the module.
            ignore (Iterable[str] | Callable[[str], bool] | None, optional): 
                Patterns or a callable to ignore certain modules.
            load_callback (Callable[[str], None] | None, optional): 
                An optional callback function that receives the name of each loaded extension.
        """
        for ext_name in self.find_extensions(root_module, package=package, ignore=ignore):
            try:
                self.load_extension(ext_name)
            except commands.ExtensionError as err:
                logger.error(f"Failed to load extension: {ext_name}")
                logger.error("".join(format_exception(err)))
                continue

            if load_callback is not None:
                load_callback(ext_name)


def _walk_modules(
    paths: abc.Iterable[str],
    prefix: str = "",
    ignore: abc.Iterable[str] | abc.Callable[[str], bool] | None = None,
) -> abc.Iterator[str]:
    """Recursively walk through modules in the given paths.

    Traverses through the package directories to yield module names. If an 'ignore' pattern 
    or callable is provided, modules matching the pattern are skipped. Packages with a
    setup function are yielded immediately without further traversal.

    Args
    ----
        paths (Iterable[str]): 
            An iterable of directory paths to search for modules.
        prefix (str, optional): 
            The prefix to prepend to module names.
        ignore (Iterable[str] | Callable[[str], bool] | None, optional): 
            Patterns or a callable to ignore certain modules.

    Returns
    -------
        Iterator[str]: 
            An iterator over module names.
    
    Raises
    ------
        TypeError: 
            If 'ignore' is provided as a string instead of an iterable or callable.
    """
    if isinstance(ignore, str):
        raise TypeError("`ignore` must be an iterable of strings or a callable")

    if isinstance(ignore, abc.Iterable):
        ignore_seq = cast(abc.Iterable[str], ignore)
        ignore_tup = tuple(ignore_seq)
        ignore = lambda path: path.startswith(ignore_tup)  # noqa: E731

    seen: set[str] = set()

    for _, name, ispkg in pkgutil.iter_modules(paths, prefix):
        if ignore and ignore(name):
            continue

        if not ispkg:
            yield name
            continue

        mod = importlib.import_module(name)
        if hasattr(mod, "setup"):
            yield name
            continue

        sub_paths: list[str] = []
        for p in mod.__path__ or []:
            if p not in seen:
                seen.add(p)
                sub_paths.append(p)

        if sub_paths:
            yield from _walk_modules(sub_paths, prefix=f"{name}.", ignore=ignore)
