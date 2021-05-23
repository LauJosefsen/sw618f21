import multiprocessing

from ais_app.repository.sql_connector import SqlConnector


class AbstractConsumerWithDb(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, action):
        multiprocessing.Process.__init__(self)
        self.result_queue = result_queue
        self.task_queue = task_queue
        self.action = action

    def run(self):
        conn = SqlConnector().get_db_connection()
        conn.set_session(autocommit=True)

        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                print("Tasks Complete")
                self.task_queue.task_done()
                break

            result = self.action(next_task, conn)
            self.task_queue.task_done()
            self.result_queue.put(result)
        conn.close()