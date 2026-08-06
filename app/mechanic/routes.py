from flask import jsonify, request

from app.extensions import cache, db
from app.models import Mechanic

from . import mechanic_bp
from .schemas import mechanic_schema, mechanics_schema


@mechanic_bp.route("/", methods=["POST"])
def create_mechanic():
    """
    Create a new Mechanic
    ---
    tags:
      - Mechanics
    summary: Adds a new mechanic to the shop.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: MechanicPayload
          type: object
          properties:
            name:
              type: string
              example: "Jane Smith"
    responses:
      201:
        description: Mechanic successfully created
        schema:
          id: MechanicResponse
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Jane Smith"
    """
    try:
        new_mechanic = mechanic_schema.load(request.json)
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@mechanic_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)
def get_mechanics():
    """
    Get all Mechanics
    ---
    tags:
      - Mechanics
    summary: Retrieves all mechanics (Cached).
    description: Returns a list of all mechanics in the database. Results are cached for 60 seconds.
    responses:
      200:
        description: A list of mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
    """
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    """
    Update a Mechanic
    ---
    tags:
      - Mechanics
    summary: Updates an existing mechanic's details.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicPayload'
    responses:
      200:
        description: Mechanic successfully updated
        schema:
          $ref: '#/definitions/MechanicResponse'
    """
    mechanic = Mechanic.query.get_or_404(id)
    try:
        mechanic_schema.load(request.json, instance=mechanic, partial=True)
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@mechanic_bp.route("/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    """
    Delete a Mechanic
    ---
    tags:
      - Mechanics
    summary: Removes a mechanic from the system.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Mechanic successfully deleted
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Mechanic 1 deleted."
    """
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted."}), 200


@mechanic_bp.route("/top-mechanics", methods=["GET"])
def get_top_mechanics():
    """
    Get Top Mechanics
    ---
    tags:
      - Mechanics
    summary: Ranks mechanics by workload.
    description: Returns a list of mechanics ordered from most service tickets to least.
    responses:
      200:
        description: A sorted list of mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/MechanicResponse'
    """

    mechanics = Mechanic.query.all()

    mechanics.sort(key=lambda m: len(m.tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200
