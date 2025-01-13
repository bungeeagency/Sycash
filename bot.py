from interactions import (
    Client,
    CommandContext,
    ComponentContext,
    Modal,
    TextInput,
    TextStyleType,
    Button,
    Embed
)
from email.utils import formataddr
import interactions
import db_manage
import re
import time
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow
from flask import Flask
from flask import request
from cryptography.fernet import Fernet
import finance.sypay as sypay
import email
import smtplib
import random
import asyncio

#############################################################################
APIKEY = ""
app = Flask(__name__)
handshake=[]
verif_pool=[]
actions_pool=[]
key=b''
fernet = Fernet(key)
profit=0.035
bot = Client(APIKEY)
regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

#############################################################################
Embed()
def run_flask():

    app.run(host='127.0.0.1',port=25400)


@app.route("/events")
def events():
    query=request.get_json()
    dec_key=fernet.decrypt(query['secret'].encode()).decode()
    if dec_key==query['tag'] and query['tag'] in handshake:
        db_manage.add_to_bal(query['tag'],float(query['amount']))
        while query['tag'] in handshake:
            handshake.remove(query['tag'])
        return "Successfully added "+str(query['amount'])+" EU to "+query['tag']+" account."
    else:
        return "Bad request"


#############################################################################
@bot.event
async def on_ready():
    print("Ready!")

#############################################################################
class utils:
    def wd(method):
        method=method[0]
        if method=="paypal":
            cid="ret_paypal"
        elif method=="bank":
            cid="ret_bank"
        else:
            cid="ret_crypto"


        modal = Modal(
            custom_id=cid,
            title="Withdrawal",
            components=[TextInput(
                    style=TextStyleType.SHORT,
                    label="Entrez le montant que vous voulez retirer",
                    placeholder="Montant",
                    custom_id="ret_value",
                    min_length=1,
                    max_length=4,)])
        return modal
    def add(method):
        method=method[0]
        if method=="paypal":
            cid="add_paypal"
        elif method=="bank":
            cid="add_bank"
        else:
            cid="add_crypto"
        modal = Modal(
        custom_id=cid,
        title="Ajouter de l'argent a votre compte Sycash",
        components=[

            TextInput(
                style=TextStyleType.SHORT,
                label="Entrez le montant à ajouter",
                placeholder="Montant",
                custom_id="modal-add",
                min_length=1,
                max_length=4,)],)
        return modal

#############################################################################
@bot.component("wd-menu")
async def primary_component(ctx: interactions.ComponentContext,choice):

    await ctx.popup(utils.wd(choice))

@bot.component("add-menu")
async def primary_component(ctx: interactions.ComponentContext,choice):
    await ctx.popup(utils.add(choice))

#############################################################################

@bot.command(name="verify", description="Verify or activate your Sycash account." ,options = [interactions.Option(name="code",description="verifcation code",type=interactions.OptionType.STRING,required=True,),])
async def verif(ctx: CommandContext,code):
    id=str(ctx.author.id)
    ppl=db_manage.get(id)['paypal']
    iban=db_manage.get(id)['iban']
    btc=db_manage.get(id)['btc_addr']
    modal_i = Modal(
                custom_id="infos",
                title="Fill your withdrawal informations.",
                components=[TextInput(
                        style=TextStyleType.SHORT,
                        label="Paypal account email",
                        value=ppl,
                        custom_id="ppl",required=False),TextInput(
                        style=TextStyleType.SHORT,
                        label="IBAN",
                        value=iban,
                        custom_id="iban",required=False),TextInput(
                        style=TextStyleType.SHORT,
                        label="BTC address",
                        value=btc,
                        custom_id="btc",required=False)])
    auth={id:code}
    if auth in verif_pool:
        verif_pool.remove(auth)
        if len(code)==6:
            db_manage.verify(id)
            db_manage.set_session(id,0.5)
            await ctx.popup(modal_i)
            return
        elif len(code)==7:
            pos=0
            for item in actions_pool:
                if id in item.keys():
                    break
                else:
                    pos+=1
                
            db_manage.set_session(id,0.5)
            db_manage.change_mail(id,actions_pool[pos][id]['mail'][0])
            db_manage.update_winfos(id,actions_pool[pos][id]['paypal'],actions_pool[pos][id]['iban'],actions_pool[pos][id]['btc'])
            actions_pool.pop(pos)
            db_manage.log(2,id,"new infos")
            await ctx.send('Informations have been successfully updated ! These informations can be changed at any moment by using the command /settings !',ephemeral=True)
            return
        
        
        await ctx.send("Okay, it's really you, you can now use your Sycash account freely!",ephemeral=True)
        db_manage.log(4,id,"logged in")
    else:
        await ctx.send("Bad OTP,try again !",ephemeral=True)
        db_manage.log(5,id,"failed otp")

