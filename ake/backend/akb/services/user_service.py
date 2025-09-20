from typing import Optional
from ..db import get_neo4j_db, User
import bcrypt


class UserService:
    def __init__(self):
        self.db = get_neo4j_db()
        self.driver = self.db.get_driver()

    def close(self):
        self.db.close()

    def create_user(self, username: str, password: str) -> Optional[User]:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        with self.driver.session() as session:
            result = session.execute_write(
                self._create_user, username, password_hash.decode("utf-8")
            )
            if result:
                return User.make_meta(username=username, password_hash=result)
        return None

    @staticmethod
    def _create_user(tx, username: str, password_hash: str) -> Optional[str]:
        query = """
        CREATE (u:User {username: $username, password_hash: $password_hash})
        RETURN u.password_hash
        """
        result = tx.run(query, username=username, password_hash=password_hash)
        record = result.single()
        return record[0] if record else None

    def find_user(self, username: str) -> Optional[User]:
        with self.driver.session() as session:
            return session.execute_read(self._find_user, username)

    @staticmethod
    def _find_user(tx, username: str) -> Optional[User]:
        query = "MATCH (u:User {username: $username}) RETURN u.username, u.password_hash"
        result = tx.run(query, username=username)
        record = result.single()
        if record:
            return User.make_meta(
                username=record["u.username"], password_hash=record["u.password_hash"]
            )
        return None

    def verify_user(self, username: str, password: str) -> bool:
        user = self.find_user(username)
        if user:
            return bcrypt.checkpw(
                password.encode("utf-8"), user.password_hash.encode("utf-8")
            )
        return False
