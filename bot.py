import json
import discord
import inspect
from discord.ext import commands
from collections import defaultdict

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

# Test
@bot.command()
async def test(cfx, arg=None):
    await cfx.send(arg if arg else 'You don\'t talk. I\'m sad.')

# Add bets
@bot.command()
async def bet(cfx, *args):
    if not bot.started:
        await cfx.send('還沒開始，別急')
        return

    if len(args) not in [1, 2]:
        await cfx.send('參數數量不對，回復上一動')
        return

    member, bet_ = (cfx.author, args[0]) if len(args) == 1 else (args[0], args[1])

    # Deal with bet_
    try:
        bet_ = eval(bet_)
    except:
        await cfx.send('怪怪的餒')
        return
    
    if not isinstance(bet_, int):
        await cfx.send('這不是整數吧')
        return
    
    # Deal with member
    if member != cfx.author:
        try:
            member = await commands.MemberConverter().convert(cfx, member)
        except commands.MemberNotFound:
            await cfx.send('找不到這個人餒')
            return

    bot.pool[member] += int(bet_)
    await cfx.send(f'幫 {member.mention} 記下一筆 {bet_} 的紀錄 ~')


# Start a new game
# TODO: Add support of multiple channels. Kind of like the problem you faced at the graduate project
@bot.command()
async def start(cfx):
    bot.pool = defaultdict(lambda: 0)
    bot.started = True
    await cfx.send('來啊')

# End the current game
@bot.command()
async def end(cfx, *args):
    if len(args) == 1 and args[0] == '-f':
        await cfx.send('好ㄅ，強制清零')
    elif sum(bot.pool.values()) != 0:
        await cfx.send('還沒達到零和，有人不老實')
        return
    else:
        for member, bet_ in bot.pool.items():
            if bet_ > 0:
                message = f'{member.mention} 贏了 {bet_} 個籌碼'
            elif bet_ == 0:
                message = f'{member.mention} 沒輸沒贏'
            elif bet_ < 0:
                message = f'{member.mention} 輸了 {abs(bet_)} 個籌碼'
            await cfx.send(message)

    bot.pool.clear()
    bot.started = False

# Show the current balance
@bot.command()
async def status(cfx):
    if not bot.started:
        await cfx.send('還沒開始，別急')
        return

    if not bot.pool:
        await cfx.send('還沒有人開始玩。。。')
        return

    message = ''
    for member, bet_ in bot.pool.items():
        await cfx.send(f'{member.mention} 現在有 {bet_} 個籌碼\n')

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
    await cfx.send(message)

if __name__ == '__main__':
    bot.run(data['token'])
    