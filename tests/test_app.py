from io import BytesIO
from pathlib import Path
import unittest

import pandas as pd
from werkzeug.security import check_password_hash

from app import create_app
from app.config import env_bool, env_int
from app.models import User
from app.services import create_password_hash, process_import


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "WTF_CSRF_ENABLED": False,
                "SECRET_KEY": "test-key-not-for-production-1234",
                "INITIAL_USER_PASSWORD": "secure-test-password",
            }
        )
        self.client = self.app.test_client()

    def test_public_pages_render_without_database(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/login").status_code, 200)
        self.assertEqual(self.client.get("/about").status_code, 200)

    def test_legacy_endpoint_names_are_registered(self):
        endpoints = {rule.endpoint for rule in self.app.url_map.iter_rules()}
        self.assertTrue(
            {"index", "login", "dashboard", "view_students", "view_results"}
            .issubset(endpoints)
        )

    def test_notice_deletion_requires_post(self):
        delete_rule = next(
            rule
            for rule in self.app.url_map.iter_rules()
            if rule.endpoint == "delete_notice"
        )
        self.assertIn("POST", delete_rule.methods)
        self.assertNotIn("GET", delete_rule.methods)

    def test_login_required_pages_redirect_to_login(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_missing_page_returns_custom_404(self):
        self.assertEqual(self.client.get("/missing-page").status_code, 404)

    def test_user_session_identifiers_include_role(self):
        student = User("same-id", "Student", "student")
        teacher = User("same-id", "Teacher", "teacher")
        self.assertEqual(student.get_id(), "student:same-id")
        self.assertEqual(teacher.get_id(), "teacher:same-id")
        self.assertNotEqual(student.get_id(), teacher.get_id())

    def test_password_hash_uses_configured_initial_password(self):
        with self.app.app_context():
            password_hash = create_password_hash()
        self.assertTrue(
            check_password_hash(password_hash, "secure-test-password")
        )

    def test_environment_value_parsers_reject_invalid_settings(self):
        from unittest.mock import patch

        with patch.dict("os.environ", {"TEST_BOOL": "maybe"}):
            with self.assertRaisesRegex(ValueError, "TEST_BOOL"):
                env_bool("TEST_BOOL", False)
        with patch.dict("os.environ", {"TEST_INT": "not-a-number"}):
            with self.assertRaisesRegex(ValueError, "TEST_INT"):
                env_int("TEST_INT", 10, 1)

    def test_import_rejects_unknown_type_and_reports_missing_columns(self):
        with self.assertRaises(ValueError):
            process_import(BytesIO(), "unknown")

        workbook = BytesIO()
        pd.DataFrame({"course_id": ["CS"]}).to_excel(workbook, index=False)
        workbook.seek(0)
        count, errors = process_import(workbook, "course")

        self.assertEqual(count, 0)
        self.assertIn("course_name", errors[0])

    def test_custom_stylesheet_has_no_uncompiled_tailwind_directives(self):
        stylesheet = Path(__file__).parents[1] / "app" / "static" / "css" / "style.css"
        self.assertNotIn("@apply", stylesheet.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
