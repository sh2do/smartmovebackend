import pytest
from datetime import datetime, timezone
from app.models.user import User, UserRole
from app.models.mover import Mover
from app.models.address import Address
from app.models.booking import Booking, BookingStatus

def test_booking_creation(init_database):
    """
    Test that a booking can be created and saved to the database,
    and that its relationships are correctly established.
    """
    # 1. Create associated objects (user, mover, addresses)
    customer = User(email='customer@example.com', role=UserRole.CUSTOMER)
    customer.set_password('password123')

    mover_user = User(email='mover@example.com', role=UserRole.MOVER)
    mover_user.set_password('password456')
    
    init_database.session.add_all([customer, mover_user])
    init_database.session.commit()

    mover = Mover(user_id=mover_user.id, company_name='Rapid Movers')
    
    pickup_addr = Address(
        street='123 Main St', city='Anytown', state='CA', zip_code='12345', user_id=customer.id
    )
    dropoff_addr = Address(
        street='456 Other Ave', city='Someville', state='CA', zip_code='67890', user_id=customer.id
    )

    init_database.session.add_all([mover, pickup_addr, dropoff_addr])
    init_database.session.commit()

    # 2. Create the Booking
    booking_time = datetime.now(timezone.utc)
    new_booking = Booking(
        user_id=customer.id,
        mover_id=mover.id,
        pickup_address_id=pickup_addr.id,
        dropoff_address_id=dropoff_addr.id,
        booking_time=booking_time,
        status=BookingStatus.PENDING
    )
    new_booking.save()
    init_database.session.commit()

    # 3. Assertions
    assert new_booking.id is not None
    assert new_booking.user_id == customer.id
    assert new_booking.mover_id == mover.id
    assert new_booking.status == BookingStatus.PENDING
    assert new_booking.booking_time == booking_time.replace(tzinfo=None)
    
    # Test relationships
    assert new_booking.user == customer
    assert new_booking.mover == mover
    assert new_booking.pickup_address == pickup_addr
    assert new_booking.dropoff_address == dropoff_addr

    # Test back-references
    assert new_booking in customer.bookings
    assert new_booking in mover.bookings
