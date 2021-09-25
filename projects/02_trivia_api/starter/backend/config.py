import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
data_base_user_name=os.environ['UserName']
data_base_user_password=os.environ['Password']
data_base_url=os.environ['URL']
data_base_name=os.environ['DataBaseName']
SQLALCHEMY_DATABASE_URI="postgresql://{}:{}@{}/{}".format(data_base_user_name,data_base_user_password,data_base_url,data_base_name)
SQLALCHEMY_TRACK_MODIFICATIONS=False