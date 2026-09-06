import psycopg2 

class SQL():

    # Запрос для отображения существующих таблиц
    def get_tables(bd):
        try:
            if not bd or not bd.open or bd.cursor is None:
                print("Нет подключения или курсора")
                return []
                     
            bd.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = bd.cursor.fetchall()
            
            result = [table[0] for table in tables] if tables else []
            return result
            
        except Exception as error:
            print(f"Ошибка SQL: {error}")
            return []



    @staticmethod
    def get_table_data(bd, table_name):
        try:
            if not bd or not bd.open or not table_name:
                return None, None
            
            bd.cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s AND table_schema = 'public')",
                (table_name.lower(),)
            )
            if not bd.cursor.fetchone()[0]:
                return None, None
            
            bd.cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s ORDER BY ordinal_position",
                (table_name.lower(),)
            )
            columns = [col[0] for col in bd.cursor.fetchall()]
            
            bd.cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")
            data = bd.cursor.fetchall()
            
            return columns, data
            
        except Exception as e:
            print(f"Error in get_table_data: {e}")
            return None, None
        
    

    @staticmethod
    def create_table(bd, table_name, columns):
    
        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            raise Exception("Table name cannot be empty")
        
        if not columns:
            raise Exception("Columns cannot be empty")
        
        valid_types = [
            'INTEGER', 'BIGINT', 'SMALLINT', 'REAL', 'DOUBLE PRECISION',
            'DECIMAL', 'NUMERIC', 'VARCHAR', 'CHAR', 'TEXT',
            'DATE', 'TIME', 'TIMESTAMP', 'BOOLEAN', 'JSON', 'JSONB',
            'UUID', 'BYTEA', 'SERIAL', 'BIGSERIAL'
        ]
        
        for col in columns:
            col_type = col['type'].upper().strip()
            
            if col_type.startswith('VARCHAR') or col_type.startswith('CHAR'):
                continue
            
            if col_type not in valid_types:
                col['type'] = 'TEXT'
        
        has_id = any(col['name'].lower() == 'id' for col in columns)
        
        if has_id:
            columns_str = ", ".join([f"{col['name']} {col['type']}" for col in columns])
        else:
            columns_str = f"id SERIAL PRIMARY KEY, " + ", ".join([f"{col['name']} {col['type']}" for col in columns])
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        print(query)  
        
        try:
            bd.cursor.execute(query)
            bd.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error creating table: {str(e)}")
        
    
    @staticmethod
    def delete_table(bd, table_name):
       
        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            raise Exception("Table name cannot be empty")
        
        check_query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        bd.cursor.execute(check_query, (table_name.lower(),))
        exists = bd.cursor.fetchone()[0]
        
        if not exists:
            raise Exception(f"Table '{table_name}' does not exist")
        
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
        
        try:
            bd.cursor.execute(query)
            bd.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting table: {str(e)}")

    
    @staticmethod
    def add_column(bd, table_name, column_name, column_type):
       
        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            raise Exception("Table name cannot be empty")
        
        if not column_name:
            raise Exception("Column name cannot be empty")
        
        if not column_type:
            column_type = "TEXT"
        
        check_query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        bd.cursor.execute(check_query, (table_name.lower(),))
        exists = bd.cursor.fetchone()[0]
        
        if not exists:
            raise Exception(f"Table '{table_name}' does not exist")
        
        check_column = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s)"
        bd.cursor.execute(check_column, (table_name.lower(), column_name.lower()))
        column_exists = bd.cursor.fetchone()[0]
        
        if column_exists:
            raise Exception(f"Column '{column_name}' already exists in table '{table_name}'")
        
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        try:
            bd.cursor.execute(query)
            bd.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error adding column: {str(e)}")

    
    @staticmethod
    def table_exists(bd, table_name):

        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            return False
        
        query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        bd.cursor.execute(query, (table_name.lower(),))
        exists = bd.cursor.fetchone()[0]
        
        return exists

    

    @staticmethod
    def get_table_structure(bd, table_name):
        
        try:
            if not bd or not bd.open or not table_name:
                return None
            
            bd.cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s AND table_schema = 'public')",
                (table_name.lower(),)
            )
            if not bd.cursor.fetchone()[0]:
                return None
            
            bd.cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name.lower(),))
            
            columns = []
            for col in bd.cursor.fetchall():
                column_info = {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == 'YES',
                    "default": col[3]
                }
                columns.append(column_info)
            
            return columns
            
        except Exception as e:
            print(f"Error in get_table_structure: {e}")
            return None


    @staticmethod
    def add_record(bd, table_name, columns, values):
       
        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            raise Exception("Table name cannot be empty")
        
        if not columns or not values:
            raise Exception("Columns and values cannot be empty")
        
        if len(columns) != len(values):
            raise Exception("Number of columns and values do not match")
        
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        try:
            bd.cursor.execute(query, values)
            bd.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error adding record: {str(e)}")

    
    @staticmethod
    def get_record_by_id(bd, table_name, record_id, id_column='id'):
        
        try:
            if not bd or not bd.open or not table_name:
                return None
            
            query = f"SELECT * FROM {table_name} WHERE {id_column} = %s"
            bd.cursor.execute(query, (record_id,))
            row = bd.cursor.fetchone()
            
            if not row:
                return None
            
            bd.cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name.lower(),))
            columns = [col[0] for col in bd.cursor.fetchall()]
            
            record = {}
            for i, col in enumerate(columns):
                record[col] = row[i]
            
            return record
            
        except Exception as e:
            print(f"Error in get_record_by_id: {e}")
            return None

    
    @staticmethod
    def update_record(bd, table_name, record_id, data, id_column='id'):
    
        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            raise Exception("Table name cannot be empty")
        
        if not data:
            raise Exception("No data to update")
        
        set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
        values = list(data.values())
        values.append(record_id)
        
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
        
        try:
            bd.cursor.execute(query, values)
            bd.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error updating record: {str(e)}")


    @staticmethod
    def delete_record(bd, table_name, record_id, id_column='id'):
    
        if not bd or not bd.open:
            raise Exception("No connection to database")
        
        if not table_name:
            raise Exception("Table name cannot be empty")
        
        if record_id is None:
            raise Exception("Record ID cannot be empty")
        
        query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        
        try:
            bd.cursor.execute(query, (record_id,))
            bd.connection.commit()
            return True
        except Exception as e:
            raise Exception(f"Error deleting record: {str(e)}")

            
    @staticmethod
    def search_records(bd, table_name, column, search_text):
        
        try:
            if not bd or not bd.open:
                return []
            
            if not table_name or not column or not search_text:
                return []
            
            search_pattern = f"%{search_text}%"
            
            bd.cursor.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = %s
            """, (table_name.lower(), column.lower()))
            
            result = bd.cursor.fetchone()
            if not result:
                return []
            
            data_type = result[0]
            
            if data_type in ('integer', 'bigint', 'smallint', 'numeric', 'decimal'):
                try:
                    int(search_text)
                    query = f"SELECT * FROM {table_name} WHERE {column} = %s ORDER BY id"
                    bd.cursor.execute(query, (search_text,))
                except ValueError:
                    return []
            else:
                query = f"SELECT * FROM {table_name} WHERE {column}::text ILIKE %s ORDER BY id"
                bd.cursor.execute(query, (search_pattern,))
            
            data = bd.cursor.fetchall()
            return data
            
        except Exception as e:
            print(f"Search error: {e}")
            return []