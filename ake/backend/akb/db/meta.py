from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict


@dataclass
class Author:
    name: str
    # (pid, title)
    papers: List[Tuple[str, str]] = field(default_factory=list)

    @staticmethod
    def make_meta(
        name: str,
        papers: Optional[List[Tuple[str, str]]] = None,
    ) -> "Author":
        if papers is None:
            papers = []
        return Author(
            name=name,
            papers=papers,
        )


@dataclass
class Paper:
    pid: str
    title: str
    abstract: str
    authors: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.pid,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "categories": self.categories,
        }

    @staticmethod
    def make_meta(
        pid: str,
        title: str,
        abstract: str,
        authors: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
    ) -> "Paper":
        if authors is None:
            authors = []
        if categories is None:
            categories = []
        return Paper(
            pid=pid,
            title=title,
            abstract=abstract,
            authors=authors,
            categories=categories,
        )


@dataclass
class Category:
    name: str
    # (pid, title)
    papers: List[Tuple[str, str]] = field(default_factory=list)

    @staticmethod
    def make_meta(
        name: str,
        papers: Optional[List[Tuple[str, str]]] = None,
    ) -> "Category":
        if papers is None:
            papers = []
        return Category(
            name=name,
            papers=papers,
        )


@dataclass
class OverviewInfo:
    total_authors: int
    total_papers: int
    total_categories: int
    num_papers_per_category: Dict[str, int] = field(default_factory=dict)

    @staticmethod
    def make_meta(
        total_authors: int,
        total_papers: int,
        total_categories: int,
        num_papers_per_category: Optional[Dict[str, int]] = None,
    ) -> "OverviewInfo":
        if num_papers_per_category is None:
            num_papers_per_category = {}
        return OverviewInfo(
            total_authors=total_authors,
            total_papers=total_papers,
            total_categories=total_categories,
            num_papers_per_category=num_papers_per_category,
        )


@dataclass
class User:
    username: str
    password_hash: str

    @staticmethod
    def make_meta(
        username: str,
        password_hash: str,
    ) -> "User":
        return User(
            username=username,
            password_hash=password_hash,
        )
