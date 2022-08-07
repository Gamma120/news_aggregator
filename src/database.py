from sqlalchemy import *
from datetime import datetime

from src.utils import *

# TODO : add utf8 format in db

class Database():
    
    def __init__(self, db_path: str):
        self.url = 'sqlite:///'+db_path
        self.engine = create_engine(self.url, future=True)
        self.meta = MetaData(bind=self.engine)
        if not os.path.exists(db_path):
            self.create_tables()
            logger = get_logger()
            logger.info("Database created at "+db_path)
    
    def create_tables(self):
        """
        Create the database tables.
        """
        
        # uniqueness of name in a channel
        # uniqueness of rss url in a channel
        # file name is auto-generated by utils methode nametofile
        rss_flux = Table('rss_flux', self.meta,
                         Column('id', Integer, primary_key=True),
                         Column('name', Unicode, nullable=False),
                         Column('file_name', String, nullable=False),
                         Column('url', String, nullable=False),
                         Column('channel', Integer, ForeignKey('channels.id'), nullable=False),
                         Column('last_item', String),
                         Column('last_time_fetched', FLOAT),
                         Column('update_rate', FLOAT),
                         UniqueConstraint('name', 'channel'))
        
        channels_filters = Table('channels_filters', self.meta,
                                Column('id', Integer, primary_key=True),
                                Column('filter', String, nullable=False),
                                Column('channel', String, ForeignKey('channels.id')),
                                UniqueConstraint('filter', 'channel'))
        
        channels = Table('channels', self.meta,
                         Column('id', INTEGER, primary_key=True),
                         Column('name', String, nullable=False),                         
                         Column('update_rate', FLOAT))
        
        self.meta.create_all(self.engine)
    
    def get_table(self, table_name: str) -> Table:
        """Get the Table object of table_name.

        Args:
            table_name (str): name of the table to return

        Returns:
            Table: Table object of table_name
        """
        
        return Table(table_name, self.meta, autoload_with=self.engine)     
    
    def get_table_list(self):
        return [table for table in self.meta.tables]
    
    def get_column_list(self, table_name: str):
        table = self.get_table(table_name)
        return table.columns.keys()
    
    def get_channels_rows(self) -> list[dict]:
        """Get the rows of the channels table.

        Returns:
            list[dict]: list of rows in channels table in dictionnary format
        """
        
        with self.engine.connect() as conn:
            channels = self.get_table('channels')
            select = channels.select()
            res = conn.execute(select)
            return [_row for _row in res]

    def get_channel_id(self, channel_name: str) -> int :
        """Get the channel discord id from channel name.

        Args:
            channel_name (str): channel name

        Returns:
            int: channel id
        """
        
        with self.engine.connect() as conn:
            channels = self.get_table('channels')
            select = channels.select().where (
                channels.c.name == channel_name
            )
            res = conn.execute(select)
            return res.first()['id']
    
    def get_channel_name(self, channel_id: int) -> str:
        """Get the channel name associated to the id provided.

        Args:
            channel_id (int): channel discord id

        Returns:
            str: channel name
        """
        
        with self.engine.connect() as conn:
            channels = self.get_table('channels')
            select = channels.select().where (
                channels.c.id == channel_id
            )
            res = conn.execute(select)
            return res.first()['name']
        
    def add_channel(self, channel_id: int, channel_name: str, update_rate: float = None):
        """Add a row in channels table.

        Args:
            channel_id (int): id of the discord channel
            channel_name (str): name of the discord channel
            update_rate (float, optional): default update rate for the rss flux in the channel. Default to None.
        """
        
        with self.engine.connect() as conn:
            channels = self.get_table('channels')
            ins = channels.insert().values(name = channel_name,
                                           id = channel_id,
                                           update_rate = update_rate)
            
            conn.execute(ins)
            conn.commit()

    def remove_channel(self, channel_id: int):
        """Remove a row in the channels table.

        Args:
            channel_id (int): channel discord id
        """
    
        with self.engine.connect() as conn:
            channels = self.get_table('channels')
            ins = channels.delete().where(and_(
                channels.c.id == channel_id
            ))
            conn.execute(ins)
            conn.commit()

    # TODO : test
    def edit_channel(self, channel_id: int, channel_name: str = None, update_rate: str = None):
        """Edit a row in the channels table.

        Args:
            channel_id (int): channel discrod id
            channel_name (str, optional): channel discord name. Defaults to None.
            update_rate (str, optional): default update rate for the rss flux in the channel. Defaults to None.
        """
        
        changes = {}
        if (channel_name != None): changes.update({'name': channel_name})
        if (update_rate != None): changes.update({'update_rate': update_rate})
        with self.engine.connect() as conn:
            channels = self.get_table('channels')
            edit = channels.update().where(
                channels.c.id == channel_id).values(changes)
            
            conn.execute(edit)
            conn.commit()

    # TODO : raise error
    def get_rss_row(self, rss_name: str, channel_id: int = None) -> list[dict]:
        """Get a row from the rss_flux table. If channel_id is not provided, could return multiple rows.

        Args:
            rss_name (str): name of the rss flux
            channel_id (int, optional): channel discord id. default is None.

        Returns:
            list[dict]: a list of row in dictionnary type
        """
        
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = None
            if(channel_id != None):
                ins = rss_flux.select().where(and_(
                    rss_flux.c.name == rss_name,
                    rss_flux.c.channel == channel_id)
                )
            else:
                ins = rss_flux.select().where(
                    rss_flux.c.name == rss_name
                )
            res = conn.execute(ins)
            return [dict(_row) for _row in res]
            
    
    def get_rss_rows(self, channel_id: int = None) -> list[dict]:
        """Get the rows from the rss_flux table.

        Args:
            channel (int, optional): id of the discord channel of the rows to select.
            Defaults select from all channels.

        Returns:
            list[dict]: list of rows in dictionnary type
        """
        
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            if(channel_id != None):
                select = rss_flux.select().where(
                    rss_flux.c.channel == channel_id
                )
            else:
                select = rss_flux.select()
            res = conn.execute(select)
            return [_row for _row in res]

    # TODO : replace rss_dict with the actual arguments 
    def add_rss_flux(self, rss_dict: dict, channel_id: int):
        """Add a new row in the table rss_flux.
        
        Args:
            rss_dict (dict): dictionnary of rss flux informations
            channel_id (int): channel discord id
        """
        
        if('channel' in rss_dict.keys()):
            channel_id = rss_dict.get('channel')
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.insert().values(name = rss_dict.get('name'),
                                        file_name = name_to_file(rss_dict.get('name'))+'.xml',
                                        url = rss_dict.get('url'),
                                        channel = channel_id,
                                        last_time_fetched = rss_dict.get('last_time_fetched'),
                                        update_rate = rss_dict.get('update_rate'))
            conn.execute(ins)
            conn.commit()
            
    def remove_rss_flux(self, name: str, channel_id: int):
        """Remove a row in the table rss_flux.
        
        Args:
            name (str): name of the rss flux to remove
            channel_id (int): channel discord id
        """
        
        # TODO : should raise error when it doesn't exist
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.delete().where(and_(
                rss_flux.c.name == name,
                rss_flux.c.channel == channel_id
            ))
            conn.execute(ins)
            conn.commit()

    # TODO : change dict to individual params
    def edit_rss_flux(self, name: str, channel_id: int, changes: dict):
        """Edit a row in the table rss_flux.
        
        Args:
            name (str): name of the rss flux to edit
            channel_id (int): channel discord id
            changes (dict): changes to edit
        """
        
        with self.engine.connect() as conn:
            rss_flux = self.get_table('rss_flux')
            ins = rss_flux.update().where(and_(
                rss_flux.c.name == name,
                rss_flux.c.channel == channel_id
            )).values(changes)
            conn.execute(ins)
            conn.commit()

    def to_fetch(self, channel_id: int = None) -> list[dict]:
        """Return a list of rss flux that need to be fetched. If a channel id is provided, it will only list those from the related channel.
        
        Args:
            channel_id (int, optional): channel discord id. Default is None.
        """
        
        now = date_to_int(datetime.utcnow())
        with self.engine.connect() as conn:
            rss_flux =  self.get_table('rss_flux')
            if (channel_id != None):
                ins = rss_flux.select().where(
                    and_(
                        rss_flux.c.channel == channel_id,
                        or_(
                            rss_flux.c.last_time_fetched == None,
                            rss_flux.c.update_rate == None,
                            rss_flux.c.last_time_fetched + rss_flux.c.update_rate <= now)
                        )
                    )
            else:
                ins = rss_flux.select().where(
                    or_(rss_flux.c.last_time_fetched == None,
                        rss_flux.c.update_rate == None,
                        rss_flux.c.last_time_fetched + rss_flux.c.update_rate <= now)
                    )
            res = conn.execute(ins)
            rows_list = []
            for row in res:
                rows_list.append(row._mapping)
            return rows_list

    # TODO : add verification of others parameters
    def valid_line(self, line: str, src_path: str, cpt_line: int) -> Boolean:
        """
        Check formating of a line in an imported files. Doesn't check the validity of the url.\n
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
                        
    # TODO : support others parameters      
    def import_list_rss(self, src_path: str, channel_id: int = None):
        """ Add rss flux in database from a text file in cvs format. If channel is provided, only rss flux from this channel will be exported.\n
        Format of the file:\n
            flux name;url[;channel[;last item[;last time fetched[;update rate]]]]

        Args:
            src_path (str): path to the file to import
            channel_id (str): id of the discord channel from which the rss flux must be subscribed. Default is None.
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
                    name = line[0]; url = line[1]
                    file_name = name_to_file(name)
                    if(len(line) > 2):
                        channel=line[2]
                        channel_id = self.get_channel_id(channel)
                    # Add entry to database
                    self.add_rss_flux({'name': name, 'file_name': file_name, 'url': url, 'channel': channel_id}, channel_id)
                cpt_line+=1
            logger.info("Import completed")
            rss_source.close()

    
    def export_list_rss(self, export_name: str = None, channel: int = None) -> str:
        """Convert the database to a text file csv format. 

        Args:
            export_name (str): name of the exported file. Default RSS-<date>.csv
            channel (str): id of the discord channel of the rows to select.
            Defaults select from all channels.
        
        Returns:
            str: path of the exported file
        """
        
        # Get the rows from the database
        rows_list = self.get_rss_rows(channel)

        # Create the file to export
        if(export_name == None): export_name = 'RSS-'+datetime.strftime(datetime.utcnow(),'%Y-%m-%d')+'.csv'
        export_path = os.path.join(PRJCT_TMP,export_name)
        export_file = open(export_path,'w')
        
        # add the format in comment
        export_file.write('# flux name;url;channel;last item;last time fetched;update rate\n')
        
        for row in rows_list:
            line=''
            # format to csv (doesn't add row id)
            for key in row.keys():
                if(key != 'id' and key != 'file_name'):
                    line+=str(row[key])+';'
            line+='\n'
            
            export_file.write(line)
        
        export_file.close()
        return export_path