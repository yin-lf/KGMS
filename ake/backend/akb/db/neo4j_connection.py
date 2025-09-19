from neo4j import GraphDatabase
from ..const import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jConnection:
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jConnection, cls).__new__(cls)
            try:
                cls._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
                # Test the connection
                with cls._driver.session() as session:
                    session.run("RETURN 1")
                print("Successfully connected to Neo4j.")
            except Exception as e:
                print(f"Failed to connect to Neo4j: {e}")
                cls._instance = None
                raise
        return cls._instance

    def get_driver(self):
        return self._driver

    def close(self):
        if self._driver is not None:
            self._driver.close()
            print("Neo4j connection closed.")
            Neo4jConnection._driver = None
            Neo4jConnection._instance = None

# Singleton instance
def get_neo4j_db():
    return Neo4jConnection()
