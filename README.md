# misc-scripts
Scripts involving DIY data science pipelines, linux file management, and random useful code snippits. 


# Directory Name Scanner

Fast Python script for finding directories by name patterns on large filesystems.

## Why This Exists

When you need to find folders quickly on massive drives, `find` and `grep` can be painfully slow. This script is optimized for speed by:

- Only scanning directory names (ignores files completely)
- Using efficient filesystem traversal
- Providing real-time progress feedback
- Handling interruptions gracefully

## Setup

### Basic Installation
1. Download `find_dirs.py` to your project directory
2. Optional: Install tqdm for progress bars: `pip install tqdm`

## Parameters/Args

--tqdm: Use progress bar (requires pip install tqdm)
--report-every N: Progress update frequency (default: 1000)
--max-depth N: Stop searching after N levels deep
--skip PATH [PATH ...]: Skip these paths entirely


### For Jupyter Notebooks
```python
# Put find_dirs.py in the same directory as your notebook, then:
import sys
sys.path.append('.')  # if needed
from find_dirs import find_matching_dirs

# Basic usage with progress bar
from find_dirs import find_matching_dirs

matches = find_matching_dirs("/data", ["word1", "word2"], use_tqdm=True)
print(f"Found {len(matches)} directories")

# Show first 10 results
for path in matches[:10]:
    print(path)

# Search with options
matches = find_matching_dirs(
    "/mnt/storage", 
    ["word1", "word2"], 
    use_tqdm=True,
    max_depth=8,
    skip_paths=["/proc", "/sys", "/snap"]
)

# Filter results further
filtered = [m for m in matches if "subfolder" in m]
print(f"Filtered to {len(filtered)} matches")
```

### As Standalone Script
# Basic search
python find_dirs.py /path/to/search word1 word2

# With progress bar and system path exclusion
python find_dirs.py /mnt/storage word1 word2 --tqdm --skip /proc /sys /snap

# Limit search depth
python find_dirs.py /data word1 word2 --max-depth 5






## Requirements

Python 3.7+
Optional: tqdm for progress bars
