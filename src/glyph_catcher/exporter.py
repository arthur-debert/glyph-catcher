"""
Module for exporting processed Unicode data to various formats.
"""

import os
import csv
import json
import shutil
import gzip
from typing import Dict, List, Any, Optional

from .types import ExportOptions
from .processor import filter_by_unicode_blocks, filter_by_dataset, load_master_data_file
from .config import get_output_filename


def export_data(
    unicode_data: Dict[str, Dict[str, str]],
    aliases_data: Dict[str, List[str]],
    options: ExportOptions
) -> List[str]:
    """
    Export Unicode data to the specified format(s).
    
    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        options: Export options
        
    Returns:
        List of paths to the generated output files
    """
    # If use_master_file is True and master_file_path is provided, load data from the master file
    if options.use_master_file and options.master_file_path:
        try:
            print(f"Loading data from master file: {options.master_file_path}")
            loaded_unicode_data, loaded_aliases_data = load_master_data_file(options.master_file_path)
            
            if loaded_unicode_data and loaded_aliases_data:
                unicode_data = loaded_unicode_data
                aliases_data = loaded_aliases_data
            else:
                print("Warning: Failed to load data from master file. Using provided data instead.")
        except Exception as e:
            print(f"Error loading master file: {e}")
            print("Using provided data instead.")
    
    # Filter data by dataset or Unicode blocks if specified
    if options.dataset:
        print(f"Filtering data using dataset: {options.dataset}")
        unicode_data, aliases_data = filter_by_dataset(unicode_data, aliases_data, options.dataset)
        print(f"Dataset contains {len(unicode_data)} characters")
    elif options.unicode_blocks:
        print(f"Filtering data to include only these Unicode blocks: {', '.join(options.unicode_blocks)}")
        unicode_data, aliases_data = filter_by_unicode_blocks(unicode_data, aliases_data, options.unicode_blocks)
        print(f"Filtered data contains {len(unicode_data)} characters")
    
    # Create output directory if it doesn't exist
    os.makedirs(options.output_dir, exist_ok=True)
    
    output_files = []
    
    # Determine which formats to export
    formats = ['csv', 'json', 'lua', 'txt'] if options.format_type == 'all' else [options.format_type]
    
    # Export to each format
    # Export to each format
    for fmt in formats:
        # Get the output filename based on format and dataset
        filename = get_output_filename(fmt, options.dataset)
        output_filename = os.path.join(options.output_dir, filename)
        
        # Create a temporary file for uncompressed output
        temp_filename = output_filename
        if options.compress:
            temp_filename = output_filename + ".temp"
        
        if fmt == 'csv':
            write_csv_output(unicode_data, aliases_data, temp_filename)
        elif fmt == 'json':
            write_json_output(unicode_data, aliases_data, temp_filename)
        elif fmt == 'lua':
            write_lua_output(unicode_data, aliases_data, temp_filename)
        elif fmt == 'txt':
            write_txt_output(unicode_data, aliases_data, temp_filename)
        
        # Compress the file if requested
        if options.compress:
            compress_file(temp_filename, output_filename)
            os.remove(temp_filename)  # Remove the temporary uncompressed file
            output_filename = output_filename + ".gz"
            print(f"Data compressed and written to {output_filename}")
        else:
            print(f"Data written to {output_filename}")
        output_files.append(output_filename)
    
    return output_files


def write_csv_output(
    unicode_data: Dict[str, Dict[str, str]],
    aliases_data: Dict[str, List[str]],
    output_filename: str
) -> None:
    """
    Write Unicode data to CSV format.
    
    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        output_filename: Path to the output file
    """
    if not unicode_data:
        print("No Unicode data to write. Aborting CSV creation.")
        return

    # Determine the maximum number of aliases for any character
    max_aliases = 0
    if aliases_data:
        for cp in unicode_data.keys():
            if cp in aliases_data:
                max_aliases = max(max_aliases, len(aliases_data[cp]))

    # Create CSV headers
    headers = ['code_point', 'character', 'name', 'category', 'block']
    for i in range(1, max_aliases + 1):
        headers.append(f'alias_{i}')

    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)

            for code_point_hex, data in unicode_data.items():
                current_aliases = aliases_data.get(code_point_hex, [])
                row = [
                    f"U+{code_point_hex}",
                    data['char_obj'],
                    data['name'],
                    data['category'],
                    data.get('block', 'Unknown Block')
                ]
                for i in range(max_aliases):
                    row.append(current_aliases[i] if i < len(current_aliases) else '')
                writer.writerow(row)

    except Exception as e:
        print(f"Error writing CSV file: {e}")


def write_json_output(
    unicode_data: Dict[str, Dict[str, str]],
    aliases_data: Dict[str, List[str]],
    output_filename: str
) -> None:
    """
    Write Unicode data to JSON format.
    
    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        output_filename: Path to the output file
    """
    if not unicode_data:
        print("No Unicode data to write. Aborting JSON creation.")
        return

    json_data = []
    for code_point_hex, data in unicode_data.items():
        entry = {
            'code_point': f"U+{code_point_hex}",
            'character': data['char_obj'],
            'name': data['name'],
            'category': data['category'],
            'block': data.get('block', 'Unknown Block'),
            'aliases': aliases_data.get(code_point_hex, [])
        }
        json_data.append(entry)

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing JSON file: {e}")


