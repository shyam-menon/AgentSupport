import os

def get_directory_size(directory: str) -> int:
    """Get total size of a directory in bytes"""
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):  # Skip if it is symbolic link
                total_size += os.path.getsize(fp)
    return total_size
