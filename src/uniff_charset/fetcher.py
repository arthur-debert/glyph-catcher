"""
Module for retrieving raw Unicode data files.
"""

import logging
import os
import shutil
import tempfile
from typing import Optional

import requests
from uniff_core.types import FetchOptions

from .config import (
    CLDR_ANNOTATIONS_URL,
    DEFAULT_CACHE_DIR,
    NAME_ALIASES_FILE_URL,
    NAMES_LIST_FILE_URL,
    TMP_CACHE_DIR,
    UNICODE_DATA_FILE_URL,
    USER_AGENT,
)

logger = logging.getLogger("uniff")


def download_file(url: str, options: FetchOptions) -> Optional[str]:
    """
    Download a file from a URL to a temporary file and return its path.

    Args:
        url: URL to download from
        options: Fetch options including cache settings

    Returns:
        Path to the downloaded file, or None if download failed
    """
    # Extract the filename from the URL
    filename = os.path.basename(url)

    # Determine which cache directory to use
    cache_dir = options.cache_dir
    if options.use_temp_cache:
        cache_dir = TMP_CACHE_DIR
    elif not cache_dir and options.use_cache:
        cache_dir = DEFAULT_CACHE_DIR

    # If cache is enabled, check if the file exists in the cache directory
    if options.use_cache and cache_dir:
        cache_path = os.path.join(cache_dir, filename)
        if os.path.exists(cache_path):
            logger.debug(f"Using cached file: {cache_path}")
            return cache_path
    try:
        # Create a temporary file in the system's temp directory
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"uniff-gen-{filename}")

        # Add a user agent to avoid rate limiting
        headers = {"User-Agent": USER_AGENT}
        logger.debug(f"Downloading file from {url}")

        try:
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()

            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # If cache is enabled, save the file to the cache directory
            if options.use_cache and cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
                cache_path = os.path.join(cache_dir, filename)
                shutil.copy2(temp_file_path, cache_path)
                logger.debug(f"Saved file to cache: {cache_path}")
                # Clean up the temporary file
                os.unlink(temp_file_path)
                return cache_path

            logger.debug(f"Saved file to temporary location: {temp_file_path}")
            return temp_file_path
        except (requests.exceptions.RequestException, Exception) as e:
            logger.debug(f"Error downloading file {url}: {str(e)}")
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return None
    except Exception as e:
        logger.debug(f"Error handling file {url}: {str(e)}")
        return None


def fetch_all_data_files(options: FetchOptions) -> dict[str, str]:
    """
    Fetch all required Unicode data files.

    Args:
        options: Fetch options including cache settings

    Returns:
        Dictionary mapping file types to file paths:
        {
            'unicode_data': path_to_unicode_data_file,
            'name_aliases': path_to_name_aliases_file,
            'names_list': path_to_names_list_file,
            'cldr_annotations': path_to_cldr_annotations_file
        }
        Empty dictionary if any required file failed to download
    """
    result = {}
    logger.debug("Starting download of Unicode data files")

    # Download UnicodeData.txt
    logger.debug("Downloading UnicodeData.txt")
    unicode_data_file = download_file(UNICODE_DATA_FILE_URL, options)
    if unicode_data_file:
        result["unicode_data"] = unicode_data_file
    else:
        return {}

    # Download NameAliases.txt
    logger.debug("Downloading NameAliases.txt")
    name_aliases_file = download_file(NAME_ALIASES_FILE_URL, options)
    if name_aliases_file:
        result["name_aliases"] = name_aliases_file
    else:
        return {}

    # Download NamesList.txt
    logger.debug("Downloading NamesList.txt")
    names_list_file = download_file(NAMES_LIST_FILE_URL, options)
    if names_list_file:
        result["names_list"] = names_list_file
    else:
        return {}

    # Download CLDR annotations (optional)
    logger.debug("Downloading CLDR annotations")
    cldr_annotations_file = download_file(CLDR_ANNOTATIONS_URL, options)
    if cldr_annotations_file:
        result["cldr_annotations"] = cldr_annotations_file
    else:
        logger.debug("CLDR annotations download failed (optional)")

    logger.debug("Successfully downloaded all required data files")
    return result


def clean_cache(options: FetchOptions) -> None:
    """
    Clean up cache directories.

    Args:
        options: Fetch options including cache settings
    """
    # Determine which cache directory to clean
    cache_dir = options.cache_dir
    if options.use_temp_cache:
        cache_dir = TMP_CACHE_DIR
    elif not cache_dir and options.use_cache:
        cache_dir = DEFAULT_CACHE_DIR

    if cache_dir and os.path.exists(cache_dir):
        logger.debug(f"Cleaning cache directory: {cache_dir}")
        try:
            shutil.rmtree(cache_dir)
            logger.debug(f"Cache directory removed: {cache_dir}")
        except Exception as e:
            logger.debug(f"Error cleaning cache directory: {e}")
