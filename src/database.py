from sqlalchemy import *
from datetime import datetime
from .utils import *


# FIXME: logger

class Database():
    
    def __init__(self, db_path: str):
        set_directories()
        self.url = 'sqlite:///'+db_path
        self.engine = create_engine(self.url, future=True)
        self.meta = MetaData(bind=self.engine)
        if not os.path.exists(db_path):
            self.create_tables()
    
    def create_tables(self):
        """
        Create the database tables
        """
        
        # uniqueness of name in a channel
        # uniqueness of rss url in a channel
        # file name is auto-generated by utils methode nametofile
        rss_flux = Table('rss_flux', self.meta,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, nullable=False),
                         Column('file_name', String, nullable=False),
                         Column('url', String, nullable=False),
                         Column('channel', String, nullable=False),
                         Column('last_item', String),
                         Column('last_time_fetched', FLOAT),
                         Column('update_rate', FLOAT),
                         UniqueConstraint('name', 'channel'))
        
        channels_filters = Table('channels_filters', self.meta,
                                Column('id', Integer, primary_key=True),
                                Column('filter', String, nullable=False),
                                Column('channel', String, ForeignKey('rss_flux.channel')),
                                UniqueConstraint('filter', 'channel'))
        
        self.meta.create_all(self.engine)
    
    def get_table(self, table_name: str) -> Table:
        return Table(table_name, self.meta, autoload_with=self.engine)     
    
    def get_rss_row(self, row_id: dict) -> dict:
        """Get a row from the rss_flux table.

        Args:
            row_id (dict): dictionnary containing name and channel keys

        Returns:
            dict: the complet row in dictionnary type
        """
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.select().where(and_(
                rss_flux.c.name == row_id.get('name'),
                rss_flux.c.channel == row_id.get('channel'))
            )
            res = conn.execute(ins)
            row = res.mappings().all()
            assert len(row) == 1
            return row[0]
      
    def get_rss_flux_list(self) -> list:
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            select = rss_flux.select()
            res = conn.execute(select)
            return [_row.name for _row in res]
    
    def get_table_list(self):
        return [table for table in self.meta.tables]
    
    def get_column_list(self, table_name: str):
        table = self.get_table(table_name)
        return table.columns.keys() 
           
    def add_rss_flux(self, rss_dict: dict): # TODO : add multiple rss_flux
        """
        Add a new row in the table rss_flux,
        trigger by the discord command $add_rss
        """
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.insert().values(name = rss_dict.get('name'),
                                        file_name = name_to_file(rss_dict.get('name'))+'.xml',
                                        url = rss_dict.get('url'),
                                        channel = rss_dict.get('channel'),
                                        last_time_fetched = rss_dict.get('last_time_fetched'),
                                        update_rate = rss_dict.get('update_rate'))
            res = conn.execute(ins)
            conn.commit()
            
    def remove_rss_flux(self, name: str, channel: str):
        """
        Remove a row in the table rss_flux,
        trigger by the discord command $remove_rss
        """
        
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.delete().where(and_(
                rss_flux.c.name == name,
                rss_flux.c.channel == channel
            ))
            conn.execute(ins)
            conn.commit()

    def edit_rss_flux(self, name: str, channel: str, changes: dict):
        """
        Edit a row in the table rss_flux
        trigger by the discord command $edit_rss
        """
        
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.update().where(and_(
                rss_flux.c.name == name,
                rss_flux.c.channel == channel   
            )).values(changes)
            conn.execute(ins)
            conn.commit()

    def to_fetch(self) -> list[dict]:
        """
        return a list of rss flux that need to be fetched
        """
        
        now = date_to_int(datetime.utcnow())
        with self.engine.connect() as conn:
            rss_flux =  self.get_table('rss_flux')
            ins = rss_flux.select().where(or_(
                rss_flux.c.last_time_fetched == None,
                rss_flux.c.update_rate == None,
                rss_flux.c.last_time_fetched + rss_flux.c.update_rate <= now)
            )
            res = conn.execute(ins)
            rows_list = []
            for row in res:
                rows_list.append(row._mapping)
            return rows_list

    def valid_line(self, line: str, src_path: str, cpt_line: int) -> Boolean:
        """
        To know if a line is conform to an imported files. Doesn't check the validity of the url.\n
        Details of error are logged.

        Args:
            line (str): line from a file to import
            src_path (str): path of file to import
            cpt_line (int): line number in the file

        Returns:
            Boolean: True if the line is valid, False otherwise
        """
        
        logger = logging.getLogger('Database')
        if line[0] == "\n" or line[0] == "#":
            return False
        else:
            line = line.split(';')
            # line must have at least 2 info
            if len(line)<2:
                logger.error("Wrong formating in "+src_path+', line '+str(cpt_line))
                return False
            else:
                xml_url = line[0]
                xml_name = line[1].strip('\n')
                if xml_url=='' or xml_name=='':
                    logger.error("Wrong formating in "+src_path+', line '+str(cpt_line))
                    return False
        return True
                        
        
    def import_list(self, src_path: str, channel: str):
        """ Add rss flux in database from informations in a text file

        Args:
            src_path (str): path to the file to import
            channel (str): name of the discord channel from which the request is made
        """
        
        logger = logging.getLogger('Database')
        try:
            rss_source = open(src_path, 'r')
        
        except FileNotFoundError as e:
            logger.error(e)
        
        else:
            logger.info("Begin import...")
            cpt_line = 1 # To track line number for easier error message
            for line in rss_source:
                if(self.valid_line(line,src_path,cpt_line)):
                    line = line.strip('\n')
                    line = line.split(';')
                    name = line[0]
                    file_name = name_to_file(name)
                    url = line[1]
                    # Add entry to database
                    self.add_rss_flux({'name': name, 'file_name': file_name, 'url': url, 'channel': channel})
                cpt_line+=1
            logger.info("Import completed")
            rss_source.close()
            
# TODO : export flux