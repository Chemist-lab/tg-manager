from pathlib import Path
from function import *
from database_manager import *
import random
from PIL import Image, ImageFont, ImageDraw 
import os

from pathlib import Path

from telethon import functions
import json
import requests

user_menu_state = {}


async def usr_load_5_pic(who, msg_id):