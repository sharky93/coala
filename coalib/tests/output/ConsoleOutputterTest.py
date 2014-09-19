"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
import sys
sys.path.insert(0, ".")
import builtins

from coalib.misc.i18n import _
_input = builtins.__dict__["input"]
builtins.__dict__["input"] = lambda x: x
from coalib.output.ConsoleOutputter import ConsoleOutputter


class ConsoleOutputterTestCase(unittest.TestCase):
    def setUp(self):
        self.uut = ConsoleOutputter()

    def test_require_settings(self):
        self.assertEqual(self.uut.require_settings({"setting": "help text"}),
                         {"setting":
                              _("Please enter a value for the needed setting \"{}\" ({}): ").format("setting",
                                                                                                    "help text")})


if __name__ == '__main__':
    unittest.main(verbosity=2)

builtins.__dict__["input"] = _input