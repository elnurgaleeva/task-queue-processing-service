from locust import HttpLocust, TaskSet, task, between
import secrets
import time

class AppBehavior(TaskSet):
    created_tasks = []
    completed_tasks = []

    @task(1)
    def create_task_factorial(self):
        new_task = {"type": "factorial", "args": { "n": "50" }}
        task_response = self.client.post('/tasks/submissions', json=new_task, name='post task for factorial')
        if task_response.status_code != 202:
            return
        task_id = task_response.json().get('id')
        self.created_tasks.append(task_id)

    @task(3)
    def create_task_url(self):
        new_task = {"type": "http-fetch", "args": { "url": "https://www.example.com/"}}
        task_response = self.client.post('/tasks/submissions', json=new_task, name='post task for url')
        if task_response.status_code != 202:
            return
        task_id = task_response.json().get('id')
        self.created_tasks.append(task_id)

    @task(12)
    def get_task_submission(self):
        if len(self.created_tasks) == 0:
            return
        task_id = self.created_tasks.pop(secrets.randbelow(len(self.created_tasks)))
        with self.client.get(f'/tasks/submissions/{task_id}', name='get task submission', catch_response=True) as task_response:
            status = task_response.json().get('status')
            while status in ['QUEUED', 'RUNNING']:
                time.sleep(1)
                task_response = self.client.get(f'/tasks/submissions/{task_id}', name='get task submission again', catch_response=True)
                status = task_response.json().get('status')
                print(f'checking again after getting QUEUED or RUNNING status: now status is {status} for task_id {task_id}')
            if status == 'FAILED' or task_response.status_code != 200:
                task_response.failure(f'task status is {status}')
            else:
                task_response.success()
        self.completed_tasks.append(task_id)

    @task(4)
    def get_task_result(self):
        if len(self.completed_tasks) == 0:
            return
        task_id = self.completed_tasks.pop(secrets.randbelow(len(self.completed_tasks)))
        with self.client.get(f'/tasks/{task_id}', catch_response=True, name='get task result') as task_response:
            if task_response.status_code == 200:
                status = task_response.json().get('status')
                if status == 'FAILED':
                    result = task_response.json().get('result')
                    task_response.failure(f'task status is FAILED for task_id {task_id} with result: {result}')
                else:
                    task_response.success()
            else:
                task_response.failure(f'status code is {task_response.status_code} for task_id {task_id}')


class AppUser(HttpLocust):
    task_set = AppBehavior
    wait_time = between(1, 5)