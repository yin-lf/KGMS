# raw data from https://www.kaggle.com/datasets/Cornell-University/arxiv
# TOTAL: 17,088,511 triples

import csv
import json
import os
import re

SRC_JSON = "../../ake_backend/ake_backend/archive/arxiv-metadata-oai-snapshot.json"
OUTPUT_DIR = "output"

def clean_text(text):
    """清理文本中的问题字符"""
    if not text:
        return ""
    
    # 移除或替换换行符
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\r+', ' ', text)
    
    # 移除或替换制表符
    text = re.sub(r'\t+', ' ', text)
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除前后空白
    text = text.strip()
    
    # 替换可能导致CSV解析问题的双引号
    text = text.replace('"', '""')
    
    return text

def process_arxiv_jsonl():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 用于存储唯一的实体
    authors_set = set()
    papers_dict = {}  # paper_id -> {title, id}
    categories_set = set()
    
    # 用于存储关系
    author_paper_relations = []  # (author_name, paper_id)
    paper_category_relations = []  # (paper_id, category_name)
    
    with open(SRC_JSON, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                paper_id = data.get('id', '').strip()
                title = clean_text(data.get('title', ''))
                authors_str = data.get('authors', '').strip()
                categories_str = data.get('categories', '').strip()
                abstract = clean_text(data.get('abstract', ''))

                
                papers_dict[paper_id] = {
                    'id': paper_id,
                    'title': title,
                    'abstract': abstract,
                }

                authors = [clean_text(author) for author in authors_str.split(", ") if author.strip()]
                for author in authors:
                    if author:
                        authors_set.add(author)
                        author_paper_relations.append((author, paper_id))
                
                categories = [clean_text(cat) for cat in categories_str.split(" ") if cat.strip()]
                for category in categories:
                    if category:
                        categories_set.add(category)
                        paper_category_relations.append((paper_id, category))
                
            except json.JSONDecodeError as e:
                print(f"警告: 第{line_num}行JSON解析错误: {e}")
                continue
            except Exception as e:
                print(f"警告: 第{line_num}行处理错误: {e}")
                continue
    
    print(f"数据处理完成! 共处理了 {line_num} 行")
    print(f"- 论文数量: {len(papers_dict)}")
    print(f"- 作者数量: {len(authors_set)}")
    print(f"- 分类数量: {len(categories_set)}")
    print(f"- 作者-论文关系数量: {len(author_paper_relations)}")
    print(f"- 论文-分类关系数量: {len(paper_category_relations)}")
    
    print("\n正在生成TSV文件...")
    
    csv_config = {
        'delimiter': '\t',
        'quoting': csv.QUOTE_ALL,
        'quotechar': '"',
        'lineterminator': '\n'
    }
    
    # 1. authors.tsv
    authors_file = os.path.join(OUTPUT_DIR, "authors.tsv")
    with open(authors_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow(['name:ID(Author)'])
        for author in sorted(authors_set):
            writer.writerow([author])
    print(f"✓ 生成 {authors_file}")
    
    # 2. papers.tsv
    papers_file = os.path.join(OUTPUT_DIR, "papers.tsv")
    with open(papers_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow(['id:ID(Paper)', 'title', 'abstract'])
        for paper_id, paper_info in papers_dict.items():
            writer.writerow([paper_id, paper_info['title'], paper_info['abstract']])
    print(f"✓ 生成 {papers_file}")

    # 3. categories.tsv
    categories_file = os.path.join(OUTPUT_DIR, "categories.tsv")
    with open(categories_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow(['name:ID(Category)'])
        for category in sorted(categories_set):
            writer.writerow([category])
    print(f"✓ 生成 {categories_file}")
    
    # 4. Author -> Paper (HAS_PAPER)
    author_has_paper_file = os.path.join(OUTPUT_DIR, "author_has_paper.tsv")
    with open(author_has_paper_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow([':START_ID(Author)', ':END_ID(Paper)', ':TYPE'])
        for author, paper_id in author_paper_relations:
            writer.writerow([author, paper_id, 'HAS_PAPER'])
    print(f"✓ 生成 {author_has_paper_file}")
    
    # 5. Paper -> Author (AUTHORED_BY)
    paper_authored_by_file = os.path.join(OUTPUT_DIR, "paper_authored_by.tsv")
    with open(paper_authored_by_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow([':START_ID(Paper)', ':END_ID(Author)', ':TYPE'])
        for author, paper_id in author_paper_relations:
            writer.writerow([paper_id, author, 'AUTHORED_BY'])
    print(f"✓ 生成 {paper_authored_by_file}")
    
    # 6. Paper -> Category (BELONGS_TO)
    paper_belongs_to_file = os.path.join(OUTPUT_DIR, "paper_belongs_to.tsv")
    with open(paper_belongs_to_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow([':START_ID(Paper)', ':END_ID(Category)', ':TYPE'])
        for paper_id, category in paper_category_relations:
            writer.writerow([paper_id, category, 'BELONGS_TO'])
    print(f"✓ 生成 {paper_belongs_to_file}")
    
    # 7. Category -> Paper (CONTAINS)
    category_contains_file = os.path.join(OUTPUT_DIR, "category_contains.tsv")
    with open(category_contains_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, **csv_config)
        writer.writerow([':START_ID(Category)', ':END_ID(Paper)', ':TYPE'])
        for paper_id, category in paper_category_relations:
            writer.writerow([category, paper_id, 'CONTAINS'])
    print(f"✓ 生成 {category_contains_file}")
    
def main():
    if not os.path.exists(SRC_JSON):
        print(f"错误: 找不到输入文件 '{SRC_JSON}'")
        return
    
    try:
        process_arxiv_jsonl()
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()