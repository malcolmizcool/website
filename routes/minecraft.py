from flask import Blueprint, render_template, request, redirect, session, flash
import json
from datetime import datetime
import os
from helpers import load_json, award_achievement, award_flair, require_admin, data_path
import uuid
import pytz
from models import User
from extensions import db

minecraft = Blueprint('minecraft', __name__)

@minecraft.route('/minecraft', methods=['GET', 'POST'])
def minecraft_home():
    return render_template('minecraft/minecrafthome.html', title='Minecraft Server Status')