"""
Module for retrieving raw Unicode data files.
"""

import os
import tempfile
import requests
import shutil
from typing import Optional, Dict

from .types import FetchOptions
from .config import (
    UNICODE_DATA_FILE_URL,
    NAME_ALIASES_FILE_URL,
    NAMES_LIST_FILE_URL,
    CLDR_ANNOTATIONS_URL,
    USER_AGENT,
    DEFAULT_CACHE_DIR,
    TMP_CACHE_DIR,
)


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
            print(f"Using cached file: {cache_path}")
            return cache_path
    try:
        # Create a temporary file in the system's temp directory
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"glyph-catcher-{filename}")
        
        # Add a user agent to avoid rate limiting
        headers = {'User-Agent': USER_AGENT}
        
        print(f"Downloading {url}...")
        try:
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # If cache is enabled, save the file to the cache directory
            if options.use_cache and cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
                cache_path = os.path.join(cache_dir, filename)
                shutil.copy2(temp_file_path, cache_path)
                print(f"Cached file to: {cache_path}")
                # Clean up the temporary file
                os.unlink(temp_file_path)
                return cache_path
            
            return temp_file_path
        except (requests.exceptions.RequestException, Exception) as e:
            print(f"Error downloading {url}: {e}")
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def fetch_all_data_files(options: FetchOptions) -> Dict[str, str]:
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
    
    # Download UnicodeData.txt
    unicode_data_file = download_file(UNICODE_DATA_FILE_URL, options)
    if unicode_data_file:
        result['unicode_data'] = unicode_data_file
    else:
        print("Failed to download UnicodeData.txt")
        return {}
    
    # Download NameAliases.txt
    name_aliases_file = download_file(NAME_ALIASES_FILE_URL, options)
    if name_aliases_file:
        result['name_aliases'] = name_aliases_file
    else:
        print("Failed to download NameAliases.txt")
        return {}
    
    # Download NamesList.txt
    names_list_file = download_file(NAMES_LIST_FILE_URL, options)
    if names_list_file:
        result['names_list'] = names_list_file
    else:
        print("Failed to download NamesList.txt")
        return {}
    
    # Download CLDR annotations (optional)
    cldr_annotations_file = download_file(CLDR_ANNOTATIONS_URL, options)
    if cldr_annotations_file:
        result['cldr_annotations'] = cldr_annotations_file
    else:
        print("Warning: Failed to download CLDR annotations. Continuing without CLDR annotations.")
    
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
        print(f"Cleaning cache directory: {cache_dir}")
        try:
            shutil.rmtree(cache_dir)
            print(f"Cache directory removed: {cache_dir}")
        except Exception as e:
            print(f"Error cleaning cache directory: {e}")