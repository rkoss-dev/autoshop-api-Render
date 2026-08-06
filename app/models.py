from app.extensions import db

ticket_mechanic = db.Table(
    "ticket_mechanic",
    db.Column(
        "ticket_id", db.Integer, db.ForeignKey("service_ticket.id"), primary_key=True
    ),
    db.Column(
        "mechanic_id", db.Integer, db.ForeignKey("mechanic.id"), primary_key=True
    ),
)


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

    tickets = db.relationship("ServiceTicket", backref="customer", lazy=True)


class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    VIN = db.Column(db.String(50), nullable=False)
    service_date = db.Column(db.String(50))
    service_description = db.Column(db.String(200))

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    mechanics = db.relationship(
        "Mechanic", secondary=ticket_mechanic, backref="tickets"
    )

    parts = db.relationship("Inventory", secondary=ticket_inventory, backref="tickets")


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
