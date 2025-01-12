import os
import shutil
from datetime import datetime, timedelta
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MarkdownCleaner:
    def __init__(
        self,
        markdown_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "markdown"),
        max_file_age_days: int = 7,
        max_file_count: int = 1000
    ):
        self.markdown_dir = Path(markdown_dir)
        self.max_file_age_days = max_file_age_days
        self.max_file_count = max_file_count

    def get_file_stats(self):
        """Get current statistics about markdown files."""
        if not self.markdown_dir.exists():
            return 0, []
        
        files = list(self.markdown_dir.glob("**/*.md"))
        return len(files), files

    def cleanup_by_age(self):
        """Remove files older than max_file_age_days."""
        if not self.markdown_dir.exists():
            logging.info(f"Directory {self.markdown_dir} does not exist")
            return

        cutoff_date = datetime.now() - timedelta(days=self.max_file_age_days)
        removed_count = 0

        for file_path in self.markdown_dir.glob("**/*.md"):
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    file_path.unlink()
                    removed_count += 1
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")

        logging.info(f"Removed {removed_count} files older than {self.max_file_age_days} days")

    def cleanup_by_count(self):
        """Keep only the newest max_file_count files."""
        if not self.markdown_dir.exists():
            return

        _, files = self.get_file_stats()
        if len(files) <= self.max_file_count:
            return

        # Sort files by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove excess files (keeping the newest ones)
        files_to_remove = files[self.max_file_count:]
        removed_count = 0

        for file_path in files_to_remove:
            try:
                file_path.unlink()
                removed_count += 1
            except Exception as e:
                logging.error(f"Error removing {file_path}: {str(e)}")

        logging.info(f"Removed {removed_count} excess files, keeping {self.max_file_count} newest files")

    def cleanup_empty_dirs(self):
        """Remove empty subdirectories."""
        if not self.markdown_dir.exists():
            return

        for dirpath, dirnames, filenames in os.walk(self.markdown_dir, topdown=False):
            if dirpath != str(self.markdown_dir) and not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                    logging.info(f"Removed empty directory: {dirpath}")
                except Exception as e:
                    logging.error(f"Error removing directory {dirpath}: {str(e)}")

    def run_cleanup(self):
        """Run all cleanup operations."""
        initial_count, _ = self.get_file_stats()
        logging.info(f"Starting cleanup. Initial file count: {initial_count}")

        self.cleanup_by_age()
        self.cleanup_by_count()
        self.cleanup_empty_dirs()

        final_count, _ = self.get_file_stats()
        logging.info(f"Cleanup complete. Final file count: {final_count}")
        logging.info(f"Removed {initial_count - final_count} files")


if __name__ == "__main__":
    cleaner = MarkdownCleaner()
    cleaner.run_cleanup()
