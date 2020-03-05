from locust import HttpLocust, TaskSet, task, seq_task, between
import secrets
import random
import time


class TaskException(Exception):
    pass

class UserBehavior(TaskSet):

    @task(1)
    def create_task_factorial(self):
        f_value = random.randrange(101)
        new_task = {"type": "factorial", "args": {"n": f"{f_value}"}}
        task_response = self.client.post('/tasks/submissions', json=new_task, name='post task for factorial')
        if task_response.status_code != 202:
           raise TaskException('task not created')
        task_id = task_response.json().get('id')
        self.check_task(task_id)

    @task(5)
    def create_task_url(self):
        new_task = {"type": "http-fetch", "args": {"url": "https://www.google.com"}}
        task_response = self.client.post('/tasks/submissions', json=new_task, name='post task for url')
        if task_response.status_code != 202:
            raise TaskException('task not created')
        task_id = task_response.json().get('id')
        self.check_task(task_id)

    def check_task(self, task_id):
        with self.client.get(f'/tasks/submissions/{task_id}', name='get task submission', catch_response=True) as status_response:
            if status_response.status_code != 200:
                raise TaskException('task status is not reachable')
            status = status_response.json().get('status')
            while status in ['QUEUED', 'RUNNING']:
                time.sleep(1)
                status_response = self.client.get(f'/tasks/submissions/{task_id}', name='get task submission again', catch_response=True)
                if status_response.status_code != 200:
                    raise TaskException('task status is not reachable')
                status = status_response.json().get('status')
                print(f'checking again after getting QUEUED or RUNNING status: now status is {status} for task_id {task_id}')
            if status == 'FAILED':
                status_response.failure(f'task status is {status}')
            else:
                status_response.success()

        with self.client.get(f'/tasks/{task_id}', catch_response=True, name='get task result') as result_response:
            if result_response.status_code != 200:
                raise TaskException('task result is not reachable')
            status = result_response.json().get('status')
            if status == 'FAILED':
                result = result_response.json().get('result')
                result_response.failure(f'task status is FAILED for task_id {task_id} with result: {result}')
            else:
                result_response.success()

class AppUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5, 5)
