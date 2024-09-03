from flask import jsonify, Blueprint, request

routes_bp = Blueprint("trips_routes", __name__)

@routes_bp.route("/endpoint", methods=["POST"])
def route_function():
    return None