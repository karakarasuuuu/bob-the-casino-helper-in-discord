import json
import discord
import inspect
from discord.ext import commands
from collections import defaultdict


# Setting

# Get the token
with open('items.json', 'r', encoding='utf8') as file:
    data = json.load(file)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)
bot.started = False

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    # Change the status
    # TODO: Use *status* instead of *Game*
    status = discord.Game('手上的籌碼')
    await bot.change_presence(activity=status)

    # Some initial settings
    bot.pools = defaultdict(dict)
    bot.game_status = defaultdict(lambda: False)

# Test
@bot.command()
async def test(cfx, arg=None):
    await cfx.reply(arg if arg else 'You don\'t talk. I\'m sad.')



# Commands

# Add bets
@bot.command()
async def bet(cfx, *args):
    if not bot.game_status[id(cfx.channel)]:
        await cfx.reply('還沒開始，別急')
        return

    if len(args) not in [1, 2]:
        await cfx.reply('參數數量不對，回復上一動')
        return

    # If there is no user mentioned
    # Then this record belongs to the author
    member, bet_ = (cfx.author, args[0]) if len(args) == 1 else (args[0], args[1])

    # Deal with bet_
    try:
        bet_ = eval(bet_)
    except:
        await cfx.reply('怪怪的餒')
        return
    
    if not isinstance(bet_, int):
        await cfx.reply('這不是整數吧')
        return
    
    # Deal with member
    if member != cfx.author:
        try:
            member = await commands.MemberConverter().convert(cfx, member)
        except commands.MemberNotFound:
            await cfx.reply('找不到這個人餒')
            return

    bot.pools[id(cfx.channel)][member] += int(bet_)
    await cfx.reply(f'幫 {member.mention} 記下一筆*{"贏" if bet_ > 0 else "輸"} {abs(bet_)}* 個籌碼的紀錄 ~')

# Start a new game
# TODO: Add support of multiple channels. Kind of like the problem you faced at the graduate project
@bot.command()
async def start(cfx):
    # If the game is started already, then it should do nothing instead
    if bot.game_status[id(cfx.channel)]:
        await cfx.reply('已經開始了==')
        return

    bot.pools[id(cfx.channel)] = defaultdict(lambda: 0)
    bot.game_status[id(cfx.channel)] = True
    await cfx.reply('來啊')

# End the current game
@bot.command()
async def end(cfx, *args):
    # If the game isn't started yet, then it should do nothing instead
    if not bot.game_status[id(cfx.channel)]:
        await cfx.reply('還沒開始要怎麼結束')
        return
    
    # Force end
    if len(args) == 1 and args[0] == '-f':
        await cfx.reply('好ㄅ，強制清零')
    
    # It isn't zero-sum yet
    elif sum(bot.pools[id(cfx.channel)].values()) != 0:
        await cfx.reply('還沒達到零和，有人不老實')
        return
    else:
        await status(cfx)

    # Clear the pool
    bot.pools[id(cfx.channel)].clear()
    bot.game_status[id(cfx.channel)] = False

# Show the current balance
@bot.command()
async def status(cfx):
    # If the game isn't started, then there will not be any status
    if not bot.game_status[id(cfx.channel)]:
        await cfx.reply('還沒開始，別急')
        return

    # Even if the game is started, it does not make any sense to show the status if nobody has inputted something
    if not bot.pools[id(cfx.channel)]:
        await cfx.reply('還沒有人開始玩。。。')
        return

    for member, bet_ in bot.pools[id(cfx.channel)].items():
        if bet_ > 0:
            message = f'{member.mention} 贏了 {bet_} 個籌碼'
        elif bet_ == 0:
            message = f'{member.mention} 沒輸沒贏'
        elif bet_ < 0:
            message = f'{member.mention} 輸了 {abs(bet_)} 個籌碼'
        await cfx.reply(message)

# Help message
@bot.command()
async def help(cfx):
    message = inspect.cleandoc( # Use it to clean the blanks on the left
        '''
        **$help**: 顯示此幫助訊息
        **$start**: 開始一場賽局
        **$bet** *[標別人可以幫別人輸入]* *<籌碼數量>*: 輸入籌碼
        **$end** *[-f]*: 結束一場賽局。附上參數 `-f` 則強制結束（不論結果）
        **$status**: 查看當前的情況
        ''')
    await cfx.reply(message)



# Main process
if __name__ == '__main__':
    bot.run(data['token'])
    