import mysql.connector
import os
from math import ceil, log
import json
import traceback
import datetime
import pickle as pkl
from glob import glob

class stage2:


    def __init__(self, dat_dir=r'C:\data', max_num_files=2000):
        self.__max_num_files = max_num_files
        self.__dat_dir = os.path.normpath(dat_dir)
        self.__metadata = {}
        self.__tables = ()


    def stepc(self):
        '''
        queries:
            0 = Find all users of Nebraska
            1 = All users who sent a message between 8am - 9am
            2 = All users who sent a message between 8am - 9am from Nebraska
            3 = All users who sent the maximum number of messages between 8am - 9am
                from Nebraska
        returns:
            List of all users matched in the query
        '''

        opt = self.__get_option()

        if opt == 0:
            self.query_nebraska()
        elif opt == 1:
            self.messages_in_time_range()
        elif opt == 2:
            self.messages_in_range_nebraska()
        elif opt == 3:
            self.max_num_messages_in_time_range_nebraska()


    def messages_in_time_range(self):

        print("Find timestamps for time range")
        self.__sort_table_by_column('Time', 'value')

        print("Find timeids between 8:30 and 9:30")
        ind = self.__get_val_by_col_id('Time', 'value')
        print(self.binary_search('08:30:00', 'Time', 'value'))
        print(self.binary_search('09:30:00', 'Time', 'value'))


    def __query_nebraska(self):

        print("Sorting State table on name column")
        self.__sort_table_by_column('State', 'name')

        print("Searching State table for Nebraska")
        state_data = self.binary_search('Nebraska', 'State', 'name')
        ind = self.__get_val_by_col_id('State', 'id')
        state_id = state_data[0][ind]

        print("Sorting Location table on stateid")
        self.__sort_table_by_column('Location', 'stateId')

        print("Searching Location table for Nebraska state id: {}".format(state_id))
        loc_data = self.find_all(state_id, 'Location', 'stateId')
        loc_id_ind = self.__get_val_by_col_id('Location', 'locationId')

        print(loc_data)

        print("Search for persons from nebraska by location id")
        self.__sort_table_by_column('Person', 'locationId')
        persons = []
        for loc in loc_data:
            persons.append(self.binary_search(loc[0], 'Person', 'locationId'))

        print(persons)


    #def __query_


    def find_all(self, value, table, col_id):

        val, fname = self.binary_search(value, table, col_id, return_fname=True)

        if fname != None:
            file_num = int(fname.split('_')[1][:-4])
        else:
            print("Binary Search returned None")
            return

        print("Starting with: {}".format(file_num))

        ind = self.__get_val_by_col_id(table, col_id)

        matching_entries = []
        b=False
        offset = 0
        while True:
            fname=os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, file_num + offset))
            if not os.path.isfile(fname):
                print("Not an existing file")
                break


            with open(fname, 'r') as dat_file:
                data = json.load(dat_file)

            for val in data:
                if str(val[ind]) == str(value):
                    matching_entries.append(val)
                else:
                    b = True
                    break
            if b:
                break

            offset += 1

        b=False
        offset = -1
        while True:
            fname=os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, file_num + offset))
            if not os.path.isfile(fname):
                print("Not an existing file")
                break

            with open(fname, 'r') as dat_file:
                data = json.load(dat_file)

            for val in data[::-1]:
                print("Val: {}, value {}".format(val[ind], value))
                if str(val[ind]) == str(value):
                    matching_entries.append(val)
                else:
                    b=True
                    break
            if b:
                break

            offset -= 1

        return matching_entries


    def __get_val_by_col_id(self, table, col_id):
        for i, field in enumerate(self.__metadata[table]['fields']):
            if field[0] == col_id:
                return i

        print("No valid column id")
        return None


    def binary_search(self, value, table, col_id, return_fname=False):

        self.get_metadata()

        for i, field in enumerate(self.__metadata[table]['fields']):
            if field[0] == col_id:
                col_num = i

        num_files = ceil( self.__metadata[table]['num_entries'] / self.__metadata[table]['entries_per_file'] ) - 1

        print(num_files)

        i_low = 0
        i_high = num_files

        iter_counter = 0
        max_iter = log(num_files, 2)

        print("Starting iterations")
        while i_low <= i_high:

            if iter_counter < max_iter:
                iter_counter += 1
            else:
                print("Maximum number of iterations reached.")
                break

            i = (i_high + i_low) // 2

            # print("low: {}; high: {}; i: {}".format(i_low, i_high, i))

            with open(os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, i))) as dat_file:
                # print("Checking file: {}_{:06d}.dat".format(table, i))
                res = self.entry_binary_search(json.load(dat_file), value, col_num)

            if res == -1:
                i_high = i - 1
            elif res == 1:
                i_low = i + 1
            elif return_fname:
                return res, "{}_{:06d}.dat".format(table, i)
            else:
                return res, None

        return None, None


    def entry_binary_search(self, data, value, col_num):

        if str(value) < str(data[0][col_num]):
            #print("{} is less than {}".format(value, data[0][col_num]))
            return -1
        elif str(value) > str(data[-1][col_num]):
            #print("{} is greater than {}".format(value, data[0][col_num]))
            return 1
        elif len(data) == 1:
            return data[0]

        i_low = 0
        i_high = len(data) - 1

        while i_low < i_high:
            i = (i_high - i_low) // 2

            if data[i][col_num] == value:
                return data[i]
            elif value > data[i][col_num]:
                i_low = i + 1
            else:
                i_high = i - 1

        return False


    def __get_option(self):

        print("STAGE 2, STEP C: Queries")
        print("=======================================================================================")
        print("  0 = Find all users of Nebraska")
        print("  1 = All users who sent a message between 8am - 9am")
        print("  2 = All users who sent a message between 8am - 9am from Nebraska")
        print("  3 = All users who sent the maximum number of messages between 8am - 9am from Nebraska")

        print("=======================================================================================")

        option = -1
        while option in [0,1,2,3]:
            option = input("Enter Option [0,1,2,3]: ")

        return option


    def stepa(self):
        if not os.path.isdir(self.__dat_dir):
            os.mkdir(self.__dat_dir)

        self.__write_db_to_files()


    def __sort_table_by_column(self, table, column):
        self.stepb(table, column)


    def stepb(self, table, column):
        '''
        Args:
            table is what table you want to sort
                options are:
                    [City, Date, Location, Message, Person, Time, Timestamp]
            column: column to sort by
                options depend on table
        '''

        self.get_metadata()

        if table not in self.__metadata:
            print("Invalid table name")
            return

        files = glob(os.path.join(self.__dat_dir, table + "_*.dat"))

        data = []
        for file in files:
            with open(file, 'r') as f:
                data += json.load(f)

        col_ind = -1
        for i, field in enumerate(self.__metadata[table]['fields']):
            if field[0] == column:
                col_ind = i
                break

        if col_ind == -1:
            print("Invalid column name")
            return

        data.sort(key=lambda x: str(x[col_ind]))

        entries_per_file = ceil(self.__metadata[table]['num_entries']) / self.__max_num_files

        i_ent = 0
        i_file = 0
        temp = []

        for entry in data:
            i_ent += 1
            temp.append(entry)
            if i_ent == entries_per_file:
                with open(os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, i_file)), 'w') as dat_file:
                    self.__dump_json(temp, dat_file)
                temp = []
                i_ent = 0
                i_file += 1

        if temp:
            with open(os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, i_file)), 'w') as dat_file:
                self.__dump_json(temp, dat_file)

        return


    def __write_db_to_files(self):
        self.__connect_db()

        if not hasattr(self, "__tables"):
            self.__fetch_tables()

        print("Tables in database:\n{}".format(self.__tables))

        self.__metadata = {}

        for (table,) in self.__tables:
            cur1 = self.__db.cursor()
            cur1.execute("SELECT COUNT(id) FROM " + table)
            num_entries = cur1.fetchone()[0]

            entries_per_file = ceil( num_entries / self.__max_num_files )

            fields = self.__get_table_columns(table)

            self.__metadata[table] = {
                'num_entries':num_entries,
                'entries_per_file':entries_per_file,
                'fields':fields
            }

            print("TABLE: {}".format(table))
            print("Number of entries: {}".format(num_entries))
            print("Entries per file: {}".format(entries_per_file))

            cur2 = self.__db.cursor()
            cur2.execute("SELECT * FROM " + table)

            i_ent=0
            i_file=0
            dat_file = open(os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, 0)), 'w')

            temp = []
            count = 0

            for vals in cur2.fetchall():

                temp.append(vals)
                i_ent += 1

                if i_ent == entries_per_file:
                    with open(os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, i_file)), 'w')\
                    as dat_file:
                        try:
                            count += len(temp)
                            self.__dump_json(temp, dat_file)
                        except TypeError:
                            traceback.print_exc()
                            print("For: {}".format(vals))
                            quit()
                        except Exception:
                            traceback.print_exc()
                            quit()
                    temp = []
                    i_ent = 0
                    i_file += 1

            if len(temp) > 0:
                with open(os.path.join(self.__dat_dir, "{}_{:06d}.dat".format(table, i_file)), 'w')\
                as dat_file:
                    try:
                        count += len(temp)
                        self.__dump_json(temp, dat_file)
                    except TypeError:
                        traceback.print_exc()
                        print("For: {}".format(vals))
                        quit()
                    except Exception:
                        traceback.print_exc()
                        quit()

            print("Number of entries stored: {}".format(count))
            print()


        self.__db.close()
        pkl.dump(self.__metadata, open(os.path.join(self.__dat_dir, 'metadata.pkl'), 'wb'))


    def get_metadata(self):
        if hasattr(self, '__metadata'):
            return self.__metadata
        elif os.path.isfile(os.path.join(self.__dat_dir, "metadata.pkl")):
            self.__metadata = pkl.load(open(os.path.join(self.__dat_dir, "metadata.pkl"), 'rb'))
            return self.__metadata
        else:
            self.__connect_db()
            self.__fetch_tables()

            self.__metadata = {}

            for (table,) in self.__tables:

                cur1 = self.__db.cursor()
                cur1.execute("SELECT COUNT(id) FROM " + table)
                num_entries = cur1.fetchone()[0]
                entries_per_file = ceil(float(num_entries) / self.__max_num_files)

                self.__metadata[table] = {
                    'num_entries':num_entries,
                    'entries_per_file':entries_per_file,
                    'fields':self.__get_table_columns(table)
                }
                with open(os.path.join(self.__dat_dir, 'metadata.pkl'), 'wb') as out:
                    pkl.dump(self.__metadata, out)

        return self.__metadata


    def __dump_json(self, vals, dat_file):

        try:
            if isinstance(vals[0][1], datetime.date) \
              or isinstance(vals[0][1], datetime.timedelta) \
              or isinstance(vals[0][1], datetime.time):
                json.dump([(val[0], str(val[1])) for val in vals], dat_file)

            else:
                json.dump(vals, dat_file)

        except Exception as e:
            print("Error dumping json")
            raise e
        return


    def __get_table_columns(self, table):

        cur = self.__db.cursor()
        cur.execute("DESC " + table)
        fields = cur.fetchall()
        cur.close()

        return tuple([field for field in fields])


    def __fetch_tables(self):

        if hasattr(self, '__tables'):
            return

        self.__connect_db()
        cur1 = self.__db.cursor()
        cur1.execute('SHOW TABLES')
        self.__tables = cur1.fetchall()
        cur1.close()
        return


    def __connect_db(self):

        if hasattr(self, '__db'):
            if self.__db.open:
                return

        config = {
            'user': 'cfarmer',
            'password': 'eKd65T',
            'host': 'cse.unl.edu',
            'database': 'cfarmer'
        }

        try:
            self.__db = mysql.connector.connect(**config)
        except Exception as e:
            print('Could not connect to database')
            raise e
