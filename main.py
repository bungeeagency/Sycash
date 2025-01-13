from interactions import (
    Client,
    CommandContext,
    ComponentContext,
    Modal,
    TextInput,
    TextStyleType,
    Button,
)
import interactions

APIKEY = ""

bot = Client(APIKEY)

#############################################################################
@bot.event
async def on_ready():
    print("Ready!")
#############################################################################
class utils:
    def wd():
        w_p = Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Paypal",
            custom_id="paypal-w"
        )

        w_btc = Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Crypto",
            custom_id="btc-w"
        )
        w_bank = Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Bank transfer",
            custom_id="bank-w"
        )
        return [w_p,w_btc,w_bank]
    def add():

        a_p = Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Paypal",
            custom_id="paypal-a"
        )

        a_btc = Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Crypto",
            custom_id="btc-a"
        )
        a_bank = Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Bank transfer",
            custom_id="bank-a"
        )
        return [a_p,a_btc,a_bank]

    bal=100
#############################################################################

@bot.component("paypal-w")
async def with_paypal(ctx: CommandContext):
    await ctx.send('Your money was sent to your paypal account')

@bot.component("btc-w")
async def with_btc(ctx: CommandContext):
    await ctx.send('Your money was sent to your btc address')

@bot.component("bank-w")
async def with_bank(ctx: CommandContext):
    await ctx.send('Your money was sent to your bank account')
#############################################################################

@bot.component("paypal-a")
async def with_paypala(ctx: CommandContext):
    await ctx.send('Money successfully added to your account !')

@bot.component("btc-a")
async def with_btca(ctx: CommandContext):
    await ctx.send('Money successfully added to your account !')

@bot.component("bank-a")
async def with_banka(ctx: CommandContext):
    await ctx.send('Money successfully added to your account !')

#############################################################################

@bot.command(name="balance", description="Get balance value.")
async def balance(ctx: CommandContext):
    await ctx.send(utils.bal)

@bot.command(name="withdraw", description="Get balance value.")
async def withdraw(ctx: CommandContext):
    modal = Modal(
        custom_id="ret_modal",
        title="Withdrawal",
        components=[

            TextInput(
                style=TextStyleType.SHORT,
                label="Entrez le montant que vous voulez retirer",
                placeholder="Montant",
                custom_id="text-input-1",
                min_length=1,
                max_length=4,
            )
        ]
    )
    await ctx.popup(modal)

@bot.command(name="send-button", description="Send a button")
async def send_button(ctx: CommandContext):
    modal = Modal(
        custom_id="modal-add",
        title="Ajouter de l'argent a votre compte Sycash",
        components=[

            TextInput(
                style=TextStyleType.SHORT,
                label="Entrez le montant à ajouter",
                placeholder="Montant",
                custom_id="modal-add",
                min_length=1,
                max_length=4,
            )
        ],
    )
    await ctx.popup(modal)


#############################################################################

@bot.modal("ret_modal")
async def modal(ctx: CommandContext, ret_val):

    if int(ret_val)>utils.bal:
        await ctx.send('```ansi\n\u001b[1;31m❌ Not enough funds to make this withdrawal.```')
    else:
        await ctx.send("""```ansi\n\u001b[1;34m✅ Thank you for your fidelity, """+ret_val+""" EU will be sent to your account in less than 1 day.```""")


@bot.modal("modal-add")
async def modal_add(ctx: CommandContext, amount: str):
    await ctx.send(amount+" EU will be add to your Sycash account.")
    await ctx.send("Choose your payment method ", components=utils.add())
    
@bot.modal("modal2")
async def modal2(ctx: CommandContext, ret, add):
    print(ret,add)
    if int(ret)>utils.bal:
        await ctx.send("Votre solde est insuffisant pour retirer cette somme.")
    else:
        await ctx.send('Choose your withdrawal method',components=utils.wd())

    utils.bal+=int(add)

bot.start()