@bot.command(name="balance", description="Get balance value.")
async def balance(ctx: CommandContext):
    if not isVerified(str(ctx.author.id)):
        await ctx.send("Your account isn't verified.",ephemeral=True)
        return
    bal=db_manage.get_user_bal(str(ctx.author.id))
    await ctx.send("```ansi\n\u001b[1;34m"+str(bal)+" EU```",ephemeral=True)

@bot.command(name="withdraw", description="Convert your Sycash credit in EUR")
async def withdraw(ctx: CommandContext):
    if not isVerified(str(ctx.author.id)):
        await ctx.send("Your account isn't verified.",ephemeral=True)
        return
    wd_menu = SelectMenu(
        custom_id="wd-menu",
        options=[
            SelectOption(label="Paypal", value="paypal"),
            SelectOption(label="Bank transfer", value="bank"),
            SelectOption(label="Crypto", value="crypto")
        ],
        placeholder="Choose your payment method",
        min_values=1,
        max_values=1,
    )
    await ctx.send("", components=wd_menu,ephemeral=True)
    db_manage.log(7,str(ctx.author.id),"withdraw try")

@bot.command(name="add_money", description="Add Sycash credit.")
async def add(ctx: CommandContext):
    if str(ctx.author.id) in handshake:
        await ctx.send('Vous avez déja un lien de paiement actif, veuillez passer par celui ci.',ephemeral=True)
        return
    if not isVerified(str(ctx.author.id)):
        await ctx.send("Your account isn't verified.",ephemeral=True)
        return
    add_menu = SelectMenu(
        custom_id="add-menu",
        options=[
            SelectOption(label="Paypal", value="paypal"),
            SelectOption(label="Bank transfer", value="bank"),
            SelectOption(label="Crypto", value="crypto")
        ],
        placeholder="Choose your payment method",
        min_values=1,
        max_values=1,
    )
    await ctx.send("", components=add_menu,ephemeral=True)
    


@bot.command(name="register", description="Register to Sycash.")
async def send_button(ctx: CommandContext):
    if db_manage.exist(str(ctx.author.id)):
        await ctx.send('```ansi\n\u001b[1;31m❌ You already have a Sycash account.```',ephemeral=True)
    else:
    
        modal = Modal(
            custom_id="modal-register",
            title="Register to Sycash",
            components=[

                TextInput(
                    style=TextStyleType.SHORT,
                    label="Entrez votre adresse email",
                    placeholder="Mail",
                    custom_id="reg-mail"
                
                )
            ],
        )

interactions.api.models.member.Member()

@bot.command(name="pay", description="Send money to sycash user",options = [interactions.Option(name="user",description="Tag of the recipient",type=interactions.OptionType.USER,required=True),interactions.Option(name="amount",description="Amount to send",type=interactions.OptionType.INTEGER,required=True)])
async def pay(ctx,user,amount):
    rec_id=str(user.id)
    sender_id=str(ctx.author.id)
    if not db_manage.valid_session(sender_id):
        await ctx.send('Hmmm, it seems that your connection session has expired, an email has been sent to you to extend your session.',ephemeral=True)
        generate_regmail(db_manage.get(sender_id)["mail"],sender_id,1)
        return
    if not db_manage.get(rec_id):
        await ctx.send("Hmmm, it looks like the user you are trying to send money to is not on Sycash, how about inviting him to Sycash ?",ephemeral=True)
        return
    if int(db_manage.get_user_bal(sender_id)) < amount:
        await ctx.send("Hmmm, it seems that you don't have enough money to make this transfer, please fund your Sycash account first !",ephemeral=True)
    else:
        db_manage.ret_to_bal(sender_id,amount)
        db_manage.add_to_bal(rec_id,amount)
        await ctx.send(str(amount)+' EU were successfully sent to '+str(user)+'.',ephemeral=True)
        await user.send("```ansi\n\u001b[1;34m💰 "+str(ctx.author)+" sent you "+str(amount)+' EU.```')
        db_manage.log(0,sender_id,str(amount)+" eu sent to "+str(user))
        db_manage.log(1,rec_id,str(amount)+" eu received from "+str(ctx.author))



