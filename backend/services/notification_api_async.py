"""
Async Notification API
Replaces sync notification API with async processing
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AsyncNotificationAPI:
    """Async notification API with non-blocking operations"""
    
    def __init__(self):
        self.notification_channels = ["email", "sms", "push"]
    
    async def send_booking_confirmation_async(self, context: Dict[str, Any], ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking confirmation asynchronously"""
        try:
            # Simulate async notification sending
            await asyncio.sleep(0.2)  # Simulate API call delay
            
            # Generate notification data
            notification_id = str(uuid.uuid4())[:8]
            
            notification_data = {
                'notification_id': notification_id,
                'type': 'booking_confirmation',
                'ticket': ticket,
                'context': context,
                'sent_at': datetime.now().isoformat(),
                'channels': self.notification_channels,
                'status': 'sent'
            }
            
            logger.info(f"Async booking confirmation sent: {notification_id}")
            return notification_data
            
        except Exception as e:
            logger.error(f"Async booking confirmation failed: {e}")
            return {
                'notification_id': 'error',
                'type': 'booking_confirmation',
                'status': 'failed',
                'error': str(e)
            }
    
    async def send_payment_reminder_async(self, context: Dict[str, Any], payment: Dict[str, Any]) -> Dict[str, Any]:
        """Send payment reminder asynchronously"""
        try:
            # Simulate async notification sending
            await asyncio.sleep(0.1)  # Simulate API call delay
            
            notification_id = str(uuid.uuid4())[:8]
            
            notification_data = {
                'notification_id': notification_id,
                'type': 'payment_reminder',
                'payment': payment,
                'context': context,
                'sent_at': datetime.now().isoformat(),
                'channels': ['email', 'sms'],
                'status': 'sent'
            }
            
            logger.info(f"Async payment reminder sent: {notification_id}")
            return notification_data
            
        except Exception as e:
            logger.error(f"Async payment reminder failed: {e}")
            return {
                'notification_id': 'error',
                'type': 'payment_reminder',
                'status': 'failed',
                'error': str(e)
            }
    
    async def send_flight_update_async(self, context: Dict[str, Any], update_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Send flight update asynchronously"""
        try:
            # Simulate async notification sending
            await asyncio.sleep(0.15)  # Simulate API call delay
            
            notification_id = str(uuid.uuid4())[:8]
            
            notification_data = {
                'notification_id': notification_id,
                'type': 'flight_update',
                'update_type': update_type,
                'details': details,
                'context': context,
                'sent_at': datetime.now().isoformat(),
                'channels': self.notification_channels,
                'status': 'sent'
            }
            
            logger.info(f"Async flight update sent: {notification_id}")
            return notification_data
            
        except Exception as e:
            logger.error(f"Async flight update failed: {e}")
            return {
                'notification_id': 'error',
                'type': 'flight_update',
                'status': 'failed',
                'error': str(e)
            }
    
    async def finalize_and_notify_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize booking and send notifications asynchronously"""
        try:
            # Generate ticket data
            ticket = {
                'pnr': f"PNR{str(uuid.uuid4())[:6].upper()}",
                'route': f"{context.get('from', 'Unknown')} → {context.get('to', 'Unknown')}",
                'date': context.get('date', 'Unknown'),
                'passenger': context.get('passenger_name', 'Traveler'),
                'flight_code': context.get('selected_flight', 'FL123'),
                'price': context.get('selected_price', 5000),
                'booking_time': datetime.now().isoformat()
            }
            
            # Send notifications in parallel
            confirmation_task = self.send_booking_confirmation_async(context, ticket)
            update_task = self.send_flight_update_async(context, 'booking_confirmed', ticket)
            
            # Wait for both notifications to complete
            confirmation_result, update_result = await asyncio.gather(
                confirmation_task,
                update_task,
                return_exceptions=True
            )
            
            # Combine results
            final_result = {
                'ticket': ticket,
                'notifications': {
                    'confirmation': confirmation_result if not isinstance(confirmation_result, Exception) else {'error': str(confirmation_result)},
                    'update': update_result if not isinstance(update_result, Exception) else {'error': str(update_result)}
                },
                'finalized_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            logger.info(f"Async booking finalized: {ticket['pnr']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Async booking finalization failed: {e}")
            return {
                'ticket': {},
                'notifications': {'error': str(e)},
                'status': 'failed',
                'error': str(e)
            }

# Global async notification API instance
_async_notification_api = None

async def get_async_notification_api() -> AsyncNotificationAPI:
    """Get or create async notification API instance"""
    global _async_notification_api
    if _async_notification_api is None:
        _async_notification_api = AsyncNotificationAPI()
    return _async_notification_api

# Async wrapper functions for backward compatibility
async def send_booking_confirmation_async(context: Dict[str, Any], ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for booking confirmation"""
    api = await get_async_notification_api()
    return await api.send_booking_confirmation_async(context, ticket)

async def send_payment_reminder_async(context: Dict[str, Any], payment: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for payment reminder"""
    api = await get_async_notification_api()
    return await api.send_payment_reminder_async(context, payment)

async def send_flight_update_async(context: Dict[str, Any], update_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for flight update"""
    api = await get_async_notification_api()
    return await api.send_flight_update_async(context, update_type, details)

async def finalize_and_notify_async(context: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for booking finalization"""
    api = await get_async_notification_api()
    return await api.finalize_and_notify_async(context)
