import telebot
from telebot import types
import random
import json

TOKEN = 'INSERT YOUR TOKEN HERE'


bot = telebot.TeleBot(TOKEN)
with open('codes.json', 'r') as f:
    codes = json.load(f)

#you should replace with usernames of actual admins
admin = "@Admin1"
support = "@Admin2"

btc_address = 'btc address or equivalent game card storage'
seller_pi_wallet = None
buyer_crypto_wallet = None


buy_command = "I want to buy Pi"
sell_command = "I want to sell Pi"
manage_command = "Manage my offers"
group_id = '@yourgrouphere'
offer_price = 0
max_amount = 0
buyer_amount = 0
claimed = False
new_code = 0
user_id = None


def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    item_buy = telebot.types.KeyboardButton(buy_command)
    item_sell = telebot.types.KeyboardButton(sell_command)
    manage_offers = telebot.types.KeyboardButton(manage_command)
    markup.add(item_sell, item_buy,manage_offers)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == sell_command) 
def sell_pi(message):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Go back")
    markup.add(button)
    bot.send_message(message.chat.id, "Please enter your offer price:", reply_markup=markup)
    bot.register_next_step_handler(message, process_sell)

def process_sell(message):
    if message.text == "Go back":
         go_back(message) 
    else:
     global offer_price
     global new_code
     global user_id
     offer_price = message.text
     chat_id = message.chat.id
     user_id = message.from_user.id
     if isfloat(offer_price):
        offer_price = float(offer_price)
        new_code = str(random.randint(1000, 9999))
        # Create a New unique code for the offer and Update the database
        codes[new_code] = {'username': user_id, 'status': 'active', 'price': offer_price, 'max_amount': max_amount, 'buyer_amount': buyer_amount,'seller_pi_wallet': seller_pi_wallet, 'buyer_crypto_wallet': buyer_crypto_wallet, 'buyer_pi_wallet': None,'seller_crypto,address': None,'claimed': claimed, 'msg_id': None,'payment_method': None,'msg': None}
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        bot.send_message(message.from_user.id, "Enter your Pi wallet address")
        bot.register_next_step_handler(message, pi_wallet)
     else:
        bot.send_message(chat_id, "Please enter a valid offer price as a number.")
        sell_pi(message)

def pi_wallet(message):
    if message.text == "Go back":
        go_back(message)
    else:
        codes[new_code]['seller_pi_wallet'] = message.text
        bot.send_message(message.from_user.id, "Please enter the maximum amount of Pi you would like to sell")
        bot.register_next_step_handler(message, amount_to_sell)

def amount_to_sell(message):
    if message.text == "Go back":
        go_back(message)
    else: 
        global max_amount
        if isfloat(message.text):
            max_amount = float(message.text)
            if max_amount < 5:
                bot.send_message(message.from_user.id, "The amount must be equal to or greater than 5")
                process_sell(message)
            else:
                codes[new_code]['max_amount'] = max_amount
                with open('codes.json', 'w') as f:
                    json.dump(codes, f, indent=2)
                print(max_amount)
                message_to_group = f"\nPi Seller: {message.from_user.first_name} \nCode: {new_code} \nPrice per PI: ${offer_price} \nAmount {max_amount}Pi \n Status: Available"
                group_msg = bot.send_message(group_id, message_to_group)
                codes[new_code]['msg'] = group_msg.text
                codes[new_code]['msg_id'] = group_msg.message_id
                with open('codes.json', 'w') as f:
                    json.dump(codes, f, indent=2)
                bot.send_message(message.from_user.id, f"submitted. Code: {new_code}")    
                bot.send_message(message.chat.id, f"\n`Code: {new_code} \nPrice per PI: ${offer_price} \nAmount {max_amount}Pi` \n\n Your offer has been posted in the offers section.", parse_mode="Markdown")




@bot.message_handler(func=lambda message: message.text == "Go back")
def go_back(message):
    start(message)

selected_offer = 0
@bot.message_handler(func=lambda message: message.text == buy_command)
def buy_pi(message):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Go back")
    markup.add(button)
    bot.send_message(message.chat.id, "Please enter the offer code from the group:", reply_markup=markup)
    bot.register_next_step_handler(message, process_buy)