@bot.command(name="settings", description="Displays your account settings.")
async def infos(ctx):
    id=str(ctx.author.id)
    mail=db_manage.get(id)['mail']
    ppl=db_manage.get(id)['paypal']
    iban=db_manage.get(id)['iban']
    btc=db_manage.get(id)['btc_addr']
    modal_i = Modal(
                custom_id="infos",
                title="Fill your withdrawal informations.",
                components=[TextInput(
                        style=TextStyleType.SHORT,
                        label="Paypal account email",
                        value=ppl,
                        custom_id="ppl",required=False),TextInput(
                        style=TextStyleType.SHORT,
                        label="IBAN",
                        value=iban,
                        custom_id="iban",required=False),TextInput(
                        style=TextStyleType.SHORT,
                        label="BTC address",
                        value=btc,
                        custom_id="btc",required=False),TextInput(
                        style=TextStyleType.SHORT,
                        label="Account email",
                        value=mail,
                        custom_id="mail",required=False)])
    await ctx.popup(modal_i)
#############################################################################

def isValid(email):
    if re.fullmatch(regex, email):
        return True
    return False
def isVerified(id):
    if db_manage.get_verif_state(id)=="1":
        return True
    return False

def send_mail(dest,sujet,content):
    msg = email.message.EmailMessage()
    msg.add_header('Content-Type','text/html')
    msg.set_payload(content)
    msg['Subject'] = sujet
    msg['From'] =  formataddr(('Sycash', 'YOUR_ADDRESS'))
    msg['To'] = dest
    server = smtplib.SMTP('smtp.ionos.fr', 587)
    server.starttls()
    server.login("YOUR_ADDRESS", "YOUR_PWD")
    server.send_message(msg)
    server.quit()

def generate_regmail(dest,id,context):
    c=open("./html/mail_template.html","r").read()
    if context==0:
        otp=str(random.randint(111111,999999))
    elif context==1:
        otp=str(random.randint(11111,99999))
    elif context==2:
        otp=str(random.randint(1111111,9999999))
    verif_pool.append({id:otp})
    c=c.replace('%REM%',"/verify "+otp)
    send_mail(dest,"Confirm your Sycash account",c)
    print('mail sent')

#############################################################################

@bot.modal("ret_paypal")
async def modal(ctx: CommandContext, ret_val):
    bal=db_manage.get_user_bal(str(ctx.author.id))
    if int(ret_val)>int(bal):
        await ctx.send('```ansi\n\u001b[1;31m❌ Not enough funds to make this withdrawal.```',ephemeral=True)
    else:
        #send_money()
        await ctx.send("""```ansi\n\u001b[1;34m✅ Thank you for your fidelity, """+ret_val+""" EU will be sent to your account in less than 1 day.```""",ephemeral=True)

@bot.modal("infos")
async def modal(ctx: CommandContext, paypal,bank,btc,*args):
    id=str(ctx.author.id)
    i=db_manage.get(id)
    if len(args)==1:
        if not (paypal,bank,btc,*args)==(i['paypal'],i['iban'],i['btc_addr'],i['mail']):
            actions_pool.append({"900141001916678214":{"mail":args,"paypal":paypal,"iban":bank,"btc":btc}})
            generate_regmail(i['mail'],id,2)
            await ctx.send('We need to verify your email before modifying these informations, an email has been sent with all the instructions.',ephemeral=True)
            return

    db_manage.log(2,id,"infos updated")
    await ctx.send('Informations have been successfully updated ! These informations can be changed at any moment by using the command /settings !',ephemeral=True)


@bot.modal("ret_bank")
async def modal(ctx: CommandContext, ret_val):
    bal=db_manage.get_user_bal(str(ctx.author.id))
    if int(ret_val)>int(bal):
        await ctx.send('```ansi\n\u001b[1;31m❌ Not enough funds to make this withdrawal.```',ephemeral=True)
    else:
        #send_money()
        await ctx.send("""```ansi\n\u001b[1;34m✅ Thank you for your fidelity, """+ret_val+""" EU will be sent to your account in less than 1 day.```""",ephemeral=True)

