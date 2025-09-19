import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from akb.services import GraphService
from akb.db import Author, Paper, Category, OverviewInfo


@pytest.fixture(scope="module")
def graph_service():
    """
    Provides a GraphService instance for the test module.
    This fixture is scoped to the module, so the service is created once
    and torn down after all tests in the module have run.
    """
    service = GraphService()
    # Clear the database and create index before running tests
    service.clear_all_data()
    service.create_fulltext_index()
    yield service
    # Teardown: close the connection after tests are done
    service.close()


def test_add_and_find_author(graph_service):
    """
    Tests adding a new author and then finding them, returning an Author object.
    """
    author_name = "Test Author"
    paper_id = "test_paper_for_author"
    paper_title = "A Paper by Test Author"
    paper_abstract = "This is a test abstract."

    graph_service.add_author(author_name)
    graph_service.add_paper(paper_id, paper_title, paper_abstract)
    graph_service.link_author_to_paper(author_name, paper_id)

    author = graph_service.find_author_info(author_name)
    assert author is not None and isinstance(author, Author)
    assert author.name == author_name
    assert (paper_id, paper_title) in author.papers

    graph_service.clear_all_data()


def test_add_and_find_paper_by_id(graph_service):
    """
    Tests adding a new paper and then finding it by ID, returning a Paper object.
    """
    paper_id = "test_paper_001"
    paper_title = "A Test Paper"
    paper_abstract = "This is a test abstract."
    author_name = "Paper Author"
    category_name = "Paper Category"

    graph_service.add_paper(paper_id, paper_title, paper_abstract)
    graph_service.add_author(author_name)
    graph_service.add_category(category_name)
    graph_service.link_author_to_paper(author_name, paper_id)
    graph_service.link_paper_to_category(paper_id, category_name)

    paper = graph_service.find_paper_by_id(paper_id)
    assert paper is not None and isinstance(paper, Paper)
    assert paper.pid == paper_id
    assert paper.title == paper_title
    assert paper.abstract == paper_abstract
    assert author_name in paper.authors
    assert category_name in paper.categories

    graph_service.clear_all_data()


def test_add_and_find_category(graph_service):
    """
    Tests adding a new category and then finding it, returning a Category object.
    """
    category_name = "Test Category"
    paper_id = "test_paper_for_category"
    paper_title = "A Paper in Test Category"
    paper_abstract = "This is a test abstract."
    another_paper_id = "another_test_paper"
    another_paper_title = "Another Paper in Test Category"
    another_paper_abstract = "This is another test abstract."

    graph_service.add_category(category_name)
    graph_service.add_paper(paper_id, paper_title, paper_abstract)
    graph_service.add_paper(
        another_paper_id, another_paper_title, another_paper_abstract
    )
    graph_service.link_paper_to_category(paper_id, category_name)
    graph_service.link_paper_to_category(another_paper_id, category_name)

    category = graph_service.find_category(category_name)
    assert category is not None and isinstance(category, Category)
    assert category.name == category_name
    assert (paper_id, paper_title) in category.papers
    assert (another_paper_id, another_paper_title) in category.papers

    graph_service.clear_all_data()


def test_search_papers_by_title_and_abstract(graph_service):
    """
    Tests fuzzy searching for papers by title and abstract.
    """
    paper1_id = "search_paper_1"
    paper1_title = "Introduction to Graph Databases"
    paper1_abstract = "This paper discusses the fundamentals of graph databases."

    paper2_id = "search_paper_2"
    paper2_title = "Advanced Neo4j"
    paper2_abstract = "A deep dive into advanced features of the Neo4j graph database."

    graph_service.add_paper(paper1_id, paper1_title, paper1_abstract)
    graph_service.add_paper(paper2_id, paper2_title, paper2_abstract)

    # Search for "graph database"
    results = graph_service.search_papers("graph database")
    assert len(results) >= 2
    assert isinstance(results[0], Paper)

    # Check if the most relevant result is first
    assert results[0].pid == paper2_id or results[0].pid == paper1_id

    # Search for "fundamentals"
    results = graph_service.search_papers("fundamentals")
    assert len(results) == 1
    assert results[0].pid == paper1_id

    graph_service.clear_all_data()


def test_update_paper_with_abstract(graph_service):
    """
    Tests updating a paper's title and abstract.
    """
    paper_id = "update_paper_001"
    old_title = "Old Title"
    new_title = "New Title"
    new_abstract = "This is the new abstract."
    graph_service.add_paper(paper_id, old_title)
    graph_service.update_paper(paper_id, new_title, new_abstract)

    paper = graph_service.find_paper_by_id(paper_id)
    assert paper is not None and isinstance(paper, Paper)
    assert paper.title == new_title
    assert paper.abstract == new_abstract

    graph_service.clear_all_data()


def test_update_category(graph_service):
    """
    Tests updating a category's name.
    """
    old_name = "Old Category"
    new_name = "New Category"
    graph_service.add_category(old_name)
    graph_service.update_category(old_name, new_name)

    assert graph_service.find_category(old_name) is None
    new_category = graph_service.find_category(new_name)
    assert new_category is not None and isinstance(new_category, Category)
    assert new_category.name == new_name

    graph_service.clear_all_data()


def test_delete_author(graph_service):
    """
    Tests deleting an author.
    """
    author_name = "Author to Delete"
    graph_service.add_author(author_name)
    assert graph_service.find_author_info(author_name) is not None
    graph_service.delete_author(author_name)
    assert graph_service.find_author_info(author_name) is None


