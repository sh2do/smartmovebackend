from flask import Blueprint, request, g # Import g
from app.models.review import Review
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required
from app.utils.validators import validate_request

review_bp = Blueprint('review', __name__, url_prefix='/reviews')

@review_bp.route('', methods=['POST'])
@jwt_required
@validate_request('booking_id', 'rating', 'comment')
def create_review():
    current_user = g.current_user
    data = request.get_json()
    data['user_id'] = current_user.id
    try:
        review = Review.create(data)
        return success(review.to_dict(), 201)
    except Exception as e:
        return error_response(str(e))

@review_bp.route('/mover/<int:mover_id>', methods=['GET'])
def get_mover_reviews(mover_id):
    try:
        reviews = Review.query.filter_by(mover_id=mover_id).all()
        return success([r.to_dict() for r in reviews])
    except Exception as e:
        return error_response(str(e))