def process_buy(message):
    if message.text == "Go back":
        go_back(message)
    else: 
        chat_id = message.chat.id
        if message.text.isdigit():
            # Check if the offer code exists in the codes dictionary
            offer_code = message.text
            global selected_offer
            selected_offer = offer_code
            
           
            if offer_code in codes:
                if codes[selected_offer]['status'] == 'claimed' or codes[selected_offer]['status'] == 'canceled':
                    bot.send_message(chat_id, "Unfortunately, This offer is Either claimed by another buyer or no longer available")
                    go_back(message)
                else:
                    #Todo: Retrieve the associated chat_id and notify the user
                    price = codes[offer_code]['price']
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    confirm = telebot.types.KeyboardButton("Confirm")
                    back = telebot.types.KeyboardButton("Go back")
                    markup.add(confirm,back)
                    bot.send_message(chat_id, f"Code: {offer_code} \nPrice per PI: ${price} \nMax-Amount {codes[offer_code]['max_amount']}Pi` \n\n Do you want to buy?", reply_markup=markup)

            else:
                    bot.send_message(chat_id, "Invalid offer code. Please enter a valid code from the group.")
                    if message.text.isdigit():
                        bot.register_next_step_handler(message, process_buy)
        else:
            if message.text != sell_command:
                bot.send_message(chat_id, "Please enter a valid offer code as a number.")
                bot.register_next_step_handler(message, process_buy)
            else:
                process_sell(message)


@bot.message_handler(func=lambda message: message.text == "Confirm")
def buy_amount(message):
    codes[selected_offer]['claimed'] = True
    group_msg = codes[selected_offer]['msg']
    print(group_msg)
    x = 'NOT Available or Claimed' in group_msg
    print(x)
    if 'Available' in group_msg:
        print(group_msg)
        new_group_msg = group_msg.replace('Available', 'UnAvailable or Claimed')
        print(new_group_msg)
        print("the message is availalbe")
        bot.edit_message_text(chat_id=group_id, text=new_group_msg, message_id=codes[selected_offer]['msg_id'])
        codes[selected_offer]['status'] = 'claimed' 
        codes[selected_offer]['msg'] = codes[selected_offer]['msg'].replace('Available', 'Unavailable or Claimed')
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
    else: 
        print("else case excuting")
    with open('codes.json', 'w') as f:
        json.dump(codes, f, indent=2)
    bot.send_message(admin, f"Someone is interested in the offer : `{selected_offer}`. \n\nThe bot has already sent a notification to the poster of the offer." )
    bot.send_message(codes[selected_offer]['username'], f"Someboy Is interested in your offer: <code>{selected_offer}</code>.\n\nKeep checking your notifications, We will request you to send the PI tokens to the buyer after the buyer deposits his/her assets in Escrow.\n\nWe have marked your offer as claimed BUT If you don't see a notification of the buyer depositing <b>within two hours</b>, Please Reactivate your offer ({selected_offer}) by clicking on 'Manage my Offers' in the menu", parse_mode="HTML")
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Go back")
    markup.add(button)
    bot.send_message(message.from_user.id, "How much Pi would you like to buy", reply_markup=markup)
    bot.register_next_step_handler(message, amount_verification)

def amount_verification(message):
    if message.text == 'Go back':
        go_back(message)
    else:    
        global buyer_amount
        max_amount = codes[selected_offer]['max_amount']
        print(max_amount * 0.5)
        if isfloat(message.text):
            if float(message.text) < (max_amount * 0.5) or float(message.text) > (max_amount):
                bot.send_message(message.from_user.id, "The amount you buy must be atleast 50% or half of the total offered amount and less than or equal to the total offered amount.")
                buy_amount(message)
            else:
                buyer_amount = float(message.text)
                codes[selected_offer]['buyer_amount'] = int(message.text)
                with open('codes.json', 'w') as f:
                    json.dump(codes, f, indent=2)
                markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
                btc = telebot.types.KeyboardButton("Bitcoin")
                eth = telebot.types.KeyboardButton("Ethereum")
                bnb = telebot.types.KeyboardButton("BNB (BSC)")
                back = telebot.types.KeyboardButton("Go back")
                markup.add(btc, eth, bnb, back)   
                bot.send_message(message.from_user.id, "Select a payment method from the menu", reply_markup=markup)     
        else:
            bot.send_message(message.from_user.id, "Please enter a valid value!")
            buy_amount(message)

@bot.message_handler(func=lambda message: message.text == "Bitcoin" )
def bitcoin_add(message):
    markup = telebot.types.ReplyKeyboardRemove() 
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Go back")
    markup.add(button)
    bot.send_message(message.from_user.id, "Send your Bitcoin Address.", reply_markup=markup)
    bot.register_next_step_handler(message, bitcoin_deposit)

def bitcoin_deposit(message):
    if message.text == 'Go back':
        go_back(message)
    else:
        codes[selected_offer]['payment_method'] = 'Bitcoin'
        global buyer_crypto_wallet
        buyer_crypto_wallet = message.text
        codes[selected_offer]['buyer_crypto_wallet'] = buyer_crypto_wallet
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        verify = telebot.types.KeyboardButton("Verify")
        markup.add(verify)
        price = codes[selected_offer]['price']
        bot.send_message(message.chat.id, f"Send {buyer_amount * price + (buyer_amount * price) *0.03}USD worth of Bitcoin to this address \n\n <code>{btc_address}</code> \n\nclick on VERIFY then send your Pi wallet when you are done so we can verify your deposit and send you {buyer_amount}Pi coins. \n\n <b>Do NOT click verify before completing your payment</b>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Ethereum" )
