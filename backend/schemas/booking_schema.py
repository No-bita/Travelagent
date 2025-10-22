"""
Booking Schema
Defines booking models, payment integration, and ticket management
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from enum import Enum
import uuid

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PassengerType(str, Enum):
    ADULT = "adult"
    CHILD = "child"
    INFANT = "infant"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class PassengerDetails(BaseModel):
    """Passenger information for booking"""
    passenger_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    middle_name: Optional[str] = Field(None, max_length=50, description="Middle name")
    date_of_birth: date = Field(..., description="Date of birth")
    gender: Gender = Field(..., description="Gender")
    passenger_type: PassengerType = Field(..., description="Passenger type")
    nationality: str = Field(default="IN", description="Nationality code")
    passport_number: Optional[str] = Field(None, description="Passport number")
    passport_expiry: Optional[date] = Field(None, description="Passport expiry date")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    emergency_contact: Optional[str] = Field(None, description="Emergency contact number")
    special_requests: Optional[str] = Field(None, description="Special requests or needs")
    
    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation
        if not v or len(v.replace(' ', '').replace('-', '').replace('+', '')) < 10:
            raise ValueError('Invalid phone number')
        return v

class SeatSelection(BaseModel):
    """Seat selection details"""
    seat_number: str = Field(..., description="Seat number (e.g., 12A)")
    seat_type: str = Field(..., description="Seat type (window, aisle, middle)")
    seat_class: str = Field(..., description="Seat class (economy, business, first)")
    price: float = Field(..., ge=0, description="Seat price")
    passenger_id: str = Field(..., description="Associated passenger ID")

class FlightSegment(BaseModel):
    """Flight segment details"""
    segment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    flight_number: str = Field(..., description="Flight number")
    airline_code: str = Field(..., description="Airline code")
    departure_airport: str = Field(..., description="Departure airport code")
    arrival_airport: str = Field(..., description="Arrival airport code")
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    duration: str = Field(..., description="Flight duration")
    aircraft_type: Optional[str] = Field(None, description="Aircraft type")
    terminal_departure: Optional[str] = Field(None, description="Departure terminal")
    terminal_arrival: Optional[str] = Field(None, description="Arrival terminal")
    baggage_allowance: Optional[str] = Field(None, description="Baggage allowance")

class BookingRequest(BaseModel):
    """Complete booking request"""
    user_id: str = Field(..., description="User ID making the booking")
    session_id: str = Field(..., description="Session ID")
    flight_segments: List[FlightSegment] = Field(..., min_items=1, description="Flight segments")
    passengers: List[PassengerDetails] = Field(..., min_items=1, max_items=9, description="Passenger details")
    seat_selections: List[SeatSelection] = Field(default_factory=list, description="Seat selections")
    contact_email: EmailStr = Field(..., description="Contact email for booking")
    contact_phone: str = Field(..., description="Contact phone for booking")
    special_requests: Optional[str] = Field(None, description="Special requests")
    insurance_required: bool = Field(default=False, description="Travel insurance required")
    meal_preferences: Dict[str, str] = Field(default_factory=dict, description="Meal preferences by passenger")
    
    @validator('passengers')
    def validate_passengers(cls, v):
        if not v:
            raise ValueError('At least one passenger is required')
        return v

class PaymentDetails(BaseModel):
    """Payment information"""
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float = Field(..., ge=0, description="Payment amount")
    currency: str = Field(default="INR", description="Currency code")
    payment_method: str = Field(..., description="Payment method (card, netbanking, upi, wallet)")
    payment_gateway: str = Field(default="razorpay", description="Payment gateway")
    gateway_transaction_id: Optional[str] = Field(None, description="Gateway transaction ID")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    payment_url: Optional[str] = Field(None, description="Payment URL for redirect")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Payment completion time")

class BookingDetails(BaseModel):
    """Complete booking details"""
    booking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_reference: str = Field(..., description="Booking reference number")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    flight_segments: List[FlightSegment] = Field(..., description="Flight segments")
    passengers: List[PassengerDetails] = Field(..., description="Passenger details")
    seat_selections: List[SeatSelection] = Field(default_factory=list, description="Seat selections")
    total_amount: float = Field(..., ge=0, description="Total booking amount")
    base_fare: float = Field(..., ge=0, description="Base fare amount")
    taxes_fees: float = Field(..., ge=0, description="Taxes and fees")
    seat_charges: float = Field(default=0, ge=0, description="Seat selection charges")
    insurance_amount: float = Field(default=0, ge=0, description="Insurance amount")
    booking_status: BookingStatus = Field(default=BookingStatus.PENDING, description="Booking status")
    payment_details: PaymentDetails = Field(..., description="Payment information")
    contact_email: EmailStr = Field(..., description="Contact email")
    contact_phone: str = Field(..., description="Contact phone")
    special_requests: Optional[str] = Field(None, description="Special requests")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Booking expiry time")
    
    def calculate_total(self):
        """Calculate total amount"""
        self.total_amount = (
            self.base_fare + 
            self.taxes_fees + 
            self.seat_charges + 
            self.insurance_amount
        )
        return self.total_amount

class TicketDetails(BaseModel):
    """Ticket information"""
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str = Field(..., description="Associated booking ID")
    passenger_id: str = Field(..., description="Passenger ID")
    ticket_number: str = Field(..., description="Airline ticket number")
    seat_number: str = Field(..., description="Seat number")
    flight_segments: List[FlightSegment] = Field(..., description="Flight segments for this ticket")
    status: str = Field(default="confirmed", description="Ticket status")
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = Field(None, description="Ticket validity")

class BookingResponse(BaseModel):
    """Booking response"""
    booking_id: str
    booking_reference: str
    booking_status: BookingStatus
    payment_url: Optional[str] = None
    total_amount: float
    passengers: List[PassengerDetails]
    flight_segments: List[FlightSegment]
    expires_at: Optional[datetime] = None
    success: bool = True
    message: str = "Booking created successfully"

class PaymentResponse(BaseModel):
    """Payment response"""
    payment_id: str
    payment_url: str
    amount: float
    currency: str
    payment_status: PaymentStatus
    expires_at: datetime
    success: bool = True
    message: str = "Payment initiated successfully"

class BookingConfirmation(BaseModel):
    """Booking confirmation details"""
    booking_id: str
    booking_reference: str
    booking_status: BookingStatus
    payment_status: PaymentStatus
    tickets: List[TicketDetails]
    total_amount: float
    contact_email: EmailStr
    contact_phone: str
    flight_segments: List[FlightSegment]
    passengers: List[PassengerDetails]
    seat_selections: List[SeatSelection]
    booking_date: datetime
    success: bool = True
    message: str = "Booking confirmed successfully"

class BookingCancellation(BaseModel):
    """Booking cancellation request"""
    booking_id: str = Field(..., description="Booking ID to cancel")
    reason: Optional[str] = Field(None, description="Cancellation reason")
    refund_requested: bool = Field(default=True, description="Request refund")
    
class CancellationResponse(BaseModel):
    """Cancellation response"""
    booking_id: str
    cancellation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    refund_amount: float
    refund_status: str
    cancellation_fee: float
    success: bool = True
    message: str = "Booking cancelled successfully"
