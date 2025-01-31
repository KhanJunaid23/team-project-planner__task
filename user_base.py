import json
import os
import traceback
import datetime
from abc import ABC,abstractmethod
class UserBase(ABC):
    """
    Base interface implementation for API's to manage users.
    """
    @abstractmethod

    # create a user
    def create_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "name" : "<user_name>",
          "display_name" : "<display name>"
        }
        :return: A json string with the response {"id" : "<user_id>"}

        Constraint:
            * user name must be unique
            * name can be max 64 characters
            * display name can be max 64 characters
        """
        pass

    # list all users
    def list_users(self) -> str:
        """
        :return: A json list with the response
        [
          {
            "name" : "<user_name>",
            "display_name" : "<display name>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        pass

    # describe user
    def describe_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>"
        }

        :return: A json string with the response

        {
          "name" : "<user_name>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>"
        }

        """
        pass

    # update user
    def update_user(self, request: str) -> str:
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>",
          "user" : {
            "name" : "<user_name>",
            "display_name" : "<display name>"
          }
        }

        :return:

        Constraint:
            * user name cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
        """
        pass

    def get_user_teams(self, request: str) -> str:
        """
        :param request:
        {
          "id" : "<user_id>"
        }

        :return: A json list with the response.
        [
          {
            "name" : "<team_name>",
            "description" : "<some description>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        pass


class UserManager(UserBase):
    def __init__(self,db_path='db/users.json'):
        self.db_path=db_path
        if not os.path.exists(self.db_path):
            with open(self.db_path,'w') as file:
                json.dump({},file)

    def create_user(self, request:str) -> str:
        try:
            user_data=json.loads(request)
            name=user_data.get('name')
            display_name = user_data.get('display_name')

            if not name or not display_name:
                raise ValueError("Name and display name are required")
            if len(name) > 64 or len(display_name) > 64:
                raise ValueError("Name and display name must be 64 characters or less")

            
            with open(self.db_path,'+r') as file:
                users=json.load(file)
                if any(user['name'] == name for user in users.values()):
                    raise ValueError("User name must be unique")
                user_id=str(len(users)+1)
                users[user_id] = {
                    "name": name,
                    "display_name": display_name,
                    "creation_time": datetime.datetime.now().isoformat()
                }
                file.seek(0)
                json.dump(users,file)
            return json.dumps({"status": "success", "user_id": user_id})
        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def list_users(self) -> str:
        try:
            with open(self.db_path,'r') as file:
                users = json.load(file)
            users_list=[
                {
                    "id":user['id'],
                    "name":user['name'],
                    "display_name": user["display_name"],
                    "creation_time":user['creation_time']
                }
                for user in users.values()
            ]
            return json.dumps({"status": "success", "users_list": users_list})

        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def describe_user(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            user_id = request_data.get('id')
            if not user_id:
                raise ValueError("User ID is required")
            with open(self.db_path, 'r') as f:
                users = json.load(f)
            if user_id not in users:
                raise ValueError("User not found")
            user = users[user_id]
            user_data = {
                "id":user['id'],
                "name":user['name'],
                "display_name": user["display_name"],
                "creation_time":user['creation_time']
            }
            return json.dumps({"status": "success", "user_data": user_data})
        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def update_user(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            user_id = request_data.get('id')
            user_details = request_data.get('user', {})

            if not user_id:
                raise ValueError("User ID is required")
            if "name" in user_details and len(user_details["name"]) > 64:
                raise ValueError("Name must be 64 characters or less")
            if "display_name" in user_details and len(user_details["display_name"]) > 128:
                raise ValueError("Display name must be 128 characters or less")

            with open(self.db_path, 'r+') as file:
                users = json.load(file)

                if user_id not in users:
                    raise ValueError("User not found")

                users[user_id].update(user_details)
                file.seek(0)
                json.dump(users, file, indent=4)

            return json.dumps({"status": "success", "user_data": {"id": user_id}})

        except Exception as e:
            raise ValueError(traceback.format_exc())
        
    def get_user_teams(self, request: str) -> str:
        try:
            request_data = json.loads(request)
            user_id = request_data.get('id')

            if not user_id:
                raise ValueError("User ID is required")

            teams_db_path = 'db/teams.json'
            if not os.path.exists(teams_db_path):
                raise ValueError("Teams database not found")

            with open(teams_db_path, 'r') as file:
                teams = json.load(file)

            user_teams = []
            for team_id, team in teams.items():
                if user_id in team.get("users", []):
                    user_teams.append({
                        "name": team["name"],
                        "description": team["description"],
                        "creation_time": team["creation_time"]
                    })

            return json.dumps(user_teams)

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")
        except Exception as e:
            raise ValueError(f"Error getting user teams: {str(e)}")
        
