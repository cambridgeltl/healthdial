from datetime import datetime
from pydantic import BaseModel
from dao.Role import Role


class User(BaseModel):
    """
    A Pydantic model for representing users in an application.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The hased password for the user's account.
        country (str): The country of residence of the user.
        country (str): The country of residence of the user.
        age_group (str): The age group of the user.
        gender (str): The gender of the user.
        region_of_residence (str): The region where the user currently resides.
        place_of_origin (str): The place where the user originates from.
        primary_language (str): The primary language spoken by the user.
        secondary_languages (str): Other languages spoken by the user.
        education_level (str): The highest education level completed by the user.
        date_added (datetime): The date and time when the user was added to the system.
        role (Role): The role assigned to the user, with associated permissions.
    """

    username: str
    email: str
    password: str
    country: str
    age_group: str
    gender: str
    region_of_residence: str
    place_of_origin: str
    primary_language: str
    secondary_languages: str
    education_level: str
    date_added: datetime
    role: Role = None

    def __repr__(self):
        role_repr = self.role.__repr__() if self.role else "None"
        return (
            f'User(email="{self.email}", username="{self.username}", password="******", '
            f'country="{self.country}", age_group="{self.age_group}", gender="{self.gender}", '
            f'region_of_residence="{self.region_of_residence}", place_of_origin="{self.place_of_origin}", '
            f'primary_language="{self.primary_language}", secondary_languages="{self.secondary_languages}", '
            f'education_level="{self.education_level}", role={role_repr})'
        )
