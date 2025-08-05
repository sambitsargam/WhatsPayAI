"""
APScheduler Job Scheduler

Manages background tasks for processing deposits and saving state.
"""

import logging
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def process_deposits():
    """
    Background job to process pending deposits.
    
    Checks all addresses in the deposit queue for new incoming transactions
    and credits user balances accordingly.
    """
    try:
        # Import here to avoid circular imports
        from .hathor_client import check_incoming_deposits
        from .app import balances, deposit_queue
        
        if not deposit_queue:
            return
        
        processed_addresses = []
        
        for address, user_info in deposit_queue.items():
            user_id = user_info.get('user_id')
            expected_amount = user_info.get('expected_amount', 0)
            
            if not user_id:
                logger.warning(f"Invalid user_info for address {address}")
                continue
            
            # Check for new deposits
            deposits = check_incoming_deposits(address)
            
            for tx_hash, amount in deposits:
                # Credit user balance
                if user_id not in balances:
                    balances[user_id] = 0.0
                
                balances[user_id] += amount
                
                logger.info(f"Credited {amount} HTR to user {user_id} from tx {tx_hash}")
                
                # Send notification to user (import here to avoid circular imports)
                try:
                    from .twilio_client import send_whatsapp_message_safe
                    import asyncio
                    
                    message = f"✅ Deposit confirmed! {amount} HTR has been added to your account. Current balance: {balances[user_id]} HTR"
                    
                    # Run async function in sync context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(send_whatsapp_message_safe(user_id, message))
                    loop.close()
                    
                except Exception as e:
                    logger.error(f"Failed to send deposit notification: {e}")
            
            # If we found deposits, mark address as processed
            if deposits:
                processed_addresses.append(address)
        
        # Remove processed addresses from queue
        for address in processed_addresses:
            del deposit_queue[address]
            logger.info(f"Removed processed address {address} from deposit queue")
        
    except Exception as e:
        logger.error(f"Error in process_deposits job: {e}")


def save_state_job():
    """
    Background job to periodically save application state to disk.
    """
    try:
        # Import here to avoid circular imports
        from .app import save_state
        save_state()
        
    except Exception as e:
        logger.error(f"Error in save_state job: {e}")


def start_scheduler():
    """
    Initialize and start the background scheduler.
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # Add deposit processing job (every 30 seconds)
        scheduler.add_job(
            process_deposits,
            'interval',
            seconds=30,
            id='process_deposits',
            name='Process Hathor Deposits'
        )
        
        # Add state saving job (every 60 seconds)
        scheduler.add_job(
            save_state_job,
            'interval',
            seconds=60,
            id='save_state',
            name='Save Application State'
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


def stop_scheduler():
    """
    Stop the background scheduler.
    """
    global scheduler
    
    if scheduler is not None:
        try:
            scheduler.shutdown()
            scheduler = None
            logger.info("Background scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")


def get_scheduler_status() -> Dict[str, any]:
    """
    Get current scheduler status and job information.
    
    Returns:
        Dictionary with scheduler status
    """
    if scheduler is None:
        return {"running": False, "jobs": []}
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        "running": scheduler.running,
        "jobs": jobs
    }
