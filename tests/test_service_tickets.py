import unittest

from app import create_app
from app.extensions import db
from app.models import Customer, Inventory, Mechanic, ServiceTicket


class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["RATELIMIT_ENABLED"] = False

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            customer = Customer(name="Alice", email="alice@test.com", password="pass")
            mechanic = Mechanic(name="Bob Builder")
            part = Inventory(name="Spark Plug", price=9.99)

            db.session.add_all([customer, mechanic, part])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    # --- POSITIVE TESTS ---
    def test_create_ticket_success(self):
        """Test successfully creating a ticket for an existing customer."""
        payload = {
            "VIN": "1A2B3C4D",
            "service_date": "2023-12-01",
            "service_description": "Engine Check",
            "customer_id": 1,
        }
        response = self.client.post("/service-tickets/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertIn("1A2B3C4D", str(response.data))

    def test_assign_mechanic_success(self):
        """Test assigning a mechanic to a ticket."""
        with self.app.app_context():
            ticket = ServiceTicket(VIN="123", customer_id=1)
            db.session.add(ticket)
            db.session.commit()

        response = self.client.put("/service-tickets/1/assign-mechanic/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn("assigned", str(response.data))

    def test_add_part_to_ticket(self):
        """Test adding an inventory part to a ticket."""
        with self.app.app_context():
            ticket = ServiceTicket(VIN="123", customer_id=1)
            db.session.add(ticket)
            db.session.commit()

        response = self.client.put("/service-tickets/1/add-part/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Spark Plug", str(response.data))

    # --- NEGATIVE TESTS ---
    def test_create_ticket_invalid_customer(self):
        """Test creating a ticket with a customer_id that doesn't exist."""
        payload = {
            "VIN": "1A2B3C4D",
            "customer_id": 999,
        }
        response = self.client.post("/service-tickets/", json=payload)

        self.assertEqual(response.status_code, 400)

    def test_assign_mechanic_already_assigned(self):
        """Test that assigning the same mechanic twice returns an error."""
        with self.app.app_context():
            ticket = ServiceTicket(VIN="123", customer_id=1)
            mechanic = db.session.get(Mechanic, 1)
            ticket.mechanics.append(mechanic)
            db.session.add(ticket)
            db.session.commit()

        response = self.client.put("/service-tickets/1/assign-mechanic/1")

        self.assertEqual(response.status_code, 400)
        self.assertIn("already assigned", str(response.data))

    def test_remove_mechanic_not_assigned(self):
        """Test removing a mechanic who isn't even working on the ticket."""
        with self.app.app_context():
            ticket = ServiceTicket(VIN="123", customer_id=1)
            db.session.add(ticket)
            db.session.commit()

        response = self.client.put("/service-tickets/1/remove-mechanic/1")

        self.assertEqual(response.status_code, 400)
        self.assertIn("not assigned", str(response.data))