def ethereum_add(message):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Go back")
    markup.add(button)
    bot.send_message(message.from_user.id, "Send your Ethereum Address.", reply_markup=markup)
    bot.register_next_step_handler(message, ethereum_deposit)

def ethereum_deposit(message):
    if message.text == 'Go back':
        go_back(message)
    else:
        codes[selected_offer]['payment_method'] = 'Ethereum'
        global buyer_crypto_wallet
        buyer_crypto_wallet = message.text
        codes[selected_offer]['buyer_crypto_wallet'] = buyer_crypto_wallet
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        verify = telebot.types.KeyboardButton("Verify")
        markup.add(verify)
        price = codes[selected_offer]['price']
        bot.send_message(message.chat.id, f"Send {buyer_amount * price + (buyer_amount * price)*0.03}USD worth of Ethereum to this address \n\n <code>{eth_address}</code> \n\nclick on VERIFY then send your Pi wallet when you are done so we can verify your deposit and send you {buyer_amount}Pi coins. \n\n <b>Do NOT click verify before completing your payment</b>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "BNB (BSC)" )
def bnb_add(message):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Go back")
    markup.add(button)
    bot.send_message(message.from_user.id, "Send your BNB Address.", reply_markup=markup)
    bot.register_next_step_handler(message, bnb_deposit)

def bnb_deposit(message):
    if message.text == 'Go back':
        go_back(message)
    else:
        codes[selected_offer]['payment_method'] = 'BNB'
        global buyer_crypto_wallet
        buyer_crypto_wallet = message.text
        codes[selected_offer]['buyer_crypto_wallet'] = buyer_crypto_wallet
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        verify = telebot.types.KeyboardButton("Verify")
        markup.add(verify)
        price = codes[selected_offer]['price']
        bot.send_message(message.chat.id, f"Send {buyer_amount * price + (buyer_amount * price)*0.03}USD worth of BNB to this address \n\n <code>{bnb_address}</code> \n\nclick on VERIFY then send your Pi wallet when you are done so we can verify your deposit and send you {buyer_amount}Pi coins. \n\n <b>(Do NOT click verify before completing your payment )</b>", parse_mode="HTML", reply_markup=markup)


wait_msg = 0
wait_chat = 0
wait_id = 0
@bot.message_handler(func=lambda message: message.text == "Verify")
def verification(message):
    global wait_msg
    global wait_chat
    global wait_id
    wait_chat = message.chat.id
    markup = telebot.types.ReplyKeyboardRemove()
    wait_msg = bot.send_message(message.from_user.id, f"We are Verifying your Deposit, Wait... \n\n Send your Pi Address now while we verify your deposit. ", reply_markup=markup)
    wait_id = wait_msg.id
    amount = codes[selected_offer]['price']*codes[selected_offer]['buyer_amount']
    wallet = codes[selected_offer]['buyer_crypto_wallet']
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Approve", callback_data= f'approved')
    markup.add(button) 
    bot.send_message(admin, f"Amount: {amount} \n\nBuyer Addrress: {wallet} \n\n Our Addresses: {btc_address}\n{eth_address}\n{bnb_address}",  reply_markup=markup)
    bot.register_next_step_handler(message, buyer_pi_address_taker)


@bot.callback_query_handler(func=lambda call: call.data == "approved")
def approved(call):
    bot.send_message(wait_chat, "Verification Succesful! Send your Pi Address")
    bot.send_message(admin, "Verification message has been sent to the trader. He shall provide his Pi address now.")

def buyer_pi_address_taker(message):
    codes[selected_offer]['buyer_pi_wallet'] = message.text
    bot.send_message(admin, f'<code>{selected_offer}</code> \n\nBuyer Pi address <code>{message.text}</code>. \n\nSeller Pi Address: <code>{codes[selected_offer]["seller_pi_wallet"]}</code> \n\nPi Ammount: {codes[selected_offer]["buyer_amount"]} \n\nThe bot has sent this address to the seller asking them to deposit the pi and also to send thier {codes[selected_offer]["payment_method"]} Address', parse_mode="HTML")
    bot.send_message(message.from_user.id, f"You will receive {codes[selected_offer]['buyer_amount']}Pi to the provided address. Please contact our support {support} if you have any dispute")
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    submit = telebot.types.KeyboardButton("Submit")
    markup.add(submit)
    bot.send_message(codes[selected_offer]['username'], f"<b>The buyer's deposit has been approved.</b>\n\nSend {codes[selected_offer]['buyer_amount']}Pi coins (The amount the buyer agreed to buy) to: \n\n <code>{codes[selected_offer]['buyer_pi_wallet']}</code>\n\nPlease click on SUBMIT to send your {codes[selected_offer]['payment_method']} Address to the bot, You will receive ${codes[selected_offer]['price']*codes[selected_offer]['buyer_amount']} worth of {codes[selected_offer]['payment_method']} (Minus a 3% fee) AFTER we verify your Pi transaction. \n\nPlease contact our support {support} if you have any kind of dispute.", parse_mode="HTML", reply_markup=markup)



@bot.message_handler(func=lambda message: message.text == "Submit")
def crypto_address_taker(message):
    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, f"Send your {codes[selected_offer]['payment_method']} Address", reply_markup = markup)
    bot.register_next_step_handler(message, seller_crypto_address_taker)
