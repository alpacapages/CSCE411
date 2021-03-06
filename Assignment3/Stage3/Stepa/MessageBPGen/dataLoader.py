from sys import exit

import mysql.connector

import dbCredentials

def importMessages():
    connection = getDbConnection()
    cursor = connection.cursor()

    sql = "select m.id, m.value, m.personId, ts.dateId, ts.timeId " \
    + "from Message m, Timestamp ts " \
    + "where m.timestampId = ts.id " \
    + "order by ts.timeId asc"

    cursor.execute(sql)

    messages = list()
    for (id, value, personId, dateId, timeId) in cursor:
        # message = (id, value, dateId, timeId)
        message = (timeId, id, value, personId, dateId)
        messages.append(message)

    cursor.close()
    connection.close()
    return messages

# def importPersonsAsQueue():
    # connection = getDbConnection()
    # cursor = connection.cursor()
#
    # sql = "select p.id, p.idStr, p.name, l.stateId, l.cityId " \
    # + "from Person p, Location l " \
    # + "where p.locationId = l.id " \
    # + "order by l.stateId"
#
    # cursor.execute(sql)
#
    # persons = Queue()
    # for (id, idStr, name, stateId, cityId) in cursor:
        # # person = (id, idStr, name, stateId, cityId)
        # person = (stateId, id, idStr, name, cityId)
        # persons.put(person)
#
    # cursor.close()
    # connection.close()
#
    # return persons


def importPersons():
    connection = getDbConnection()
    cursor = connection.cursor()

    sql = "select p.id, p.idStr, p.name, l.stateId, l.cityId " \
    + "from Person p, Location l " \
    + "where p.locationId = l.id " \
    + "order by l.stateId"

    cursor.execute(sql)

    persons = list()
    for (id, idStr, name, stateId, cityId) in cursor:
        # person = (id, idStr, name, stateId, cityId)
        person = (stateId, id, idStr, name, cityId)
        persons.append(person)

    cursor.close()
    connection.close()

    return persons

def getDbConnection():
    connection = mysql.connector.connect()

    try:
        connection = mysql.connector.connect(
            user=dbCredentials.USER, password=dbCredentials.PASSWORD,
            host=dbCredentials.HOST, database=dbCredentials.DATABASE)

    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            exit("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            exit("Database does not exist")
        else:
            exit(err)

    return connection

