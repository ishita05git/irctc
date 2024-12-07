from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Train, Booking

routes = Blueprint('routes', __name__)

# Register user
@routes.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password, role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# Login user and return JWT token
@routes.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        token = create_access_token(identity={'user_id': user.id, 'role': user.role})
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# Add new train (admin only)
@routes.route('/admin/add_train', methods=['POST'])
@jwt_required()
def add_train():
    user_identity = get_jwt_identity()
    if user_identity['role'] != 'admin':
        return jsonify({'message': 'Access forbidden: Admin only'}), 403

    data = request.get_json()
    new_train = Train(source=data['source'], destination=data['destination'], total_seats=data['total_seats'], available_seats=data['total_seats'])
    db.session.add(new_train)
    db.session.commit()
    return jsonify({'message': 'Train added successfully'}), 201

# Get seat availability
@routes.route('/seats/<source>/<destination>', methods=['GET'])
def get_seat_availability(source, destination):
    # Strip whitespace/newline characters
    source = source.strip()
    destination = destination.strip()
    
    print(f"Received request for source: '{source}' and destination: '{destination}'")

    trains = Train.query.filter_by(source=source, destination=destination).all()
    if not trains:
        print(f"No trains found for {source} to {destination}")
        return jsonify([])

    print(f"Found trains: {trains}")

    train_list = [{
        'train_id': train.id,
        'source': train.source,
        'destination': train.destination,
        'available_seats': train.available_seats
    } for train in trains]

    return jsonify(train_list)

# Book a seat
@routes.route('/book_seat', methods=['POST'])
@jwt_required()
def book_seat():
    data = request.get_json()
    user_identity = get_jwt_identity()
    train = Train.query.get(data['train_id'])

    if train and train.available_seats >= data['seats']:
        booking = Booking(user_id=user_identity['user_id'], train_id=train.id, seats_booked=data['seats'])
        train.available_seats -= data['seats']
        db.session.add(booking)
        db.session.commit()
        return jsonify({'message': 'Booking successful', 'booking_id': booking.id}), 201
    return jsonify({'message': 'Not enough seats available'}), 400

# Get booking details
@routes.route('/booking/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking_details(booking_id):
    user_identity = get_jwt_identity()
    booking = Booking.query.get(booking_id)
    if booking and booking.user_id == user_identity['user_id']:
        return jsonify({'user_id': booking.user_id, 'train_id': booking.train_id, 'seats_booked': booking.seats_booked}), 200
    return jsonify({'message': 'Booking not found or unauthorized'}), 404
