import json
import unittest

from app import create_app
from app.extensions import db
from app.models import Customer


class TestCustomers(unittest.TestCase):
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
    def test_create_customer_success(self):
        """Test that we can successfully create a customer."""
        payload = {
            "name": "Alice Wonderland",
            "email": "alice@example.com",
            "password": "securepassword",
        }
        response = self.client.post("/customers/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Alice", str(response.data))

    def test_login_success(self):
        """Test that a valid user can log in and receive a token."""
        with self.app.app_context():
            user = Customer(name="Bob", email="bob@test.com", password="password123")
            db.session.add(user)
            db.session.commit()

        login_payload = {"email": "bob@test.com", "password": "password123"}
        response = self.client.post("/customers/login", json=login_payload)

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn("token", data)

    # --- NEGATIVE TESTS ---
    def test_login_wrong_password(self):
        """Test that logging in with a bad password fails."""
        with self.app.app_context():
            user = Customer(
                name="Charlie", email="charlie@test.com", password="realpassword"
            )
            db.session.add(user)
            db.session.commit()

        bad_login = {"email": "charlie@test.com", "password": "WRONGPASSWORD"}
        response = self.client.post("/customers/login", json=bad_login)

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid email or password", str(response.data))

    def test_access_protected_route_without_token(self):
        """Test that accessing /my-tickets without a token gets blocked."""
        response = self.client.get("/customers/my-tickets")

        self.assertEqual(response.status_code, 401)
        self.assertIn("Token is missing", str(response.data))


if __name__ == "__main__":
    unittest.main()
