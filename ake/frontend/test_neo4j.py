import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.akb.db.neo4j_connection import Neo4jConnection

def test_neo4j_connection():
    print("Testing Neo4j connection...")
    
    try:
        # 创建连接
        neo4j_conn = Neo4jConnection()
        driver = neo4j_conn.get_driver()
        
        print("✓ Successfully connected to Neo4j")
        
        # 只检查节点类型
        print("\nChecking node types in database:")
        query = """
        CALL db.labels() YIELD label
        CALL {
            WITH label
            MATCH (n)
            WHERE label IN labels(n)
            RETURN count(n) as count
        }
        RETURN label, count
        ORDER BY count DESC
        LIMIT 10
        """
        
        with driver.session() as session:
            result = session.run(query)
            for record in result:
                print(f"   {record['label']}: {record['count']} nodes")
        
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_neo4j_connection()