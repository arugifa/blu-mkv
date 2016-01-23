from blu_mkv import ProgramController


class TestBaseController:
    def test_instantiate_controller_with_executable_file_path(self):
        executable_path = '/usr/bin/my_program'
        controller = ProgramController(executable_path)
        assert controller.executable_path == executable_path
