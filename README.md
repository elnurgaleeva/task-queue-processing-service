# task-queue-processing-service

This repository contains test script for Locust to generate load for task queue processing service.
Locust doc: https://docs.locust.io/en/stable/index.html
Test script is here: task_queue_processing_locust_file.py

Steps to run test:
1. Make sure Python 3 is installed (python3 -V). Locust is supported on Python 3.6, 3.7 and 3.8. 

2. Install Locust: pip3 install locustio. Current stable Locust version is 0.14.5.

3. Test can be run in distributed mode using master and slaves (one slave per each processor core).
Command to run test:

locust -f task_queue_processing_locust_file.py --logfile log --step-load --master&
locust -f task_queue_processing_locust_file.py --logfile log --slave& (this line should be repeated per each processor core)

--logfile - optional parameter if log should go to specified file. If not set, log will go to stdout/stderr.

--step-load - optional parameter if stepping load profile is selected. Allows to monitor service performance with different user load and probe the max RPS that can be achieved.

4. Once test has started, open Web UI on http://localhost:8089 (if you are running Locust locally).

5. Enter values into start form and press the button 'Start swarming'.