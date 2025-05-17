"""
This is a diagnostic script to test if the new adapter works correctly
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AdapterTest")

def test_adapter():
    """Test if the adapter can be imported and initialized"""
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        
        # Import the adapter
        logger.info("Importing MotoRecommenderAdapter from moto_adapter_correct")
        from moto_adapter_correct import MotoRecommenderAdapter
        
        # Create adapter
        logger.info("Creating adapter instance")
        adapter = MotoRecommenderAdapter()
        
        # Test connection
        logger.info("Testing Neo4j connection")
        connection_status = adapter.test_connection()
        logger.info(f"Connection status: {'SUCCESS' if connection_status else 'FAILED'}")
        
        return connection_status
    
    except Exception as e:
        logger.error(f"Error in adapter test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Starting adapter test")
    result = test_adapter()
    logger.info(f"Test result: {'SUCCESS' if result else 'FAILED'}")
