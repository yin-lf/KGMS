from typing import List
from ..db import get_neo4j_db, Paper
from ..const import RelationType
from .graph_service import GraphService


class RecommendationService:
    def __init__(self):
        self.db = get_neo4j_db()
        self.driver = self.db.get_driver()
        self.graph_service = GraphService()

    def close(self):
        self.db.close()

    def get_recommendations(self, username: str) -> List[Paper]:
        with self.driver.session() as session:
            papers = session.execute_read(self._get_recommendations, username)
            # Ensure we have a list of unique papers
            unique_papers = []
            seen_ids = set()
            for paper in papers:
                if paper.pid not in seen_ids:
                    unique_papers.append(paper)
                    seen_ids.add(paper.pid)
            return unique_papers

    @staticmethod
    def _get_recommendations(tx, username: str) -> List[Paper]:
        query = """
        MATCH (target_user:User {username: $username})-[:LIKES]->(liked_paper:Paper)<-[:LIKES]-(other_user:User)
        WHERE target_user <> other_user
        MATCH (other_user)-[:LIKES]->(recommended_paper:Paper)
        WHERE NOT (target_user)-[:LIKES]->(recommended_paper)
        RETURN DISTINCT recommended_paper.id AS id
        """
        result = tx.run(query, username=username)
        papers = []
        for record in result:
            paper = GraphService._find_paper_by_id(tx, record["id"])
            if paper:
                papers.append(paper)
        return papers

    def record_feedback(self, username: str, paper_id: str, liked: bool):
        with self.driver.session() as session:
            session.execute_write(self._record_feedback, username, paper_id, liked)

    @staticmethod
    def _record_feedback(tx, username: str, paper_id: str, liked: bool):
        if liked:
            query = f"""
            MATCH (u:User {{username: $username}})
            MATCH (p:Paper {{id: $paper_id}})
            MERGE (u)-[:LIKES]->(p)
            """
            tx.run(query, username=username, paper_id=paper_id)
        else:
            query = f"""
            MATCH (u:User {{username: $username}})-[r:LIKES]->(p:Paper {{id: $paper_id}})
            DELETE r
            """
            tx.run(query, username=username, paper_id=paper_id)

    def get_liked_papers(self, username: str) -> List[Paper]:
        with self.driver.session() as session:
            return session.execute_read(self._get_liked_papers, username)

    @staticmethod
    def _get_liked_papers(tx, username: str) -> List[Paper]:
        query = """
        MATCH (u:User {username: $username})-[:LIKES]->(p:Paper)
        RETURN p.id AS id
        """
        result = tx.run(query, username=username)
        papers = []
        for record in result:
            paper = GraphService._find_paper_by_id(tx, record["id"])
            if paper:
                papers.append(paper)
        return papers

