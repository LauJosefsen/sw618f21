import json
import multiprocessing
import os

from ais_app.repository.enc_cell_repository import EncCellRepository
from ais_app.repository.grid_repository import GridRepository
from ais_app.repository.sql_connector import SqlConnector
from ais_app.services.space_data_preprocessing_service import SpaceDataPreprocessingService


class GridService:
    __grid_repository = GridRepository()

    def apply_to_grid_intervals(self, group_size, function_to_apply, num_consumers=multiprocessing.cpu_count(), shared_info = None, grid_name = "grid"):
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        consumers = [
            GridService.Consumer(tasks, results, function_to_apply, shared_info)
            for i in range(num_consumers)
        ]

        for w in consumers:
            w.start()

        grid_groups = self.__grid_repository.get_intervals(grid_name, group_size)

        for task in grid_groups:
            tasks.put(task)
        for i in range(num_consumers):
            tasks.put(None)
        tasks.put(None)

        num_jobs = len(grid_groups)
        while num_jobs:
            result = results.get()
            print(f'Result: {result}, {num_jobs} left')
            num_jobs -= 1

        return results


    class Consumer(multiprocessing.Process):
        def __init__(self, task_queue, result_queue, function_to_apply, shared_info=None):
            multiprocessing.Process.__init__(self)
            self.results = result_queue
            self.task_queue = task_queue
            self.shared_info = shared_info
            self.function_to_apply = function_to_apply

        def run(self):
            conn = SqlConnector().get_db_connection()
            conn.set_session(autocommit=True)

            while True:
                next_task = self.task_queue.get()
                if next_task is None:
                    print("Tasks Complete")
                    self.task_queue.task_done()
                    break

                result = self.function_to_apply(next_task, self.shared_info, conn)
                self.task_queue.task_done()
                self.results.put(result)
            conn.close()
            return