@bot.modal("ret_crypto")
async def modal(ctx: CommandContext, ret_val):
    bal=db_manage.get_user_bal(str(ctx.author.id))
    if int(ret_val)>int(bal):
        await ctx.send('```ansi\n\u001b[1;31m❌ Not enough funds to make this withdrawal.```',ephemeral=True)
    else:
        #send_money()
        await ctx.send("""```ansi\n\u001b[1;34m✅ Thank you for your fidelity, """+ret_val+""" EU will be sent to your account in less than 1 day.```""",ephemeral=True)

@bot.modal("add_bank")
async def modal_add(ctx: CommandContext, amount: str):
    id=str(ctx.author.id)
    c=0
    state=0
    if id in handshake:
        ctx.send('Vous avez déja un lien de paiement actif, veuillez passer par celui ci.',ephemeral=True)
        return
    else:
        handshake.append(id)
    await ctx.send("To proceed to payment, click [here]("+sypay.create_checkout(int(amount),id)+")",ephemeral=True)
    while id in handshake:
        if c>=1800:
            state=1
            ctx.send("Lien expiré",ephemeral=True)
            while id in handshake:
                handshake.remove(id)
            break
        c+=1
        await asyncio.sleep(1)
    if state==0:
        await ctx.send("```ansi\n\u001b[1;34m"+amount+" EU has been added to your balance !```",ephemeral=True)
        db_manage.log(6,id,amount+" EU added")
@bot.modal("add_paypal")
async def modal_add(ctx: CommandContext, amount: str):
    id=str(ctx.author.id)
    c=0
    state=0
    if id in handshake:
        await ctx.send('Vous avez déja un lien de paiement actif, veuillez passer par celui ci.',ephemeral=True)
        return
    else:
        handshake.append(id)
    await ctx.send("To proceed to payment, click [here]("+sypay.create_checkout_paypal(id,amount)+")",ephemeral=True)
    while id in handshake:
        if c>=1800:
            state=1
            ctx.send("Lien expiré",ephemeral=True)
            while id in handshake:
                handshake.remove(id)
            break
        c+=1
        await asyncio.sleep(1)
    if state==0:
        await ctx.send(amount+" EU has been added to your balance !",ephemeral=True)
        db_manage.log(6,id,amount+" EU added")
@bot.modal("add_crypto")
async def modal_add(ctx: CommandContext, amount: str):
    id=str(ctx.author.id)
    c=0
    state=0
    if id in handshake:
        await ctx.send('Vous avez déja un lien de paiement actif, veuillez passer par celui ci.',ephemeral=True)
        return
    else:
        handshake.append(id)
    await ctx.send("To proceed to payment, click [here]("+sypay.create_checkout_crypto(id,amount)+")",ephemeral=True)
    while id in handshake:
        if c>=1800:
            state=1
            ctx.send("Lien expiré",ephemeral=True)
            while id in handshake:
                handshake.remove(id)
            break
        c+=1
        await asyncio.sleep(1)
    if state==0:
        await ctx.send(amount+" EU has been added to your balance !",ephemeral=True)
        db_manage.log(6,id,amount+" EU added")

@bot.modal("modal-register")
async def register_user(ctx: CommandContext,mail):
    id=str(ctx.author.id)
    if isValid(mail):
        deja=db_manage.mail_used(mail)
        print(deja)
        if deja:
            await ctx.send('```ansi\n\u001b[1;31m❌ This email address is already used for another Sycash account.```',ephemeral=True)
        else:
            db_manage.create_user(str(ctx.author.id),mail)
            generate_regmail(mail,id,0)
            await ctx.send('```ansi\n\u001b[1;34m✅ Thank you, '+str(ctx.author)+' ! We have sent you an email to '+mail+' to finish setting up your Sycash account.```',ephemeral=True)
            db_manage.log(3,id,"registered")
    else:
        await ctx.send("```ansi\n\u001b[1;31m❌ Invalid email address, try again.```",ephemeral=True)


import threading

t=threading.Thread(target=run_flask)
t.start()
bot.start()

