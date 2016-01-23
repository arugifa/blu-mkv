from pathlib import PurePath
import subprocess


class ProgramController:
    """Base interface with an external program.

    :param str executable_path: absolute path of the program's executable file
    """
    def __init__(self, executable_file):
        """
        :param str executable_file:
            name or absolute path of the program's executable file.
            If a name is given, the related file will be searched in
            the directories listed in the environment variable ``PATH``
        """
        self.executable_path = self._get_executable_path(executable_file)

    @staticmethod
    def _get_executable_path(executable_file):
        """Return the absolute path of the program's executable file."""
        if PurePath(executable_file).is_absolute():
            executable_path = executable_file
        else:
            try:
                which_output = subprocess.check_output(
                    ['which', executable_file],
                    stderr=subprocess.PIPE,
                    universal_newlines=True)
            except subprocess.CalledProcessError as exc:
                error = exc.stderr.rstrip()
                raise FileNotFoundError(error) from exc

            executable_path = which_output.rstrip()

        return executable_path
