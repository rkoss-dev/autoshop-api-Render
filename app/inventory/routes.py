from flask import jsonify, request

from app.extensions import db
from app.models import Inventory

from . import inventory_bp
from .schemas import inventories_schema, inventory_schema


@inventory_bp.route("/", methods=["POST"])
def create_part():
    """
    Create a new Part
    ---
    tags:
      - Inventory
    summary: Adds a new part to the inventory system.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: InventoryPayload
          type: object
          properties:
            name:
              type: string
              example: "Premium Oil Filter"
            price:
              type: number
              format: float
              example: 14.99
    responses:
      201:
        description: Part successfully created
        schema:
          id: InventoryResponse
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Premium Oil Filter"
            price:
              type: number
              format: float
              example: 14.99
    """
    try:
        new_part = inventory_schema.load(request.json)
        db.session.add(new_part)
        db.session.commit()
        return inventory_schema.jsonify(new_part), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@inventory_bp.route("/", methods=["GET"])
def get_parts():
    """
    Get all Parts
    ---
    tags:
      - Inventory
    summary: Retrieves all parts available in the inventory.
    responses:
      200:
        description: A list of inventory parts
        schema:
          type: array
          items:
            $ref: '#/definitions/InventoryResponse'
    """
    parts = Inventory.query.all()
    return inventories_schema.jsonify(parts), 200


@inventory_bp.route("/", methods=["PUT"])
def update_part(id):
    """
    Update a Part
    ---
    tags:
      - Inventory
    summary: Updates an existing part's name or price.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryPayload'
    responses:
      200:
        description: Part successfully updated
        schema:
          $ref: '#/definitions/InventoryResponse'
    """
    part = Inventory.query.get_or_404(id)
    try:
        inventory_schema.load(request.json, instance=part, partial=True)
        db.session.commit()
        return inventory_schema.jsonify(part), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@inventory_bp.route("/", methods=["DELETE"])
def delete_part(id):
    """
    Delete a Part
    ---
    tags:
      - Inventory
    summary: Removes a part from the inventory.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Part successfully deleted
        schema:
          $ref: '#/definitions/MessageResponse'
    """
    part = Inventory.query.get_or_404(id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part '{part.name}' successfully deleted."}), 200
