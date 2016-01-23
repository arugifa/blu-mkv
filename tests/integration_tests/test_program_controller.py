import re

import pytest

from blu_mkv import ProgramController


class TestBaseController:
    def test_instantiate_controller_with_executable_file_name(self):
        controller = ProgramController('which')
        assert controller.executable_path == '/usr/bin/which'

    def test_instantiate_controller_with_wrong_executable_file_name(self):
        executable_name = 'imaginary_program'

        with pytest.raises(FileNotFoundError) as exc_info:
            ProgramController(executable_name)

        assert re.search(
            r'no imaginary_program in \(.+\)', str(exc_info.value))
