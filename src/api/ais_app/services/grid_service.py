import multiprocessing
import os

from ais_app.repository.enc_cell_repository import EncCellRepository
from ais_app.repository.grid_repository import GridRepository
from ais_app.repository.sql_connector import SqlConnector
from ais_app.services.space_data_preprocessing_service import SpaceDataPreprocessingService


class GridService:
    __grid_repository = GridRepository()

    def apply_to_grid_intervals(self, group_size, function_to_apply, num_consumers=multiprocessing.cpu_count() * 2):
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        consumers = [
            SpaceDataPreprocessingService.Consumer(tasks, results)
            for i in range(num_consumers)
        ]

        for w in consumers:
            w.start()

        for task in self.__grid_repository.get_intervals(group_size):
            tasks.put(task)

        for w in consumers:
            w.join()

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

