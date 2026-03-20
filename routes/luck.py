from flask import Blueprint, render_template, request, redirect, session
import json
from datetime import datetime
import os
from helpers import award_achievement

luck = Blueprint('luck', __name__)

@luck.route('/numberspin')
def main():
    

    return render_template('numberspin.html')