from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_certificate_task(enrollment_id):
    """
    Mock task to simulate heavy certificate generation process (e.g. PDF rendering).
    In a real scenario, this would generate a PDF and save it to the Media storage.
    """
    logger.info(f"Starting certificate generation for enrollment {enrollment_id}")
    
    # Simulate heavy processing
    time.sleep(5) 
    
    # Here we would normally:
    # 1. Fetch enrollment data
    # 2. Render HTML template to PDF
    # 3. Save PDF file
    # 4. Update enrollment with certificate file path
    # 5. Send email with certificate attachment
    
    logger.info(f"Certificate generation completed for enrollment {enrollment_id}")
    return f"Certificate generated for enrollment {enrollment_id}"
