from time import time
import modules.mysql_connection as mysql

def insert(storyID,characters):
    characters = list(set(characters))
    if len(characters) < 2:
        return False
    mysql.db.execute("SELECT pairing_id,character_id FROM character_pairings")
    r = mysql.db.fetchall()
    characters = list(map(str,characters))
    characters.sort()
    n = {}
    for pairing_id,character_id in r:
        n[pairing_id] = n.get(pairing_id,[])
        n[pairing_id].append(character_id)
    pp = 0
    for pairing_id,characters_of in n.items():
        characters_of = list(map(str,characters_of))
        characters_of.sort()
        if characters == characters_of:
            pp = pairing_id
            break
    # Pairing ID Got
    if pp == 0:
        mysql.db.execute("SELECT MAX(pairing_id) AS m FROM character_pairings")
        existsPair = mysql.db.fetchone()
        pp = 1
        if existsPair is not None and existsPair[0] is not None:
            pp = int(existsPair[0])+1
        sql = "INSERT INTO character_pairings (pairing_id, character_id) VALUES " + ",".join( ["('" + str(pp) + "', %s)"] * len(characters) )
        mysql.db.execute(sql,characters)
    try:
        mysql.insert(
            'pairing_relationships',
            {
                'pairing_id'    : pp,
                'book_id'       : storyID,
                'priority'      : 'major',
                'added_time'    : int(time())
            }
        )
    except:
        pass
    return int(pp)
