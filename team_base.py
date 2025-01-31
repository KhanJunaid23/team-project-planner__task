import datetime
import json
import os
import traceback
from abc import ABC, abstractmethod
from user_base import UserManager

class TeamBase(ABC):
    """
    Base interface implementation for API's to manage teams.
    For simplicity a single team manages a single project. And there is a separate team per project.
    Users can be
    """
    @abstractmethod

    # create a team
    def create_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "admin": "<id of a user>"
        }
        :return: A json string with the response {"id" : "<team_id>"}

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        pass

    # list all teams
    def list_teams(self) -> str:
        """
        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>",
            "admin": "<id of a user>"
          }
        ]
        """
        pass

    # describe team
    def describe_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>"
        }

        :return: A json string with the response

        {
          "name" : "<team_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>",
          "admin": "<id of a user>"
        }

        """
        pass

    # update team
    def update_team(self, request: str) -> str:
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "team" : {
            "name" : "<team_name>",
            "description" : "<team_description>",
            "admin": "<id of a user>"
          }
        }

        :return:

        Constraint:
            * Team name must be unique
            * Name can be max 64 characters
            * Description can be max 128 characters
        """
        pass

    # add users to team
    def add_users_to_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        pass

    # add users to team
    def remove_users_from_team(self, request: str):
        """
        :param request: A json string with the team details
        {
          "id" : "<team_id>",
          "users" : ["user_id 1", "user_id2"]
        }

        :return:

        Constraint:
        * Cap the max users that can be added to 50
        """
        pass

    # list users of a team
    def list_team_users(self, request: str):
        """
        :param request: A json string with the team identifier
        {
          "id" : "<team_id>"
        }

        :return:
        [
          {
            "id" : "<user_id>",
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        ]
        """
        pass
    
class TeamManager(TeamBase):
    def __init__(self,db_path: str = 'db/teams.json'):
        self.db_path=db_path
        if not os.path.exists(self.db_path):
            with open(self.db_path,'w') as file:
                json.dump({},file)

    def create_team(self, request: str) -> str:
        try:
            team_data = json.loads(request)
            name = team_data.get('name')
            description = team_data.get('description')
            admin = team_data.get('admin')

            if not name or not description or not admin:
                raise ValueError("Name, description, and admin are required")
            if len(name) > 64:
                raise ValueError("Name must be 64 characters or less")
            if len(description) > 128:
                raise ValueError("Description must be 128 characters or less")

            with open(self.db_path, 'r+') as file:
                teams = json.load(file)
                if any(team['name'] == name for team in teams.values()):
                    raise ValueError("Team name must be unique")

                team_id = str(len(teams) + 1)
                teams[team_id] = {
                    "name": name,
                    "description": description,
                    "admin": admin,
                    "creation_time": datetime.datetime.now().isoformat(),
                    "users": []
                }
                file.seek(0)
                json.dump(teams, file, indent=4)

            return json.dumps({"id": team_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def list_teams(self) -> str:
        try:
            with open(self.db_path, 'r') as file:
                teams = json.load(file)

            team_list = [
                {
                    "name": team["name"],
                    "description": team["description"],
                    "creation_time": team["creation_time"],
                    "admin": team["admin"]
                }
                for team in teams.values()
            ]

            return json.dumps(team_list)

        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def describe_team(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            team_id = request_data.get('id')

            if not team_id:
                raise ValueError("Team ID is required")

            with open(self.db_path, 'r') as file:
                teams = json.load(file)

            if team_id not in teams:
                raise ValueError("Team not found")

            team = teams[team_id]
            return json.dumps({
                "name": team["name"],
                "description": team["description"],
                "creation_time": team["creation_time"],
                "admin": team["admin"]
            })

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def update_team(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            team_id = request_data.get('id')
            team_updates = request_data.get('team', {})

            if not team_id:
                raise ValueError("Team ID is required")
            if "name" in team_updates and len(team_updates["name"]) > 64:
                raise ValueError("Name must be 64 characters or less")
            if "description" in team_updates and len(team_updates["description"]) > 128:
                raise ValueError("Description must be 128 characters or less")

            with open(self.db_path, 'r+') as file:
                teams = json.load(file)

                if team_id not in teams:
                    raise ValueError("Team not found")

                if "name" in team_updates:
                    new_name = team_updates["name"]
                    if any(team['name'] == new_name for team in teams.values() if team != teams[team_id]):
                        raise ValueError("Team name must be unique")

                teams[team_id].update(team_updates)
                file.seek(0)
                json.dump(teams, file, indent=4)

            return json.dumps({"id": team_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def add_users_to_team(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            team_id = request_data.get('id')
            users = request_data.get('users', [])

            if not team_id:
                raise ValueError("Team ID is required")
            if len(users) > 50:
                raise ValueError("Cannot add more than 50 users to a team")

            with open(self.db_path, 'r+') as file:
                teams = json.load(file)

                if team_id not in teams:
                    raise ValueError("Team not found")

                teams[team_id]["users"] = list(set(teams[team_id]["users"] + users))
                file.seek(0)
                json.dump(teams, file, indent=4)

            return json.dumps({"id": team_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def remove_users_from_team(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            team_id = request_data.get('id')
            users = request_data.get('users', [])

            if not team_id:
                raise ValueError("Team ID is required")

            with open(self.db_path, 'r+') as file:
                teams = json.load(file)

                if team_id not in teams:
                    raise ValueError("Team not found")

                teams[team_id]["users"] = [user for user in teams[team_id]["users"] if user not in users]
                file.seek(0)
                json.dump(teams, file, indent=4)

            return json.dumps({"id": team_id})

        except Exception as e:
            raise ValueError(traceback.format_exc())

    def list_team_users(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            team_id = request_data.get('id')

            if not team_id:
                raise ValueError("Team ID is required")

            with open(self.db_path, 'r') as file:
                teams = json.load(file)

            if team_id not in teams:
                raise ValueError("Team not found")

            team_users = []
            for user_id in teams[team_id]["users"]:
                user_details = json.loads(UserManager.describe_user(json.dumps({"id":user_id})))
                team_users.append({
                    "id": user_id,
                    "name": user_details["name"],
                    "display_name": user_details["display_name"]
                })

            return json.dumps(team_users)

        except Exception as e:
            raise ValueError(traceback.format_exc())

