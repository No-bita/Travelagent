from fastapi import APIRouter
from schemas.message_schema import ChatRequest, ChatResponse
from core import flow_controller
from core.state_manager_async import merge_into_session_async
from core.nlp_engine_async import parse_user_input_async
from core.response_generator_async import (
    prompt_for_missing_slots_async,
    format_flight_options_async,
    get_flight_cards_data_async,
    format_payment_prompt_async,
    format_confirmation_async,
    state_summary_async,
    suggest_actions_async,
    safe_fallback_async
)
from services.payment_api_async import generate_payment_link_async
from services.notification_api_async import finalize_and_notify_async
from services.flight_service_async import search_ranked_flights_async
from config import settings
import asyncio
import logging
import time

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Fully async chat endpoint with connection pooling and parallel processing"""
    start_time = time.time()
    
    try:
        # Use async NLP processing for better performance
        nlp_result = await parse_user_input_async(req.message)
        context = await merge_into_session_async(req.session_id, nlp_result)

        action = flow_controller.decide_next_action(context)
        flight_cards = []
        
        if action == "prompt_missing":
            reply = await prompt_for_missing_slots_async(context)
        elif action == "search_flights":
            # Use the async flight service with connection pooling
            flights = await search_ranked_flights_async(context)
            
            # Use async response generation with parallel processing
            reply_task = format_flight_options_async(context, flights)
            cards_task = get_flight_cards_data_async(context, flights)
            
            # Run response generation and flight cards in parallel
            reply, flight_cards = await asyncio.gather(reply_task, cards_task)
            
            context["last_results_count"] = len(flights)
            
            # Log flight search results with timing
            processing_time = time.time() - start_time
            logger.info(f"Async search completed in {processing_time:.2f}s: {len(flights)} flights for {context.get('from')} to {context.get('to')}")
            
        elif action == "request_payment":
            payment = await generate_payment_link_async(context)
            reply = await format_payment_prompt_async(context, payment)
        elif action == "confirm":
            result = await finalize_and_notify_async(context)
            ticket = result.get('ticket', {})
            reply = await format_confirmation_async(context, ticket)
        else:
            reply = await safe_fallback_async()

        # Run state summary and action suggestions in parallel
        summary_task = state_summary_async(context)
        actions_task = suggest_actions_async(context)
        summary, actions = await asyncio.gather(summary_task, actions_task)
        
        # Log total processing time
        total_time = time.time() - start_time
        logger.info(f"Total async processing time: {total_time:.2f}s")
        
        return ChatResponse(reply=reply, state_summary=summary, actions=actions, flight_cards=flight_cards)
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Async chat processing failed after {processing_time:.2f}s: {e}")
        # Return safe fallback response
        return ChatResponse(
            reply="Sorry, I encountered an error. Please try again.",
            state_summary={},
            actions=["Try again", "Start over"],
            flight_cards=[]
        )


