# PythonToolbox
A modular Python Collection of reusable scripts and tools 

---

## 🛠️ Modules Overview

### 1. Logging Framework (logger/)
A centralized logging utility designed for resilient spatial and BIM data pipelines.

* *File:* logger/logger.py
* *Features:* Console logging + rotating log files to handle long-running batch processes cleanly.

#### Quick Start / Usage:
```python
from logger.logger import setup_logger

# Initialize logger
logger = setup_logger()

logger.info("Pipeline execution started.")
```

### 2. IFC Extractor (extractor/)*
A high-performance, memory-safe single-pass ingestion layer using IfcOpenShell.
* *File:* extractor/ifc_extractor.py
* *Features:* $O(n)$ generator-based streaming (yield), per-entity fault isolation, and optional single-pass property/quantity parsing.

### Quick Start / Usage:

```python
from extractor.ifc_extractor import IfcExtractor
from logger.logger import setup_logger

# Initialize logger
logger = setup_logger()

# Initialize extractor
extractor = IfcExtractor("path/to/model.ifc", logger=logger)

# Stream elements efficiently (O(n) generator)
for element in extractor.extract_elements(entity_type="IfcWall", include_quantities=True):
    print(element["name"], element["storey"])
```