def seller_crypto_address_taker(message):
    codes[selected_offer]['seller_crypto_wallet'] = message.text
    amnt = (codes[selected_offer]['price']*codes[selected_offer]['buyer_amount'])
    ourcut = (codes[selected_offer]['price']*codes[selected_offer]['buyer_amount']) * 0.03
    finalamnt = amnt - ourcut
    bot.send_message(admin, f"<code>{selected_offer}</code> \n\nSeller {codes[selected_offer]['payment_method']} address (SEND ASSETS HERE): <code>{message.text}</code>. \n\nBuyer BTC Address(Take assets we receieved from here): \n\n<code>{codes[selected_offer]['buyer_crypto_wallet']}</code> \n\n{codes[selected_offer]['payment_method']} Ammount to send(3% taken out): ${finalamnt}", parse_mode="HTML")
    bot.send_message(message.from_user.id, f"Sit back and relax now. You will receive ${finalamnt} worth of {codes[selected_offer]['payment_method']} shorty (A 3% has been taken out).  Please contact our support {support} if you have any dispute")







@bot.message_handler(func=lambda message: message.text == manage_command)
def manage_offers(message):
    
    user_offers = find_codes_by_username(codes, message.from_user.id)
    if len(user_offers) == 0:
        bot.send_message(message.chat.id, 'You have not made any offers. \n Press on "I want to buy Pi" to make an offer ')
    else:
        i = 0
        while i < len(user_offers):
            price = codes[user_offers[i]]['price']
            status = codes[user_offers[i]]['status']
            markup = types.InlineKeyboardMarkup()
            if status == 'active':
                button = types.InlineKeyboardButton("Cancele the offer", callback_data= f'cancel {user_offers[i]}')
            else:
                button = types.InlineKeyboardButton("Activate the offer", callback_data= f'activate {user_offers[i]}')
            markup.add(button)
            global msg_id 
            msg_id = bot.send_message(message.chat.id, f" Code: {user_offers[i]} \n Price: {price} \n Status: {status}",  reply_markup=markup)
            i += 1



@bot.callback_query_handler(func=lambda call: call.data.split()[-1] in find_codes_by_username(codes, call.from_user.id))
def activate_or_cancel(call):
    if call.data.split()[0] == 'cancel':
        codes[call.data.split()[-1]]['status'] = 'canceled' 
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        group_msg = codes[call.data.split()[-1]]['msg']
        bot.edit_message_text(chat_id=group_id, text=group_msg.replace('Available', 'Unavailable or Claimed'), message_id=codes[call.data.split()[-1]]['msg_id'])
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Activate The offer", callback_data= f'activate {call.message.text[6:10]}')
        markup.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, text=call.message.text.replace('active', 'canceled'), message_id=call.message.message_id, reply_markup=markup)
    elif call.data.split()[0] == 'activate':
        codes[call.data.split()[-1]]['status'] = 'active' 
        with open('codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        group_msg = codes[call.data.split()[-1]]['msg']
        bot.edit_message_text(chat_id=group_id, text=group_msg.replace('Unavailable or Claimed', 'Available'), message_id=codes[call.data.split()[-1]]['msg_id'])
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Cancel the offer", callback_data= f'cancel {call.message.text[6:10]}')
        markup.add(button)
        if 'claimed'in call.message.text:
            bot.edit_message_text(chat_id=call.message.chat.id, text=call.message.text.replace('claimed', 'active'), message_id=call.message.message_id, reply_markup=markup)
        bot.edit_message_text(chat_id=call.message.chat.id, text=call.message.text.replace('canceled', 'active'), message_id=call.message.message_id, reply_markup=markup)

def find_codes_by_username(data, target):
        matching_codes = []
        for code, info in data.items():
            if info.get('username') == target:
                matching_codes.append(code)
        return matching_codes


# Start the bot
bot.polling()

#Done, Daniel out! But Improving continues!  :)