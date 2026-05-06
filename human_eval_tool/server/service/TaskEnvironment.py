# -*- coding: utf-8 -*-
"""
Task Environment Configuration

This script is designed for setting up and managing the task environment in a dialogue evaluation experiment. It includes
functionalities for initializing the task environment with specific configurations, retrieving random tasks, and providing
relevant information about the tasks such as their language and dataset.

Author: Songbo Hu and Xiaobin Wang
Date: 20 November 2023
License: MIT License
"""

import json
import logging
import random
import os

class TaskEnvironment:

    def __init__(self, config_file_path=None):
        """
        Initializes an instance of the class.

        Parameters:
            config_file_path (str): The path to the configuration file.
        
        Returns:
            None
        """
        self.task_dic = None
        self.language = None
        self.dataset = None
        self.admin_email = None

        # Use an explicit constructor value first, then the reproducibility
        # environment variable, then the bundled demo task configuration.
        if config_file_path:
            self.config_file_path = config_file_path
        elif os.getenv("TASK_CONFIG_PATH"):
            self.config_file_path = os.getenv("TASK_CONFIG_PATH")
        else:
            current_path = os.path.abspath(os.path.dirname(__file__))
            self.config_file_path = os.path.join(current_path, "..", "config", "test_goals.json")
        
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                self.task_dic = json.load(f)
            if not self.task_dic:
                raise ValueError("Loaded configuration is empty or invalid.")
        except FileNotFoundError:
            logging.error('Configuration file not found at: {}'.format(self.config_file_path))
            raise
        except json.JSONDecodeError:
            logging.error('Failed to decode JSON from configuration file: {}'.format(self.config_file_path))
            raise
        except ValueError as e:
            logging.error('Error loading or validating configuration: {}'.format(e))
            raise

        # These labels are returned with each sampled task so downstream result
        # exports can recover which experiment configuration produced the row.
        self.language = os.getenv('TASK_LANGUAGE', 'English')
        self.dataset = os.getenv('TASK_DATASET', 'human_eval')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@localhost')
        
        logging.info('This is the {} language system which is using {} dataset.'.format(self.language, self.dataset))

    def get_task(self):
        """
        Get a random task from the task dictionary.

        Returns:
            dict: A dictionary containing the randomly selected task with the following keys:
                - "task_id" (str): The ID of the task.
                - "task" (str): The task itself.
                - "language" (str): The language of the task.
                - "dataset" (str): The dataset of the task.
        """
        if not self.task_dic:
            logging.error("Error: Task dictionary is empty.")
            return {"task_id": "", "task": "", "language": self.language, "dataset": self.dataset}

        random_key = random.choice(list(self.task_dic.keys()))
        dial_task = self.task_dic[random_key]
        
        return {
            "task_id": random_key,
            "task": dial_task,
            "language": self.language,
            "dataset": self.dataset
        }
