"""
Test script to verify all required packages are working.
"""
import sys

def eprint(*args, **kwargs):
    """Print to stderr to ensure output is visible"""
    print(*args, file=sys.stderr, **kwargs)

eprint(f"Python version: {sys.version}")

try:
    import flask
    eprint(f"Flask version: {flask.__version__}")
except ImportError as e:
    eprint(f"Flask import error: {e}")

try:
    import neo4j
    eprint(f"Neo4j driver version: {neo4j.__version__}")
except ImportError as e:
    eprint(f"Neo4j import error: {e}")

try:
    import numpy
    eprint(f"NumPy version: {numpy.__version__}")
except ImportError as e:
    eprint(f"NumPy import error: {e}")

try:
    import pandas
    eprint(f"Pandas version: {pandas.__version__}")
except ImportError as e:
    eprint(f"Pandas import error: {e}")

try:
    import sklearn
    eprint(f"Scikit-learn version: {sklearn.__version__}")
except ImportError as e:
    eprint(f"Scikit-learn import error: {e}")

try:
    import tensorflow
    eprint(f"TensorFlow version: {tensorflow.__version__}")
except ImportError as e:
    eprint(f"TensorFlow import error: {e}")

try:
    import scipy
    eprint(f"SciPy version: {scipy.__version__}")
except ImportError as e:
    eprint(f"SciPy import error: {e}")

try:
    import matplotlib
    eprint(f"Matplotlib version: {matplotlib.__version__}")
except ImportError as e:
    eprint(f"Matplotlib import error: {e}")

try:
    import seaborn
    eprint(f"Seaborn version: {seaborn.__version__}")
except ImportError as e:
    eprint(f"Seaborn import error: {e}")

try:
    import werkzeug
    eprint(f"Werkzeug version: {werkzeug.__version__}")
except ImportError as e:
    eprint(f"Werkzeug import error: {e}")

try:
    import pytest
    eprint(f"Pytest version: {pytest.__version__}")
except ImportError as e:
    eprint(f"Pytest import error: {e}")

eprint("\nAll import tests completed.")