def write_lua_output(
    unicode_data: Dict[str, Dict[str, str]],
    aliases_data: Dict[str, List[str]],
    output_filename: str
) -> None:
    """
    Write Unicode data as a Lua module.
    
    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        output_filename: Path to the output file
    """
    if not unicode_data:
        print("No Unicode data to write. Aborting Lua module creation.")
        return

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("-- Auto-generated unicode data module\n")
            f.write("-- Generated by glyph-catcher\n")
            f.write("return {\n")
            
            for code_point_hex, data in unicode_data.items():
                aliases = aliases_data.get(code_point_hex, [])
                # Handle special characters for Lua
                char = data['char_obj']
                if char == '\n':
                    char = '\\n'
                elif char == '\r':
                    char = '\\r'
                elif char == '\t':
                    char = '\\t'
                elif char == '"':
                    char = '\\"'
                elif char == '\\':
                    char = '\\\\'
                elif ord(char) < 32:  # Other control characters
                    char = f'\\{ord(char):03d}'
                
                # Helper function to properly escape Lua strings
                def escape_lua_string(s):
                    # First escape backslashes
                    s = s.replace('\\', '\\\\')
                    # Then escape other special characters
                    s = s.replace('"', '\\"')
                    s = s.replace('\n', '\\n')
                    s = s.replace('\r', '\\r')
                    s = s.replace('\t', '\\t')
                    # Replace any other control characters
                    result = ""
                    for c in s:
                        if ord(c) < 32 and c not in '\n\r\t':
                            result += f'\\{ord(c):03d}'
                        else:
                            result += c
                    return result
                
                # Escape special characters in all string fields
                name = escape_lua_string(data['name'])
                category = escape_lua_string(data['category'])
                block = escape_lua_string(data.get('block', 'Unknown Block'))
                
                f.write("  {\n")
                f.write(f'    code_point = "U+{code_point_hex}",\n')
                f.write(f'    character = "{char}",\n')
                f.write(f'    name = "{name}",\n')
                f.write(f'    category = "{category}",\n')
                f.write(f'    block = "{block}",\n')
                
                # Write aliases as a Lua table
                if aliases:
                    f.write('    aliases = {\n')
                    for alias in aliases:
                        # Use the same escaping function for aliases
                        escaped_alias = escape_lua_string(alias)
                        f.write(f'      "{escaped_alias}",\n')
                    f.write('    },\n')
                else:
                    f.write('    aliases = {},\n')
                
                f.write("  },\n")
            
            f.write("}\n")
    except Exception as e:
        print(f"Error writing Lua module: {e}")


def write_txt_output(
    unicode_data: Dict[str, Dict[str, str]],
    aliases_data: Dict[str, List[str]],
    output_filename: str
) -> None:
    """
    Write Unicode data in a grep-friendly text format.
    
    Args:
        unicode_data: Dictionary mapping code points to character information
        aliases_data: Dictionary mapping code points to lists of aliases
        output_filename: Path to the output file
    """
    if not unicode_data:
        print("No Unicode data to write. Aborting text file creation.")
        return

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for code_point_hex, data in unicode_data.items():
                # Format: character|name|code_point|category|block|alias1|alias2|...
                # Optimized for grep with searchable fields first
                
                # Create the base parts of the line
                line_parts = [
                    data['char_obj'],
                    data['name'],
                    f"U+{code_point_hex}",
                    data['category'],
                    data.get('block', 'Unknown Block')
                ]
                
                # Add aliases if they exist
                if code_point_hex in aliases_data:
                    line_parts.extend(aliases_data[code_point_hex])
                
                # Join with pipe separator
                f.write('|'.join(line_parts) + '\n')
    except Exception as e:
        print(f"Error writing text file: {e}")


def save_source_files(file_paths: Dict[str, str], output_dir: str) -> None:
    """
    Save the source files to the output directory.
    
    Args:
        file_paths: Dictionary mapping file types to file paths
        output_dir: Directory to save the files to
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get XDG data directory for source files
        xdg_data_dir = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
        source_files_dir = os.path.join(xdg_data_dir, "glyph-catcher", "source-files")
        
        # Create XDG directory if it doesn't exist
        os.makedirs(source_files_dir, exist_ok=True)
        
        # Copy each source file to the XDG data directory
        for file_type, file_path in file_paths.items():
            if os.path.exists(file_path):
                # Map file types to more descriptive filenames
                if file_type == 'unicode_data':
                    filename = 'UnicodeData.txt'
                elif file_type == 'name_aliases':
                    filename = 'NameAliases.txt'
                elif file_type == 'names_list':
                    filename = 'NamesList.txt'
                elif file_type == 'cldr_annotations':
                    filename = 'en.xml'
                else:
                    filename = os.path.basename(file_path)
                
                dest_path = os.path.join(source_files_dir, filename)
                shutil.copy2(file_path, dest_path)
                print(f"Saved source file: {dest_path}")
    except Exception as e:
        print(f"Error saving source files: {e}")


def compress_file(input_filename: str, output_filename: str) -> None:
    """
    Compress a file using gzip with maximum compression level.
    
    Args:
        input_filename: Path to the input file
        output_filename: Path to the output compressed file (without extension)
    """
    try:
        # Use the highest compression level (9) for maximum compression
        with open(input_filename, 'rb') as f_in:
            with gzip.open(output_filename + '.gz', 'wb', compresslevel=9) as f_out:
                f_out.write(f_in.read())
        
        print(f"Compressed {input_filename} to {output_filename}.gz")
    except Exception as e:
        print(f"Error compressing file: {e}")


def decompress_file(input_filename: str, output_filename: str) -> None:
    """
    Decompress a gzip compressed file.
    
    Args:
        input_filename: Path to the compressed input file
        output_filename: Path to the output decompressed file
    """
    try:
        with gzip.open(input_filename, 'rb') as f_in:
            with open(output_filename, 'wb') as f_out:
                f_out.write(f_in.read())
        
        print(f"Decompressed {input_filename} to {output_filename}")
    except Exception as e:
        print(f"Error decompressing file: {e}")