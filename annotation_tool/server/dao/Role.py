from typing import List
from pydantic import BaseModel

class Role(BaseModel):
    """
    A Pydantic model for representing roles within an application.

    Attributes:
        name (str): The name of the role.
        permissions (List[str]): A list of permissions associated with the role.
    """

    name: str
    permissions: List[str]

    def __repr__(self):
        return f"Role(name='{self.name}', permissions={self.permissions})"


admin_role = Role(name="admin", permissions=["visit_admin_page", "visit_task_page", "visit_task_page_with_access_control", "set_up_access_control", "download_data", "submit_task" ,  "submit_task_with_access_control"  ])

user_role = Role(name="user", permissions=["visit_task_page", "submit_task"])

authorised_user_role = Role(name="authorised_user",
                            permissions=["visit_task_page", "visit_task_page_with_access_control", "submit_task" ,  "submit_task_with_access_control"])