def test_delete_paper(graph_service):
    """
    Tests deleting a paper.
    """
    paper_id = "paper_to_delete_001"
    paper_title = "A Paper to be Deleted"
    graph_service.add_paper(paper_id, paper_title)
    assert graph_service.find_paper_by_id(paper_id) is not None
    graph_service.delete_paper(paper_id)
    assert graph_service.find_paper_by_id(paper_id) is None


def test_delete_category(graph_service):
    """
    Tests deleting a category.
    """
    category_name = "Category to Delete"
    graph_service.add_category(category_name)
    assert graph_service.find_category(category_name) is not None
    graph_service.delete_category(category_name)
    assert graph_service.find_category(category_name) is None


def test_clear_all_data(graph_service):
    """
    Tests clearing all data from the database.
    """
    graph_service.add_author("Temp Author")
    graph_service.add_paper("temp_paper_001", "Temp Paper")
    graph_service.add_category("Temp Category")

    graph_service.clear_all_data()

    assert graph_service.find_author_info("Temp Author") is None
    assert graph_service.find_paper_by_id("temp_paper_001") is None
    assert graph_service.find_category("Temp Category") is None


def test_get_all_authors(graph_service):
    """
    Tests retrieving all authors.
    """
    author1 = "Author One"
    author2 = "Author Two"
    graph_service.add_author(author1)
    graph_service.add_author(author2)

    authors = graph_service.get_all_authors()
    assert len(authors) >= 2
    author_names = [author.name for author in authors]
    assert author1 in author_names
    assert author2 in author_names

    graph_service.clear_all_data()


def test_get_all_papers(graph_service):
    """
    Tests retrieving all papers.
    """
    paper1_id = "all_papers_001"
    paper1_title = "First Paper"
    paper2_id = "all_papers_002"
    paper2_title = "Second Paper"
    graph_service.add_paper(paper1_id, paper1_title)
    graph_service.add_paper(paper2_id, paper2_title)

    papers = graph_service.get_all_papers()
    assert len(papers) >= 2
    paper_ids = [paper.pid for paper in papers]
    assert paper1_id in paper_ids
    assert paper2_id in paper_ids

    graph_service.clear_all_data()


def test_get_all_categories(graph_service):
    """
    Tests retrieving all categories.
    """
    category1 = "Category One"
    category2 = "Category Two"
    graph_service.add_category(category1)
    graph_service.add_category(category2)

    categories = graph_service.get_all_categories()
    assert len(categories) >= 2
    category_names = [category.name for category in categories]
    assert category1 in category_names
    assert category2 in category_names

    graph_service.clear_all_data()


def test_load_from_json(graph_service):
    """
    Tests loading data from a JSON file.
    """
    test_data = {
        "id": "10.101",
        "title": "JSON Paper Title",
        "abstract": "This is a test abstract from JSON.",
        "authors": "author1, author2",
        "categories": "category1 category2",
    }
    test_data2 = {
        "id": "10.102",
        "title": "JSON Paper Title 2",
        "abstract": "This is a test abstract from JSON.",
        "authors": "author1, author2",
        "categories": "category1 category2",
    }

    graph_service.load_data_from_json(test_data)
    graph_service.load_data_from_json(test_data2)

    paper = graph_service.find_paper_by_id("10.101")
    assert paper is not None and isinstance(paper, Paper)
    assert paper.title == "JSON Paper Title"
    assert paper.abstract == "This is a test abstract from JSON."
    assert "author1" in paper.authors
    assert "author2" in paper.authors
    assert "category1" in paper.categories
    assert "category2" in paper.categories

    author1 = graph_service.find_author_info("author1")
    assert author1 is not None and isinstance(author1, Author)
    assert ("10.101", "JSON Paper Title") in author1.papers

    author2 = graph_service.find_author_info("author2")
    assert author2 is not None and isinstance(author2, Author)
    assert ("10.101", "JSON Paper Title") in author2.papers

    category1 = graph_service.find_category("category1")
    assert category1 is not None and isinstance(category1, Category)
    assert ("10.101", "JSON Paper Title") in category1.papers

    category2 = graph_service.find_category("category2")
    assert category2 is not None and isinstance(category2, Category)
    assert ("10.101", "JSON Paper Title") in category2.papers

    graph_service.clear_all_data()


def test_get_overview_info(graph_service):
    """
    Tests retrieving overview information from the graph database.
    """
    # Add some test data
    authors = ["Author A", "Author B"]
    papers = [("paper_001", "Paper One"), ("paper_002", "Paper Two")]
    categories = ["Category X", "Category Y"]

    for author in authors:
        graph_service.add_author(author)
    for pid, title in papers:
        graph_service.add_paper(pid, title)
    for category in categories:
        graph_service.add_category(category)

    # Link authors to papers and papers to categories
    graph_service.link_author_to_paper("Author A", "paper_001")
    graph_service.link_author_to_paper("Author B", "paper_002")
    graph_service.link_paper_to_category("paper_001", "Category X")
    graph_service.link_paper_to_category("paper_002", "Category Y")

    # Retrieve overview info
    overview = graph_service.get_overview_info()
    assert overview is not None and isinstance(overview, OverviewInfo)
    assert overview.total_authors == 2
    assert overview.total_papers == 2
    assert overview.total_categories == 2
    assert (
        "Category X" in overview.num_papers_per_category
        and overview.num_papers_per_category["Category X"] == 1
    )
    assert (
        "Category Y" in overview.num_papers_per_category
        and overview.num_papers_per_category["Category Y"] == 1
    )

    graph_service.clear_all_data()
