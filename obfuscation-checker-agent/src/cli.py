import argparse
from typing import Any

class CLI:
    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description="Obfuscation Checker Agent")
        parser.add_argument("scan_path", help="Path to the directory to scan")
        parser.add_argument("--config", help="Path to config file", default=None)
        parser.add_argument("--output", help="Output file for report", default=None)
        parser.add_argument("--verbose", action="store_true", help="Verbose output")
        parser.add_argument("--incremental", action="store_true", help="Only scan files changed since last run")
        parser.add_argument("--cache-dir", help="Directory to store cache files", default=".obfuscation_cache")

        return parser.parse_args()

    @staticmethod
    def configure_from_args(config: Any, args: argparse.Namespace) -> None:
        """Configure the config object based on command line arguments."""
        if args.output:
            config.set("output_file", args.output)
        if args.verbose:
            config.set("verbose", True)
