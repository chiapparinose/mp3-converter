#!/usr/bin/env python3
"""
YouTube to MP3 Converter - Main Entry Point

A command-line tool to convert YouTube videos to MP3 audio files.
"""

import sys
from src.cli import main


if __name__ == '__main__':
    sys.exit(main())
