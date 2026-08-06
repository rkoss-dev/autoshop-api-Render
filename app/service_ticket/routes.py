from flask import jsonify, request

from app.extensions import db, limiter
from app.models import Customer, Inventory, Mechanic, ServiceTicket

from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema


@service_ticket_bp.route("/", methods=["POST"])
@limiter.limit("3 per minute")
def create_service_ticket():
    """
    Create a Service Ticket
    ---
    tags:
      - Service Tickets
    summary: Creates a new service ticket (Rate Limited).
    description: Limited to 3 requests per minute per IP to prevent spam.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: ServiceTicketPayload
          type: object
          properties:
            VIN:
              type: string
              example: "1234ABCD"
            service_date:
              type: string
              example: "2023-11-01"
            service_description:
              type: string
              example: "Oil Change"
            customer_id:
              type: integer
              example: 1
    responses:
      201:
        description: Ticket successfully created
        schema:
          id: ServiceTicketResponse
          type: object
          properties:
            id:
              type: integer
              example: 1
            VIN:
              type: string
              example: "1234ABCD"
            service_date:
              type: string
              example: "2023-11-01"
            service_description:
              type: string
              example: "Oil Change"
            customer_id:
              type: integer
              example: 1
            mechanics:
              type: array
              items:
                $ref: '#/definitions/MechanicResponse'
            parts:
              type: array
              items:
                $ref: '#/definitions/InventoryResponse'
    """

    try:
        data = request.json

        # --- NEW API VALIDATION ---
        # Look up the customer before we try to create the ticket
        customer_id = data.get("customer_id")
        customer = db.session.get(Customer, customer_id)

        if not customer:
            return jsonify(
                {"message": f"Invalid customer_id: {customer_id} does not exist."}
            ), 400
        # --------------------------

        new_ticket = service_ticket_schema.load(data)
        db.session.add(new_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(new_ticket), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 400


@service_ticket_bp.route("/", methods=["GET"])
def get_service_tickets():
    """
    Get all Service Tickets
    ---
    tags:
      - Service Tickets
    summary: Retrieves all service tickets.
    description: Returns a list of tickets, including nested mechanics and parts data.
    responses:
      200:
        description: A list of service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicketResponse'
    """
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200


@service_ticket_bp.route(
    "/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def assign_mechanic(ticket_id, mechanic_id):
    """
    Assign a Mechanic
    ---
    tags:
      - Service Tickets
    summary: Assigns a single mechanic to a service ticket.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: path
        name: mechanic_id
        type: integer
        required: true
    responses:
      200:
        description: Mechanic assigned
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Mechanic assigned."
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({"message": "Mechanic assigned."}), 200

    return jsonify({"message": "Mechanic already assigned."}), 400


@service_ticket_bp.route(
    "/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def remove_mechanic(ticket_id, mechanic_id):
    """
    Remove a Mechanic
    ---
    tags:
      - Service Tickets
    summary: Removes a single mechanic from a service ticket.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: path
        name: mechanic_id
        type: integer
        required: true
    responses:
      200:
        description: Mechanic removed
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Mechanic removed."
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)  # Remove from the list
        db.session.commit()
        return jsonify({"message": "Mechanic removed."}), 200

    return jsonify({"message": "Mechanic not assigned."}), 400


@service_ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def edit_ticket_mechanics(ticket_id):
    """
    Bulk Edit Mechanics
    ---
    tags:
      - Service Tickets
    summary: Add and remove multiple mechanics at once.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          id: BulkEditPayload
          type: object
          properties:
            add_ids:
              type: array
              items:
                type: integer
              example: [1, 2]
            remove_ids:
              type: array
              items:
                type: integer
              example: [3]
    responses:
      200:
        description: Ticket updated successfully
        schema:
          $ref: '#/definitions/ServiceTicketResponse'
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    data = request.json
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    for mech_id in add_ids:
        mechanic = Mechanic.query.get(mech_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mech_id in remove_ids:
        mechanic = Mechanic.query.get(mech_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["PUT"])
def add_part(ticket_id, part_id):
    """
    Add a Part to Ticket
    ---
    tags:
      - Service Tickets
    summary: Attaches an inventory part to a service ticket.
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
      - in: path
        name: part_id
        type: integer
        required: true
    responses:
      200:
        description: Part added
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Part 'Spark Plug' added to Ticket #1."
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    part = Inventory.query.get_or_404(part_id)

    if part not in ticket.parts:
        ticket.parts.append(part)
        db.session.commit()
        return jsonify(
            {"message": f"Part '{part.name}' added to Ticket #{ticket_id}."}
        ), 200

    return jsonify({"message": "This part is already attached to this ticket."}), 400
