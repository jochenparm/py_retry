import os
import sys

from os.path import dirname, realpath
from pathlib import Path
from shutil import rmtree

import toml


PROJECT_ROOT = dirname(realpath(__file__))

with open(Path(PROJECT_ROOT) / "pyproject.toml") as f_read:
    content = toml.load(f_read)
    __version__ = content["tool"]["poetry"]["version"]


class UploadCommand:
    @staticmethod
    def status(s):
        print(f"✨✨ {s}")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def git_commit_main(self) -> int:
        self.status("Pushing git commits...")
        os.system("git add .")
        os.system(f'git commit -m "{__version__}"')
        return os.system("git push origin main")

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(Path(PROJECT_ROOT) / "dist")
        except OSError:
            pass

        self.status("Building Source and Wheel distribution…")
        os.system("poetry build")

        self.status("Uploading the package to PyPI via poetry…")
        return_code = os.system("poetry publish -vv")

        if not return_code:
            push_to_main_code = self.git_commit_main()

            if not push_to_main_code:
                self.status("Pushing git tags…")
                os.system(
                    'git tag -a v{0} -m "release version v{0}"'.format(__version__)
                )
                os.system(f"git push origin v{__version__}")

        sys.exit()


if __name__ == "__main__":
    uc = UploadCommand()
    uc.run()
