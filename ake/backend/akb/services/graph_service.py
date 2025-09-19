import re
from typing import Optional, List, Dict
from ..const import RelationType
from ..db import get_neo4j_db, Author, Paper, Category, OverviewInfo


class GraphService:
    def __init__(self):
        self.db = get_neo4j_db()
        self.driver = self.db.get_driver()
        self.fulltext_index_name = "paper_fulltext_index"
        self.fulltext_index_exists = self.check_fulltext_index_exists()

    def close(self):
        self.db.close()

    def add_author(self, name: str):
        with self.driver.session() as session:
            return session.execute_write(self._create_author, name)

    @staticmethod
    def _create_author(tx, name: str):
        result = tx.run(
            "CREATE (a:Author {name: $name}) RETURN elementId(a)", name=name
        )
        return result.single()[0]

    # def add_paper(self, paper_id: str, title: str, abstract: Optional[str] = None):
    #     with self.driver.session() as session:
    #         return session.execute_write(self._create_paper, paper_id, title, abstract)
    # 支持前端传入五个参数{ id, title, abstract, authors, categories }
    def add_paper(
        self,
        paper_id: str,
        title: str,
        abstract: Optional[str] = None,
        authors: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
    ):
        with self.driver.session() as session:
            # 创建论文节点
            session.execute_write(self._create_paper, paper_id, title, abstract)

            # 创建作者节点并关联
            if authors:
                for author in authors:
                    self.add_author(author)
                    self.link_author_to_paper(author, paper_id)

            # 创建分类节点并关联
            if categories:
                for category in categories:
                    self.add_category(category)
                    self.link_paper_to_category(paper_id, category)


    @staticmethod
    def _create_paper(tx, paper_id: str, title: str, abstract: Optional[str] = None):
        if abstract is None:
            abstract = ""
        query = """
        CREATE (p:Paper {id: $paper_id, title: $title, abstract: $abstract})
        RETURN elementId(p)
        """
        result = tx.run(query, paper_id=paper_id, title=title, abstract=abstract)
        return result.single()[0]

    def add_category(self, name: str):
        with self.driver.session() as session:
            return session.execute_write(self._create_category, name)

    @staticmethod
    def _create_category(tx, name: str):
        result = tx.run(
            "CREATE (c:Category {name: $name}) RETURN elementId(c)", name=name
        )
        return result.single()[0]

    def link_author_to_paper(self, author_name: str, paper_id: str):
        with self.driver.session() as session:
            session.execute_write(self._create_author_paper_link, author_name, paper_id)

    @staticmethod
    def _create_author_paper_link(tx, author_name: str, paper_id: str):
        tx.run(
            f"""
        MATCH (a:Author {{name: $author_name}})
        MATCH (p:Paper {{id: $paper_id}})
        MERGE (a)-[:{RelationType.HAS_PAPER.name}]->(p)
        MERGE (p)-[:{RelationType.AUTHORED_BY.name}]->(a)
        """,
            author_name=author_name,
            paper_id=paper_id,
        )

    def link_paper_to_category(self, paper_id: str, category_name: str):
        with self.driver.session() as session:
            session.execute_write(
                self._create_paper_category_link, paper_id, category_name
            )

    @staticmethod
    def _create_paper_category_link(tx, paper_id: str, category_name: str):
        tx.run(
            f"""
        MATCH (p:Paper {{id: $paper_id}})
        MATCH (c:Category {{name: $category_name}})
        MERGE (p)-[:{RelationType.BELONGS_TO.name}]->(c)
        MERGE (c)-[:{RelationType.CONTAINS.name}]->(p)
        """,
            paper_id=paper_id,
            category_name=category_name,
        )

    def unlink_author_from_paper(self, author_name: str, paper_id: str):
        with self.driver.session() as session:
            session.execute_write(self._delete_author_paper_link, author_name, paper_id)

    @staticmethod
    def _delete_author_paper_link(tx, author_name: str, paper_id: str):
        tx.run(
            f"""
        MATCH (a:Author {{name: $author_name}})-[r1:{RelationType.HAS_PAPER.name}]->(p:Paper {{id: $paper_id}})
        MATCH (p)-[r2:{RelationType.AUTHORED_BY.name}]->(a)
        DELETE r1, r2
        """,
            author_name=author_name,
            paper_id=paper_id,
        )

    def unlink_paper_from_category(self, paper_id: str, category_name: str):
        with self.driver.session() as session:
            session.execute_write(
                self._delete_paper_category_link, paper_id, category_name
            )

    @staticmethod
    def _delete_paper_category_link(tx, paper_id: str, category_name: str):
        tx.run(
            f"""
        MATCH (p:Paper {{id: $paper_id}})-[r1:{RelationType.BELONGS_TO.name}]->(c:Category {{name: $category_name}})
        MATCH (c)-[r2:{RelationType.CONTAINS.name}]->(p)
        DELETE r1, r2
        """,
            paper_id=paper_id,
            category_name=category_name,
        )

    def find_author_info(self, name: str) -> Optional[Author]:
        with self.driver.session() as session:
            return session.execute_read(self._find_author_info, name)

    @staticmethod
    def _find_author_info(tx, name: str) -> Optional[Author]:
        query = f"""
        MATCH (a:Author {{name: $name}})
        OPTIONAL MATCH (a)-[:{RelationType.HAS_PAPER.name}]->(p:Paper)
        RETURN a.name as name, COLLECT(p.id) as pids, COLLECT(p.title) as paper_titles
        """
        result = tx.run(query, name=name)
        record = result.single()
        if record and record["name"]:
            return Author.make_meta(
                name=record["name"],
                papers=[
                    (pid, title)
                    for pid, title in zip(record["pids"], record["paper_titles"])
                    if pid is not None and title is not None
                ],
            )
        return None

    def find_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        with self.driver.session() as session:
            return session.execute_read(self._find_paper_by_id, paper_id)

    @staticmethod
    def _find_paper_by_id(tx, paper_id: str) -> Optional[Paper]:
        query = f"""
        MATCH (p:Paper {{id: $paper_id}})
        OPTIONAL MATCH (p)-[:{RelationType.AUTHORED_BY.name}]->(a:Author)
        WITH p, COLLECT(DISTINCT a.name) AS authors
        OPTIONAL MATCH (p)-[:{RelationType.BELONGS_TO.name}]->(c:Category)
        WITH p, authors, COLLECT(DISTINCT c.name) AS categories
        RETURN p.id AS pid, p.title AS title, p.abstract AS abstract, authors, categories
        """
        result = tx.run(query, paper_id=paper_id)
        record = result.single()
        if record and record["pid"]:
            # Filter out null authors/categories if none are linked
            authors = [author for author in record["authors"] if author is not None]
            categories = [
                category for category in record["categories"] if category is not None
            ]
            return Paper.make_meta(
                pid=record["pid"],
                title=record["title"],
                abstract=record["abstract"],
                authors=authors,
                categories=categories,
            )
        return None

    def find_category(self, name: str) -> Optional[Category]:
        with self.driver.session() as session:
            return session.execute_read(self._find_category, name)

    @staticmethod
    def _find_category(tx, name: str) -> Optional[Category]:
        query = f"""
        MATCH (c:Category {{name: $name}})
        OPTIONAL MATCH (c)-[:{RelationType.CONTAINS.name}]->(p:Paper)
        RETURN c.name as name, COLLECT(p.id) as pids, COLLECT(p.title) as paper_titles
        """
        result = tx.run(query, name=name)
        record = result.single()
        if record and record["name"]:
            return Category.make_meta(
                name=record["name"],
                papers=[
                    (pid, title)
                    for pid, title in zip(record["pids"], record["paper_titles"])
                    if pid is not None and title is not None
                ],
            )
        return None

    def update_author(self, old_name: str, new_name: str):
        with self.driver.session() as session:
            session.execute_write(self._update_author, old_name, new_name)

    @staticmethod
    def _update_author(tx, old_name: str, new_name: str):
        tx.run(
            "MATCH (a:Author {name: $old_name}) SET a.name = $new_name",
            old_name=old_name,
            new_name=new_name,
        )

    def update_paper(
        self,
        paper_id: str,
        new_title: Optional[str] = None,
        new_abstract: Optional[str] = None,
    ):
        with self.driver.session() as session:
            session.execute_write(self._update_paper, paper_id, new_title, new_abstract)

    @staticmethod
    def _update_paper(
        tx,
        paper_id: str,
        new_title: Optional[str] = None,
        new_abstract: Optional[str] = None,
    ):
        assert (
            new_title is not None or new_abstract is not None
        ), "At least one of new_title or new_abstract must be provided"
        if new_title is None:
            tx.run(
                "MATCH (p:Paper {id: $paper_id}) SET p.abstract = $new_abstract",
                paper_id=paper_id,
                new_abstract=new_abstract,
            )
        elif new_abstract is None:
            tx.run(
                "MATCH (p:Paper {id: $paper_id}) SET p.title = $new_title",
                paper_id=paper_id,
                new_title=new_title,
            )
        else:
            tx.run(
                "MATCH (p:Paper {id: $paper_id}) SET p.title = $new_title, p.abstract = $new_abstract",
                paper_id=paper_id,
                new_title=new_title,
                new_abstract=new_abstract,
            )

    def update_category(self, old_name: str, new_name: str):
        with self.driver.session() as session:
            session.execute_write(self._update_category, old_name, new_name)

    @staticmethod
    def _update_category(tx, old_name: str, new_name: str):
        tx.run(
            "MATCH (c:Category {name: $old_name}) SET c.name = $new_name",
            old_name=old_name,
            new_name=new_name,
        )

    def delete_author(self, name: str):
        with self.driver.session() as session:
            session.execute_write(self._delete_author, name)

    @staticmethod
    def _delete_author(tx, name: str):
        tx.run("MATCH (a:Author {name: $name}) DETACH DELETE a", name=name)

    def delete_paper(self, paper_id: str):
        with self.driver.session() as session:
            session.execute_write(self._delete_paper, paper_id)

    @staticmethod
    def _delete_paper(tx, paper_id: str):
        tx.run("MATCH (p:Paper {id: $paper_id}) DETACH DELETE p", paper_id=paper_id)

    def delete_category(self, name: str):
        with self.driver.session() as session:
            session.execute_write(self._delete_category, name)

    @staticmethod
    def _delete_category(tx, name: str):
        tx.run("MATCH (c:Category {name: $name}) DETACH DELETE c", name=name)

    def clear_all_data(self):
        with self.driver.session() as session:
            session.execute_write(self._clear_all_data)

    @staticmethod
    def _clear_all_data(tx):
        tx.run("MATCH (n) DETACH DELETE n")

    def search_papers(self, query_string: str) -> List[Paper]:
        with self.driver.session() as session:
            return session.execute_read(self._search_papers, query_string)

    @staticmethod
    def _search_papers(tx, query_string: str) -> List[Paper]:
        query = f"""
        CALL db.index.fulltext.queryNodes("paper_fulltext_index", $query_string) YIELD node, score
        MATCH (p:Paper) WHERE elementId(p) = elementId(node)
        OPTIONAL MATCH (p)-[:{RelationType.AUTHORED_BY.name}]->(a:Author)
        OPTIONAL MATCH (p)-[:{RelationType.BELONGS_TO.name}]->(c:Category)
        RETURN p.id as pid, p.title as title, p.abstract as abstract,
               COLLECT(DISTINCT a.name) as authors, COLLECT(DISTINCT c.name) as categories,
               score
        ORDER BY score DESC
        """
        result = tx.run(query, query_string=query_string)
        papers = []
        for record in result:
            if record and record["pid"]:
                authors = [author for author in record["authors"] if author is not None]
                categories = [
                    category
                    for category in record["categories"]
                    if category is not None
                ]
                papers.append(
                    Paper.make_meta(
                        pid=record["pid"],
                        title=record["title"],
                        abstract=record["abstract"],
                        authors=authors,
                        categories=categories,
                    )
                )
        return papers

    def check_fulltext_index_exists(self) -> bool:
        with self.driver.session() as session:
            result = session.execute_read(self._check_fulltext_index_exists, self)
            return result

    @staticmethod
    def _check_fulltext_index_exists(tx, gs: "GraphService") -> bool:
        result = tx.run(
            f"SHOW INDEXES YIELD name WHERE name = '{gs.fulltext_index_name}'"
        )
        return result.single() is not None

    def create_fulltext_index(self):
        if self.fulltext_index_exists:
            return
        with self.driver.session() as session:
            session.execute_write(self._create_fulltext_index, self)

    @staticmethod
    def _create_fulltext_index(tx, gs: "GraphService"):
        query = f"""
        CREATE FULLTEXT INDEX {gs.fulltext_index_name} FOR (p:Paper) ON EACH [p.title, p.abstract]
        """
        try:
            tx.run(query)
            gs.fulltext_index_exists = True
        except Exception as e:
            print(f"\033[31mERROR: Failed to create full-text index: {e}\033[0m")

    def drop_fulltext_index(self):
        if not self.fulltext_index_exists:
            return
        with self.driver.session() as session:
            session.execute_write(self._drop_fulltext_index, self)

    @staticmethod
    def _drop_fulltext_index(tx, gs: "GraphService"):
        query = f"""
        DROP INDEX {gs.fulltext_index_name}
        """
        try:
            tx.run(query)
            gs.fulltext_index_exists = False
        except Exception as e:
            print(f"\033[31mERROR: Failed to drop full-text index: {e}\033[0m")

    def get_all_authors(self) -> List[Author]:
        with self.driver.session() as session:
            return session.execute_read(self._get_all_authors)

    @staticmethod
    def _get_all_authors(tx) -> List[Author]:
        query = f"""
        MATCH (a:Author)
        OPTIONAL MATCH (a)-[:{RelationType.HAS_PAPER.name}]->(p:Paper)
        RETURN a.name AS name, COLLECT(p.id) AS pids, COLLECT(p.title) AS paper_titles
        """
        result = tx.run(query)
        authors = []
        for record in result:
            if record and record["name"]:
                authors.append(
                    Author.make_meta(
                        name=record["name"],
                        papers=[
                            (pid, title)
                            for pid, title in zip(
                                record["pids"], record["paper_titles"]
                            )
                            if pid is not None and title is not None
                        ],
                    )
                )
        return authors

    def get_all_papers(self) -> List[Paper]:
        with self.driver.session() as session:
            return session.execute_read(self._get_all_papers)

    @staticmethod
    def _get_all_papers(tx) -> List[Paper]:
        query = f"""
        MATCH (p:Paper)
        OPTIONAL MATCH (p)-[:{RelationType.AUTHORED_BY.name}]->(a:Author)
        WITH p, COLLECT(DISTINCT a.name) AS authors
        OPTIONAL MATCH (p)-[:{RelationType.BELONGS_TO.name}]->(c:Category)
        WITH p, authors, COLLECT(DISTINCT c.name) AS categories
        RETURN p.id AS pid, p.title AS title, p.abstract AS abstract, authors, categories
        """
        result = tx.run(query)
        papers = []
        for record in result:
            if record and record["pid"]:
                authors = [author for author in record["authors"] if author is not None]
                categories = [
                    category
                    for category in record["categories"]
                    if category is not None
                ]
                papers.append(
                    Paper.make_meta(
                        pid=record["pid"],
                        title=record["title"],
                        abstract=record["abstract"],
                        authors=authors,
                        categories=categories,
                    )
                )
        return papers

    def get_all_categories(self) -> List[Category]:
        with self.driver.session() as session:
            return session.execute_read(self._get_all_categories)

    @staticmethod
    def _get_all_categories(tx) -> List[Category]:
        query = f"""
        MATCH (c:Category)
        OPTIONAL MATCH (c)-[:{RelationType.CONTAINS.name}]->(p:Paper)
        RETURN c.name AS name, COLLECT(p.id) AS pids, COLLECT(p.title) AS paper_titles
        """
        result = tx.run(query)
        categories = []
        for record in result:
            if record and record["name"]:
                categories.append(
                    Category.make_meta(
                        name=record["name"],
                        papers=[
                            (pid, title)
                            for pid, title in zip(
                                record["pids"], record["paper_titles"]
                            )
                            if pid is not None and title is not None
                        ],
                    )
                )
        return categories

    def load_data_from_json(self, data: Dict):
        with self.driver.session() as session:
            session.execute_write(self._load_data_from_json, self, data)

    @staticmethod
    def _load_data_from_json(tx, gs: "GraphService", data: Dict):

        def clean_text(text):
            if not text:
                return ""
            text = re.sub(r"\n+", " ", text)
            text = re.sub(r"\r+", " ", text)
            text = re.sub(r"\t+", " ", text)
            text = re.sub(r"\s+", " ", text)
            text = text.strip()
            text = text.replace('"', '""')
            return text

        paper_id = data.get("id", "").strip()
        title = clean_text(data.get("title", ""))
        authors_str = data.get("authors", "").strip()
        categories_str = data.get("categories", "").strip()
        abstract = clean_text(data.get("abstract", ""))
        authors = [
            clean_text(author) for author in authors_str.split(", ") if author.strip()
        ]
        categories = [
            clean_text(cat) for cat in categories_str.split(" ") if cat.strip()
        ]

        gs.add_paper(paper_id, title, abstract)
        for author in authors:
            if author:
                gs.add_author(author)
                gs.link_author_to_paper(author, paper_id)
        for category in categories:
            if category:
                gs.add_category(category)
                gs.link_paper_to_category(paper_id, category)

    def get_overview_info(self) -> OverviewInfo:
        with self.driver.session() as session:
            return session.execute_read(self._get_overview_info)

    @staticmethod
    def _get_overview_info(tx) -> OverviewInfo:
        query = f"""
        MATCH (a:Author)
        WITH COUNT(a) AS total_authors
        MATCH (p:Paper)
        WITH total_authors, COUNT(p) AS total_papers
        MATCH (c:Category)
        WITH total_authors, total_papers, COUNT(c) AS total_categories
        OPTIONAL MATCH (c)-[:{RelationType.CONTAINS.name}]->(p:Paper)
        WITH total_authors, total_papers, total_categories, c.name AS category_name, COUNT(p) AS num_papers
        RETURN total_authors, total_papers, total_categories, COLLECT({{category: category_name, num_papers: num_papers}}) AS papers_per_category
        """
        result = tx.run(query)
        record = result.single()
        if record:
            num_papers_per_category = {
                item["category"]: item["num_papers"]
                for item in record["papers_per_category"]
                if item["category"] is not None
            }
            return OverviewInfo(
                total_authors=record["total_authors"],
                total_papers=record["total_papers"],
                total_categories=record["total_categories"],
                num_papers_per_category=num_papers_per_category,
            )
        return OverviewInfo(
            total_authors=0,
            total_papers=0,
            total_categories=0,
            num_papers_per_category={},
        )
