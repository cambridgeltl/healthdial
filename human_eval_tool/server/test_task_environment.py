import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from service.TaskEnvironment import TaskEnvironment


class TaskEnvironmentTest(unittest.TestCase):
    def test_reads_task_config_path_from_environment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "tasks.json"
            config_path.write_text(
                json.dumps({"task-1": ["Find information about seasonal flu."]}),
                encoding="utf-8",
            )

            previous = os.environ.get("TASK_CONFIG_PATH")
            os.environ["TASK_CONFIG_PATH"] = str(config_path)
            try:
                environment = TaskEnvironment()
            finally:
                if previous is None:
                    os.environ.pop("TASK_CONFIG_PATH", None)
                else:
                    os.environ["TASK_CONFIG_PATH"] = previous

            self.assertEqual(environment.config_file_path, str(config_path))
            self.assertEqual(environment.task_dic["task-1"], ["Find information about seasonal flu."])


if __name__ == "__main__":
    unittest.main()
