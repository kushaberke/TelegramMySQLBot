import configparser # pip install configparser
from telethon import TelegramClient, events # pip install telethon
from datetime import datetime
import MySQLdb # pip install mysqlclient

### Ayarları Çeken Alan
print("Ayarlar Alınıyor...")
config = configparser.ConfigParser()
config.read('config.ini')

# API lerin okunduğu alan
API_ID = config.get('settings','api_id') 
API_HASH = config.get('settings','api_hash')
BOT_TOKEN = config.get('settings','bot_token')
session_name = "sessions/Bot"

# Database Bilgilerinin Alındığı Alan
HOSTNAME = config.get('settings','hostname')
USERNAME = config.get('settings','username')
PASSWORD = config.get('settings','password')
DATABASE = config.get('settings','database')

# Telethon Client Başlatan Alan
client = TelegramClient(session_name, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/basla"))
async def start(event):
    # Get sender
    sender = await event.get_sender()
    SENDER = sender.id
    
    # set text and send message
    text = "DataBase'e Sahip Kayıt Botudur."
    await client.send_message(SENDER, text)

### Insert command
@client.on(events.NewMessage(pattern="(?i)/ekle"))
async def insert(event):
    try:
        sender = await event.get_sender()
        SENDER = sender.id

        list_of_words = event.message.text.split(" ")
        name = list_of_words[1] 
        age = list_of_words[2] 
        dt_string = datetime.now().strftime("%d/%m/%Y")

        # Create the tuple "params" with all the parameters inserted by the user
        params = (name, age, dt_string)
        sql_command = "INSERT INTO kayıtlar VALUES (NULL, %s, %s, %s);"
        crsr.execute(sql_command, params) # Execute the query
        conn.commit() # commit the changes

        # If at least 1 row is affected by the query we send specific messages
        if crsr.rowcount < 1:
            text = "Hata"
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = "Kayıt Başarıyla Eklendi !"
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return


# Function that creates a message containing a list of all the oders
def create_message_select_query(ans):
    text = ""
    for i in ans:
        id = i[0]
        product = i[1]
        quantity = i[2]
        creation_date = i[3]
        text += "<b>"+ str(id) +"</b> | " + "<b>"+ str(product) +"</b> | " + "<b>"+ str(quantity)+"</b> | " + "<b>"+ str(creation_date)+"</b>\n"
    message = "<b>Received 📖 </b> Information about orders:\n\n"+text
    return message

### SELECT COMMAND
@client.on(events.NewMessage(pattern="(?i)/listele"))
async def select(event):
    try:
        # Get the sender of the message
        sender = await event.get_sender()
        SENDER = sender.id
        # Execute the query and get all (*) the oders
        crsr.execute("SELECT * FROM kayıtlar")
        res = crsr.fetchall() # fetch all the results
        # If there is at least 1 row selected, print a message with the list of all the oders
        # The message is created using the function defined above
        if(res):
            text = create_message_select_query(res) 
            await client.send_message(SENDER, text, parse_mode='html')
        # Otherwhise, print a default text
        else:
            text = "No orders found inside the database."
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return

@client.on(events.NewMessage(pattern="(?i)/sil"))
async def delete(event):
    try:
        # Get the sender
        sender = await event.get_sender()
        SENDER = sender.id

        #/ delete 1

        # get list of words inserted by the user
        list_of_words = event.message.text.split(" ")
        id = list_of_words[1] # The second (1) element is the id

        # Crete the DELETE query passing the id as a parameter
        sql_command = "DELETE FROM kayıtlar WHERE id = (%s);"

        # ans here will be the number of rows affected by the delete
        ans = crsr.execute(sql_command, (id,))
        conn.commit()
        
        # If at least 1 row is affected by the query we send a specific message
        if ans < 1:
            text = "Order with id {} is not present".format(id)
            await client.send_message(SENDER, text, parse_mode='html')
        else:
            text = "Order with id {} was correctly deleted".format(id)
            await client.send_message(SENDER, text, parse_mode='html')

    except Exception as e: 
        print(e)
        await client.send_message(SENDER, "Something Wrong happened... Check your code!", parse_mode='html')
        return




# Create database function
def create_database(query):
    try:
        crsr_mysql.execute(query)
        print("DataBase Başarıyla Oluşturuldu")
    except Exception as e:
        print(f"Hata: '{e}'")

        ##### MAIN
if __name__ == '__main__':
    try:
        print("DataBase'e Bağlanılıyor.")
        conn_mysql = MySQLdb.connect( host=HOSTNAME, user=USERNAME, passwd=PASSWORD )
        crsr_mysql = conn_mysql.cursor()

        query = "CREATE DATABASE "+str(DATABASE)
        create_database(query)
        conn = MySQLdb.connect( host=HOSTNAME, user=USERNAME, passwd=PASSWORD, db=DATABASE )
        crsr = conn.cursor()

        # Command that creates the "oders" table 
        sql_command = """CREATE TABLE IF NOT EXISTS kayıtlar ( 
            id INTEGER PRIMARY KEY AUTO_INCREMENT, 
            Name VARCHAR(200),
            Age INT(10), 
            Kayıt_Tarihi VARCHAR(100));"""

        crsr.execute(sql_command)
        print("Tablolar Hazır")
        
        print("Bot Başladı.")
        client.run_until_disconnected()

    except Exception as error:
        print('Cause: {}'.format(error))




