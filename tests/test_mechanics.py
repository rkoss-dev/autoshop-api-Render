import json
import unittest

from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic, ServiceTicket


class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    # --- POSITIVE TESTS ---
    def test_create_mechanic_success(self):
        """Test successfully creating a new mechanic."""
        payload = {"name": "Mike wrench"}
        response = self.client.post("/mechanics/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Mike wrench", str(response.data))

    def test_get_mechanics_success(self):
        """Test retrieving all mechanics."""
        with self.app.app_context():
            mech = Mechanic(name="Sarah Connor")
            db.session.add(mech)
            db.session.commit()

        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sarah Connor", str(response.data))

    def test_get_top_mechanics(self):
        """Test that the top mechanics route sorts correctly."""
        with self.app.app_context():
            customer = Customer(name="John", email="j@j.com", password="123")
            mech_1 = Mechanic(name="Lazy Mechanic")
            mech_2 = Mechanic(name="Hardworking Mechanic")

            ticket = ServiceTicket(VIN="123", customer=customer)
            ticket.mechanics.append(mech_2)

            db.session.add_all([customer, mech_1, mech_2, ticket])
            db.session.commit()

        response = self.client.get("/mechanics/top-mechanics")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data[0]["name"], "Hardworking Mechanic")
        self.assertEqual(data[1]["name"], "Lazy Mechanic")

    # --- NEGATIVE TESTS ---
    def test_update_mechanic_not_found(self):
        """Test trying to update a mechanic that does not exist."""
        payload = {"name": "Ghost Mechanic"}
        response = self.client.put("/mechanics/999", json=payload)

        self.assertEqual(response.status_code, 404)

    def test_delete_mechanic_not_found(self):
        """Test trying to delete a mechanic that does not exist."""
        response = self.client.delete("/mechanics/999")
        self.assertEqual(response.status_code, 404)
