import os, pyodbc

class SQL:
    def __init__(self, user):
        self.conn = pyodbc.connect(os.environ['SqlConnectionString'], autocommit=True)
        self.user = user

    # EXECUTE STORED PROCEDURE
    # schema = Stored Procedure Schema
    # sp = Stored Procedure Name
    # d = dict with param_name: param_value
    # usr = bool indicating to include st_Login parameter
    def execute(self, schema, sp, d=None, usr=True):
        cursor = self.conn.cursor()

        if d is None:
            cursor.execute(f"EXEC [{schema}].[{sp}]")
        else:
            if usr:
                d['st_Login'] = self.user
            s = f"EXEC [{schema}].[{sp}] "
            for key in d:
                if key[0]=="@":
                    s+= f"{key}=?,"
                else:
                    s+= f"@{key}=?,"
            cursor.execute(s[:-1],tuple(d.values()))
        try:
            data = cursor.fetchall()
            cols = [i[0] for i in cursor.description]
        except:
            data = None
            cols = []
        cursor.close()
        return data,cols