from abc import ABC, abstractmethod
import datetime
import json
import os
import traceback


class ProjectBoardBase(ABC):
    """
    A project board is a unit of delivery for a project. Each board will have a set of tasks assigned to a user.
    """
    @abstractmethod

    # create a board
    def create_board(self, request: str):
        """
        :param request: A json string with the board details.
        {
            "name" : "<board_name>",
            "description" : "<description>",
            "team_id" : "<team id>"
            "creation_time" : "<date:time when board was created>"
        }
        :return: A json string with the response {"id" : "<board_id>"}

        Constraint:
         * board name must be unique for a team
         * board name can be max 64 characters
         * description can be max 128 characters
        """
        pass

    # close a board
    def close_board(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<board_id>"
        }

        :return:

        Constraint:
          * Set the board status to CLOSED and record the end_time date:time
          * You can only close boards with all tasks marked as COMPLETE
        """
        pass

    # add task to board
    def add_task(self, request: str) -> str:
        """
        :param request: A json string with the task details. Task is assigned to a user_id who works on the task
        {
            "title" : "<board_name>",
            "description" : "<description>",
            "user_id" : "<team id>"
            "creation_time" : "<date:time when task was created>"
        }
        :return: A json string with the response {"id" : "<task_id>"}

        Constraint:
         * task title must be unique for a board
         * title name can be max 64 characters
         * description can be max 128 characters

        Constraints:
        * Can only add task to an OPEN board
        """
        pass

    # update the status of a task
    def update_task_status(self, request: str):
        """
        :param request: A json string with the user details
        {
            "id" : "<task_id>",
            "status" : "OPEN | IN_PROGRESS | COMPLETE"
        }
        """
        pass

    # list all open boards for a team
    def list_boards(self, request: str) -> str:
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<board_id>",
            "name" : "<board_name>"
          }
        ]
        """
        pass

    def export_board(self, request: str) -> str:
        """
        Export a board in the out folder. The output will be a txt file.
        We want you to be creative. Output a presentable view of the board and its tasks with the available data.
        :param request:
        {
          "id" : "<board_id>"
        }
        :return:
        {
          "out_file" : "<name of the file created>"
        }
        """
        pass
    
class ProjectBoardManager(ProjectBoardBase):
    def __init__(self,db_path='db/boards.json'):
        self.db_path=db_path
        if not os.path.exists(self.db_path):
            with open(self.db_path,'w') as file:
                json.dump({},file)

    def create_board(self, request: str) -> str:
        try:
            board_data = json.loads(request)
            name = board_data.get('name')
            description = board_data.get('description')
            team_id = board_data.get('team_id')

            if not name or not description or not team_id:
                raise ValueError("Name, description, and team ID are required")
            if len(name) > 64:
                raise ValueError("Name must be 64 characters or less")
            if len(description) > 128:
                raise ValueError("Description must be 128 characters or less")

            with open(self.db_path, 'r+') as file:
                boards = json.load(file)

                if any(board['name'] == name and board['team_id'] == team_id for board in boards.values()):
                    raise ValueError("Board name must be unique for the team, Board name already exists")

                board_id = str(len(boards) + 1)
                boards[board_id] = {
                    "name": name,
                    "description": description,
                    "team_id": team_id,
                    "status": "OPEN",
                    "creation_time": datetime.datetime.now().isoformat(),
                    "tasks": {}
                }
                file.seek(0)
                json.dump(boards, file, indent=4)

            return json.dumps({"id": board_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def close_board(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            board_id = request_data.get('id')

            if not board_id:
                raise ValueError("Board ID is required")

            with open(self.db_path, 'r+') as file:
                boards = json.load(file)

                if board_id not in boards:
                    raise ValueError("Board not found")

                board = boards[board_id]

                if any(task['status'] != "COMPLETE" for task in board['tasks'].values()):
                    raise ValueError("Cannot close board with incomplete tasks")

                board['status'] = "CLOSED"
                board['end_time'] = datetime.datetime.now().isoformat()

                file.seek(0)
                json.dump(boards, file, indent=4)

            return json.dumps({"id": board_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def add_task(self, request: str) -> str:
        try:
            task_data = json.loads(request)
            title = task_data.get('title')
            description = task_data.get('description')
            user_id = task_data.get('user_id')
            board_id = task_data.get('board_id')

            if not title or not description or not user_id or not board_id:
                raise ValueError("Title, description, user ID, and board ID are required")
            if len(title) > 64:
                raise ValueError("Title must be 64 characters or less")
            if len(description) > 128:
                raise ValueError("Description must be 128 characters or less")

            with open(self.db_path, 'r+') as file:
                boards = json.load(file)

                if board_id not in boards:
                    raise ValueError("Board not found")

                board = boards[board_id]

                if board['status'] != "OPEN":
                    raise ValueError("Cannot add task to a closed board")

                if any(task['title'] == title for task in board['tasks'].values()):
                    raise ValueError("Task title must be unique for the board")

                task_id = str(len(board['tasks']) + 1)
                board['tasks'][task_id] = {
                    "title": title,
                    "description": description,
                    "user_id": user_id,
                    "status": "OPEN",
                    "creation_time": datetime.datetime.now().isoformat()
                }

                file.seek(0)
                json.dump(boards, file, indent=4)

            return json.dumps({"id": task_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def update_task_status(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            task_id = request_data.get('id')
            status = request_data.get('status')

            if not task_id or not status:
                raise ValueError("Task ID and status are required")
            if status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
                raise ValueError("Invalid status value")

            with open(self.db_path, 'r+') as file:
                boards = json.load(file)

                for board in boards.values():
                    if task_id in board['tasks']:
                        board['tasks'][task_id]['status'] = status
                        file.seek(0)
                        json.dump(boards, file, indent=4)
                        return json.dumps({"id": task_id})

                raise ValueError("Task not found")

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def list_boards(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            team_id = request_data.get('id')

            if not team_id:
                raise ValueError("Team ID is required")

            with open(self.db_path, 'r') as file:
                boards = json.load(file)

            open_boards = [
                {
                    "id": board_id,
                    "name": board["name"]
                }
                for board_id, board in boards.items()
                if board["team_id"] == team_id and board["status"] == "OPEN"
            ]

            return json.dumps(open_boards)

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def export_board(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            board_id = request_data.get('id')

            if not board_id:
                raise ValueError("Board ID is required")

            with open(self.db_path, 'r') as file:
                boards = json.load(file)

            if board_id not in boards:
                raise ValueError("Board not found")

            board = boards[board_id]

            os.makedirs('out', exist_ok=True)

            out_file = f"out/board_{board_id}.txt"
            with open(out_file, 'w') as file:
                file.write(f"Board: {board['name']}\n")
                file.write(f"Description: {board['description']}\n")
                file.write(f"Status: {board['status']}\n")
                file.write("Tasks:\n")
                for task_id, task in board['tasks'].items():
                    file.write(f"- Task {task_id}: {task['title']} ({task['status']})\n")
                    file.write(f"  Description: {task['description']}\n")
                    file.write(f"  Assigned to: {task['user_id']}\n")
                    file.write(f"  Created at: {task['creation_time']}\n")

            return json.dumps({"out_file": out_file})

        except Exception as e:
            raise ValueError(traceback.format_exc())
