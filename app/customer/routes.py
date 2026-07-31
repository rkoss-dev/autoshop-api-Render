from flask import jsonify, request

from app.extensions import db
from app.models import Customer, ServiceTicket
from app.service_ticket.schemas import service_tickets_schema
from app.utils.util import encode_token, token_required

from . import customer_bp
from .schemas import customer_schema, customers_schema, login_schema


@customer_bp.route("/", methods=["POST"])
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    summary: Creates a new customer account.
    description: Takes in customer details and creates a record in the database.
    parameters:
      - in: body
        name: body
        required: true
        description: The customer's details.
        schema:
          id: CustomerPayload
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
    responses:
      201:
        description: Customer successfully created
        schema:
          id: CustomerResponse
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
    """
    try:
        new_customer = customer_schema.load(request.json)
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@customer_bp.route("/", methods=["GET"])
def get_customers():
    """
    Get all Customers
    ---
    tags:
      - Customers
    summary: Retrieves a paginated list of customers.
    description: Returns customers based on page and per_page query parameters.
    parameters:
      - in: query
        name: page
        type: integer
        required: false
        default: 1
      - in: query
        name: per_page
        type: integer
        required: false
        default: 5
    responses:
      200:
        description: A list of customers
        schema:
          type: array
          items:
            $ref: '#/definitions/CustomerResponse'
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    paginated_customers = Customer.query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return customers_schema.jsonify(paginated_customers.items), 200


@customer_bp.route("/login", methods=["POST"])
def login():
    """
    Login Customer
    ---
    tags:
      - Customers
    summary: Authenticates a customer and returns a JWT token.
    description: Validates email and password, returning a Bearer token for protected routes.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: LoginPayload
          type: object
          properties:
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Successful login
        schema:
          id: LoginResponse
          type: object
          properties:
            message:
              type: string
              example: "Login successful"
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      401:
        description: Invalid email or password
    """
    try:
        user_data = login_schema.load(request.json)
    except Exception as e:
        return jsonify({"message": "Invalid format", "errors": str(e)}), 400

    customer = Customer.query.filter_by(email=user_data.email).first()

    if customer and customer.password == user_data.password:
        token = encode_token(customer.id)
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


@customer_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets(customer_id):
    """
    Get Logged-in Customer's Tickets
    ---
    tags:
      - Customers
    summary: Retrieves all service tickets for the authenticated user.
    description: Requires a Bearer token. Returns tickets associated with the logged-in customer's ID.
    security:
      - Bearer: []
    responses:
      200:
        description: A list of the user's service tickets.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              service_description:
                type: string
                example: "Oil Change"
      401:
        description: Unauthorized. Token missing or invalid.
    """
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return service_tickets_schema.jsonify(tickets), 200


@customer_bp.route("/", methods=["PUT"])
@token_required
def update_customer(customer_id, id):
    """
    Update a Customer
    ---
    tags:
      - Customers
    summary: Updates an existing customer's information.
    description: A customer can only update their own account. Requires a Bearer token.
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: The ID of the customer to update.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Johnathan Doe"
    responses:
      200:
        description: Customer successfully updated
        schema:
          $ref: '#/definitions/CustomerResponse'
      403:
        description: Unauthorized to update this account
    """
    if customer_id != id:
        return jsonify({"message": "Unauthorized to update this account."}), 403

    customer = Customer.query.get_or_404(id)
    try:
        customer_schema.load(request.json, instance=customer, partial=True)
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@customer_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(customer_id, id):
    """
    Delete a Customer
    ---
    tags:
      - Customers
    summary: Deletes a customer account.
    description: A customer can only delete their own account. Requires a Bearer token.
    security:
      - Bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
    responses:
      200:
        description: Account successfully deleted
        schema:
          id: MessageResponse
          type: object
          properties:
            message:
              type: string
              example: "Customer 1 successfully deleted."
      403:
        description: Unauthorized to delete this account
    """
    if customer_id != id:
        return jsonify({"message": "Unauthorized to delete this account."}), 403

    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} successfully deleted."}), 200
