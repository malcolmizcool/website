from flask import Blueprint, render_template, request, redirect, session
import json
import random

suit_names = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
value_names = {'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
def format_card(card):
    value = card[:-1]
    suit = card[-1]
    value = value_names.get(value, value)
    suit = suit_names.get(suit, suit)
    return f"{value} {suit}"

def update_player_stats(username, updates):
    with open('playergameinfo.json', 'r') as f:
        players = json.load(f)
    for player in players:
        if player['user'] == username:
            for key, value in updates.items():
                player[key] = value
            break
    with open('playergameinfo.json', 'w') as f:
        json.dump(players, f)

def dealer_play(game):
    while calculate_hand(game['dealer_hand']) < 17:
        game['dealer_hand'].append(game['deck'].pop())
    return game

def calculate_hand(hand):
    total = 0
    aces = 0
    
    for card in hand:
        value = card[:-1]
        if value in ['J', 'Q', 'K']:
            total += 10
        elif value == 'A':
            total += 11
            aces += 1
        else:
            total += int(value)
    
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    
    return total

jack = Blueprint('jack', __name__)

@jack.route("/blackjack")
def blackjack():
    with open('playergameinfo.json', 'r') as f:
        info = json.load(f)
    player = next((p for p in info if p['user'] == session.get('user')), None)
    return render_template('blackjack.html', player=player, info=info)

@jack.route("/blackjack/solo")
def singlejack():
    bjack = False
    if 'blackjacksolo' not in session:
        suits = ['H', 'D', 'C', 'S']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [v + s for v in values for s in suits]
        random.shuffle(deck)

        game = {
            'deck': deck,
            'hand': [],
            'dealer_hand': [],
            'status': 'playing',
            'win': None
        }

        game['hand'].extend([game['deck'].pop(), game['deck'].pop()])
        game['dealer_hand'].extend([game['deck'].pop(), game['deck'].pop()])
        session['blackjacksolo'] = game
        if calculate_hand(game['hand']) == 21 and len(game['hand']) == 2:
            with open('playergameinfo.json', 'r') as f:
                players = json.load(f)
            if session.get('user'):
                for player in players:
                    if player['user'] == session['user']:
                        player['tblackjacks'] += 1
                        break
            with open('playergameinfo.json', 'w') as f:
                json.dump(players, f)
        session['blackjacksolo'] = game
    else:
        game = session['blackjacksolo']
    




    counted_hand = calculate_hand(game['hand'])
    if counted_hand == 21  and len(game['hand']) == 2:
        bjack = True

    formatted_hand = [format_card(c) for c in game['hand']]
    formatted_dealer = [format_card(c) for c in game['dealer_hand']]

    return render_template("blackjacksolo.html", game=game, hand=formatted_hand, dealer=formatted_dealer, bjack=bjack)

@jack.route("/blackjack/hit")
def hit():
    game = session['blackjacksolo']
    game['hand'].append(game['deck'].pop())
    session['blackjacksolo'] = game


    if calculate_hand(game['hand']) > 21:
        game['win'] = 'bust'
        game['status'] = 'end'
        session['blackjacksolo'] = game


    return redirect("/blackjack/solo")

@jack.route("/blackjack/end")
def stand():
    game = session['blackjacksolo']
    game['status'] = 'end'
    session['blackjacksolo'] = game

    if game['win'] is None:
        game = dealer_play(game)
        

    if calculate_hand(game['dealer_hand']) < calculate_hand(game['hand']) <= 21:
        game['win'] = True
        with open('playergameinfo.json', 'r') as f:
            players = json.load(f)
        if session.get('user'):
            for player in players:
                if player['user'] == session['user']:
                    player['bswins'] += 1
                    break
        with open('playergameinfo.json', 'w') as f:
            json.dump(players, f)

    
    if 21 >= calculate_hand(game['dealer_hand']) > calculate_hand(game['hand']):
        game['win'] = False
    
    if calculate_hand(game['dealer_hand']) > 21 and game['win'] != False:
        game['win'] = True
        with open('playergameinfo.json', 'r') as f:
            players = json.load(f)
        if session.get('user'):
            for player in players:
                if player['user'] == session['user']:
                    player['bswins'] += 1
                    break
        with open('playergameinfo.json', 'w') as f:
            json.dump(players, f)

    if calculate_hand(game['dealer_hand']) == calculate_hand(game['hand']):
        game['win'] = 'draw'

    session['blackjacksolo'] = game

    return redirect("/blackjack/solo")

@jack.route("/blackjack/reset")
def reset():
    session.pop('blackjacksolo', None)
    return redirect("/blackjack/solo")