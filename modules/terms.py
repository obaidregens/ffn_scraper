import modules.mysql_connection as mysql

def ensure(term, taxonomy, parent=0):
    sql = """
    SELECT tt.term_id, tt.term_taxonomy_id
    FROM wp_terms AS t
    INNER JOIN wp_term_taxonomy as tt ON tt.term_id = t.term_id
    WHERE t.name = %s
    AND tt.parent = %s AND tt.taxonomy = %s
    ORDER BY t.term_id ASC
    LIMIT 1
    """
    mysql.db.execute(sql, [term, parent, taxonomy])
    term_row = mysql.db.fetchone()
    if term_row is not None:
        return int(term_row[0])
    
    insert1 = "INSERT INTO wp_terms (name,slug) VALUES (%s, %s)"
    mysql.db.execute(insert1,[term,term.lower().strip().replace(' ','-')])
    mysql.connection.commit()
    term_id = mysql.db.lastrowid
    insert2 = "INSERT INTO wp_term_taxonomy (term_taxonomy_id,term_id,taxonomy,description,parent) VALUES (%s,%s, %s, %s, %s)"
    mysql.db.execute(insert2,[term_id,term_id,taxonomy,"",parent])
    mysql.connection.commit()
    return int(term_id)
def connect(storyID,termID):
    sql = "INSERT INTO wp_term_relationships (object_id,term_taxonomy_id) VALUES (%s, %s)"
    try:
        mysql.db.execute(sql,[storyID,termID])
        mysql.connection.commit()
    except:
        pass
def updateCount():
    sql = """
    UPDATE wp_term_taxonomy SET count = (
    SELECT COUNT(*) FROM wp_term_relationships rel 
        LEFT JOIN wp_posts po ON (po.ID = rel.object_id) 
        WHERE 
            rel.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id 
            AND 
            wp_term_taxonomy.taxonomy NOT IN ('link_category')
            AND 
            po.post_status IN ('publish')
    )
    """
    mysql.db.execute(sql)
    mysql.connection.commit()
