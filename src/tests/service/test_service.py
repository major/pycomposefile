import unittest
from tests.compose_generator import ComposeGenerator


class TestComposeServices(unittest.TestCase):
    compose_with_no_services = """
version: 3.9
volumes:
  db-data:
    driver: flocker
    driver_opts:
      size: "10GiB"
"""

    compose_with_one_service = """
services:
  frontend:
    image: awesome/webapp
"""

    compose_with_one_service_complex = """
services:
  frontend:
    image: awesome/webapp
    container_name: myfrontend
    cpu_count: 1.5
"""

    compose_with_two_services = """
services:
  frontend:
    image: awesome/webapp
  backend:
    image: awesome/backend
"""

    def test_empty_services_throws_error(self):
        with self.assertRaises(KeyError):
            ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_no_services)

    def test_name_matches_with_one_service(self):
        compose_file = ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_one_service)
        self.assertIsNotNone(compose_file.services["frontend"])

    def test_compose_path_matches_name_with_one_service(self):
        compose_file = ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_one_service)
        self.assertEqual(compose_file.services["frontend"].compose_path, 'services/frontend')

    def test_names_match_with_two_services(self):
        compose_file = ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_two_services)
        self.assertEqual(list(compose_file.services.keys()), ["frontend", "backend"])

    def test_compose_paths_matches_name_with_two_services(self):
        compose_file = ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_two_services)
        self.assertEqual(compose_file.services["frontend"].compose_path, 'services/frontend')
        self.assertEqual(compose_file.services["backend"].compose_path, 'services/backend')

    def test_container_name_assigned_from_service(self):
        compose_file = ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_one_service_complex)
        self.assertEqual(compose_file.services["frontend"].container_name, "myfrontend")

    def test_cpu_count_assigned_from_service(self):
        compose_file = ComposeGenerator.convert_yaml_to_compose_file(self.compose_with_one_service_complex)
        self.assertEqual(compose_file.services["frontend"].cpu_count, 1.5)

    def test_expose_from_service(self):
        compose_file = ComposeGenerator.get_compose_with_one_service_with_deploy()
        self.assertIs(type(compose_file.services["frontend"].expose[0]), int)
        self.assertIn(3000, compose_file.services["frontend"].expose)

    def test_multiple_expose_from_service(self):
        compose_file = ComposeGenerator.get_compose_with_one_service_with_multiple_expose()
        self.assertEqual(compose_file.services["frontend"].expose, [3000, 4000, 5000])

    def test_command_string_from_service(self):
        compose_file = ComposeGenerator.get_compose_with_one_service_with_deploy()
        self.assertEqual(compose_file.services["frontend"].command.__str__(), "bundle exec thin -p 3000")

    def test_command_list_from_service(self):
        compose_file = ComposeGenerator.get_compose_with_command_list()
        self.assertEqual("bundle exec thin -p 3000", compose_file.services["frontend"].command.__str__())
    
    def test_command_list_with_quotes_from_service(self):
        compose_file = ComposeGenerator.get_compose_with_command_list_with_quotes()
        self.assertEqual('echo "hello world"', compose_file.services["frontend"].command.__str__())


if __name__ == '__main__':
    unittest.main()
