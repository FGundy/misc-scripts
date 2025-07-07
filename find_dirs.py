#!/usr/bin/env python3
"""
Quick directory name scanner - finds folders containing specific substrings.
Faster than find/grep for large filesystems since it skips files entirely.
"""
import argparse
import os
import re
from collections import deque
from pathlib import Path
from typing import List

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


def _is_under(path: Path, root: Path) -> bool:
    """Check if path is under root without string operations."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def find_matching_dirs(root: str, patterns: List[str], report_every=1000, use_tqdm=False, max_depth=None, skip_paths=None, breadth_first=False):
    """
    Walk directory tree and find folders whose names contain any of the patterns.
    
    Args:
        root: Starting directory 
        patterns: List of substrings to search for (case-insensitive)
        report_every: Progress update frequency
        use_tqdm: Use progress bar if available
        max_depth: Stop after this depth (root = depth 0)
        skip_paths: Paths to completely avoid (optional)
        breadth_first: Use breadth-first instead of depth-first search
    
    Returns:
        List of matching directory paths
    """
    # compile regex once for speed - avoids repeated string operations
    regex = re.compile("|".join(re.escape(p) for p in patterns), re.IGNORECASE)
    
    # initialize variables
    matches = []
    count = 0
    skip_list = [Path(p).resolve() for p in (skip_paths or [])]
    pbar = None
    root_path = Path(root).resolve()  # ensure root is a Path object
    
    # setup progress reporting
    if use_tqdm and HAS_TQDM:
        pbar = tqdm(unit="dirs")
        def progress(scanned, found):
            if scanned % report_every == 0:
                pbar.set_postfix(scanned=f"{scanned:,}", found=found)
                pbar.update(report_every)  # batch update instead of every single dir
    else:
        def progress(scanned, found):
            if scanned % report_every == 0:
                print(f"\rScanned {scanned:,} dirs, found {found}", end="", flush=True)
    
    try:
        # NOTE: we never touch files - stats on terabytes would kill us
        if breadth_first:
            # breadth-first search using queue
            queue = deque([(root_path, 0)])  # (path, depth)
            
            while queue:
                current_dir, depth = queue.popleft()
                count += 1
                
                # skip unwanted paths first (before expensive is_dir checks)
                if any(_is_under(current_dir, skip) for skip in skip_list):
                    continue
                    
                # check depth limit
                if max_depth is not None and depth > max_depth:
                    continue
                
                # test directory name against patterns
                if regex.search(current_dir.name):
                    matches.append(str(current_dir))
                
                # enumerate subdirectories and add to queue
                try:
                    with os.scandir(current_dir) as entries:
                        for entry in entries:
                            if entry.is_dir(follow_symlinks=False):
                                queue.append((Path(entry.path), depth + 1))
                except (PermissionError, OSError):
                    continue  # skip directories we can't read
                
                progress(count, len(matches))
        else:
            # original depth-first search
            for dirpath, dirnames, _ in os.walk(root_path, onerror=lambda e: None, followlinks=False):
                count += 1
                current_path = Path(dirpath)
                
                # check depth limit - max_depth levels beneath root (root = depth 0)
                if max_depth is not None and len(current_path.relative_to(root_path).parts) > max_depth:
                    dirnames.clear()
                    continue
                    
                # skip unwanted paths using proper path comparison
                if any(_is_under(current_path, skip) for skip in skip_list):
                    dirnames.clear()
                    continue
                
                # test directory name against patterns
                if regex.search(current_path.name):
                    matches.append(dirpath)
                
                progress(count, len(matches))
            
    except KeyboardInterrupt:
        print(f"\nStopped by user. Scanned {count:,} dirs so far.")
    finally:
        if pbar is not None:
            # flush any leftover increments so the bar totals match count
            leftover = count % report_every
            if leftover:
                pbar.update(leftover)
            pbar.close()
        print(f"\nDone. Scanned {count:,} directories, found {len(matches)} matches.")
    
    return matches


def main():
    parser = argparse.ArgumentParser(description="Find directories by name patterns")
    parser.add_argument("root", help="Starting directory")
    parser.add_argument("patterns", nargs="+", help="Substrings to search for")
    parser.add_argument("--report-every", type=int, default=1000, help="Progress update frequency")
    parser.add_argument("--tqdm", action="store_true", help="Use tqdm progress bar")
    parser.add_argument("--max-depth", type=int, help="Maximum depth to search (root = depth 0)")
    parser.add_argument("--skip", nargs="*", help="Paths to skip (e.g. /proc /sys)")
    parser.add_argument("--breadth-first", action="store_true", help="Use breadth-first search (may be faster)")
    
    args = parser.parse_args()
    
    results = find_matching_dirs(
        args.root,
        args.patterns,
        report_every=args.report_every,
        use_tqdm=args.tqdm,
        max_depth=args.max_depth,
        skip_paths=args.skip,
        breadth_first=args.breadth_first
    )
    
    # print results one per line
    for path in results:
        print(path)


if __name__ == "__main__":
    main()