import bcrypt


def hash_password(password):
    """
        Generate a hashed password using bcrypt.

        Args:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())