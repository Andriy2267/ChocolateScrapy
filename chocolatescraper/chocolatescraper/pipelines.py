# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import mysql.connector
import psycopg2


class ChocolatescraperPipeline:
    def process_item(self, item, spider):
        return item
    

class PriceTOUSDPipeline:
    gbpToUsdRate = 1.3

    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        if adapter.get('price'):

            floatprice = float(adapter['price'])

            adapter['price'] = floatprice * self.gbpToUsdRate 

            return item
        else:
            raise DropItem(f"Missing price in {item}")
        
        
class DuplicatesPipeline:

    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter['name'] in self.names_seen:
            raise DropItem(f"Deplicate item found: {item!r}")
        else:
            self.names_seen.add(adapter['name'])
            return item


class SavingToMySqlPipeline(object):

    def __init__(self):
        self.create_connection()
        ## Create books table if none exists
        self.curr = self.connection.cursor()
        self.curr.execute("""
        CREATE TABLE IF NOT EXISTS chocolatedb(
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255),
            name text,
            price DECIMAL
        )
        """)

    def create_connection(self):
        self.connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'Chopek$696$',
            database = 'chocolatedb',
            port = '3306'
        )
    

    def process_item(self, item, spider):
        self.store_db(item)
        return item
    
    def store_db(self, item):
        self.curr.execute("""INSERT INTO chocolatedb (name, price, url) VALUES (%s, %s, %s)""", (
            item["name"],
            item["price"],
            item["url"]
        ))
        self.connection.commit()


class SavingToPostgresql(object):

    def __init__(self):
        self.create_connection()
        

    def create_connection(self):
        self.connection = psycopg2.connect(
            database = 'chocolatedb',
            host = 'localhost',
            password = 'Chopek696',
            port = '5432',
            user = 'postgres'
        )
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        if "price" not in item:
            raise DropItem(f"Missing price in {item}")
        self.cursor.execute("""INSERT INTO chocolatedb (name, price, url) VALUES (%s, %s, %s)""", (
            item["name"],
            item["price"],
            item["url"]
        ))
        self.connection.commit()
