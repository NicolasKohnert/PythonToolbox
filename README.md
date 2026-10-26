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
