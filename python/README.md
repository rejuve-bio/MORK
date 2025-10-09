## MORK Dataset Loader

Load MeTTa dataset files into a MORK server for processing and querying.

### Usage

**Load dataset:**
```bash
python load_metta.py --path /path/to/metta/files --port 8431 --space annotation
```

**Clear and reload**
```bash
python load_metta.py --path /path/to/metta/files --port 8431 --space annotation --clear
```

**Clear space only:**
```bash
python load_metta.py --clear --space annotation --port 8431
```

**Options**
- `--path, -p`: Directory containing .metta files
- `--port`: MORK server port (required)
- `--space, -s`: Target MORK space (required)
- `--clear, -c`: Clear before loading or clear-only mode
- `--verbose, -v`: Enable detailed output