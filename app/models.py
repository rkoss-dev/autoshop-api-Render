from app.extensions import db

# Association table for the Many-to-Many relationship between Tickets and Mechanics
ticket_mechanic = db.Table(
    "ticket_mechanic",
    db.Column(
        "ticket_id", db.Integer, db.ForeignKey("service_ticket.id"), primary_key=True
    ),
    db.Column(
        "mechanic_id", db.Integer, db.ForeignKey("mechanic.id"), primary_key=True
    ),
)

# Association table for the Many-to-Many relationship between Tickets and Inventory
ticket_inventory = db.Table(
    "ticket_inventory",
    db.Column(
        "ticket_id", db.Integer, db.ForeignKey("service_ticket.id"), primary_key=True
    ),
    db.Column(
        "inventory_id", db.Integer, db.ForeignKey("inventory.id"), primary_key=True
    ),
)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # One Customer can have many Service Tickets
    tickets = db.relationship("ServiceTicket", backref="customer", lazy=True)


class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    VIN = db.Column(db.String(50), nullable=False)
    service_date = db.Column(db.String(50))
    service_description = db.Column(db.String(200))

    # Foreign Key linking to the Customer
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    # Relationship to Mechanics (using the association table above)
    mechanics = db.relationship(
        "Mechanic", secondary=ticket_mechanic, backref="tickets"
    )

    # Relationship to Inventory (using the association table above)
    parts = db.relationship("Inventory", secondary=ticket_inventory, backref="tickets")


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
