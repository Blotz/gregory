import discord
from discord.ext import commands
from discord.utils import get
from converter.datetimeCalc import datetimeCal
from sql.pollv2 import sql_class
import re
# await discord.utils.sleep_until(when, result=None)
class poll(commands.Cog):
    '''
    super fancy shmancy poll command
    '''
    def __init__(self, client):
        self.client = client
        self.pollsigns = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯","🇰","🇱","🇲","🇳","🇴","🇵","🇶","🇷","🇸","🇹","🇺","🇻","🇼","🇽","🇾","🇿"]
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        toggles the voting option for this poll
        """
        message_id = str(payload.message_id)
        channel_id = str(payload.channel_id)
        guild_id = str(payload.guild_id)   
        user_id = str(payload.user_id)
        
        # breaks if its the bot
        if user_id == '785578758450708492':
            return
        
        if payload.emoji.name not in self.pollsigns:
            return

        # if it has an id, its not one of the abcdef emotes
        if payload.emoji.name in self.pollsigns:
            emote_id = str(ord(payload.emoji.name))
            sql = sql_class()
            toggle = sql.toggle_vote(message_id, channel_id, guild_id, emote_id, user_id)

            if toggle == False or toggle == True:
                channel = self.client.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                await message.remove_reaction(payload.emoji, payload.member)


    @commands.command(aliases=['poll2electricboogaloo','poll'])
    async def poll2(self, ctx, time: datetimeCal, *, args):
        """
        .poll2 7d2h {who do you want to vote lol?} [arg1] [arg2]
        """
        # checks message against regex to see if it matches
        reg = re.compile('({.+})\ *(\[[^\n\r\[\]]+\] *)+')
        if not reg.match(args):
            raise discord.errors.DiscordException

        # fomatting of arguments in message
        args = args.split('[')
        name = args.pop(0)[1:]
        name = name[:name.find('}')]
        
        args = [arg[:arg.find(']')] for arg in args] # thanks ritz for this line

        if len(args) > 20:
            await ctx.send(f"bad {ctx.author.name}! thats too much polling >:(")
            return
        elif len(args) == 0:
            await ctx.send(f"bad {ctx.author.name}! thats too little polling >:(")
            return
        elif name == '' or '' in args:
            await ctx.send(f"bad {ctx.author.name}! thats too simplistic polling >:(")
            return


        # creating embed for poll
        description = ''
        for count in range(len(args)):
            description += self.pollsigns[count] + ' ' + args[count] + '\n\n'

        embed = discord.Embed(title=name,color=discord.Color.green(),description=description)
        message = await ctx.send(embed=embed)

        #add reactions
        for count in range(len(args)):
            await message.add_reaction(self.pollsigns[count])

        sql = sql_class()   
        sql.add_poll(str(message.id), str(message.channel.id), str(message.author.guild.id), name, time, self.pollsigns, args)

    @poll2.error
    async def reload_error(self, ctx, error):
        # error if cog doesnt exist
        if isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(error, discord.errors.DiscordException):
            await ctx.send('`ERROR Missing Required Argument: make sure it is .poll2 <time MMWWDDhhmmss> {title} [args]`')
        else:
            print(error)
    
    @commands.command(aliases=['checkvotes'])
    async def check_votes(self, ctx):
        '''
        allows the user to check who they voted for
        '''
        sql = sql_class()
        data = sql.check_polls(str(ctx.author.id))
        # removes duplicate polls from data
        data = list(dict.fromkeys(data))
        
        if len(data) == 0:
            await ctx.send('You havent voted on any active polls')
        elif len(data) == 1:
            votes = sql.check_votes(str(ctx.author.id), data[0][0])
            await ctx.author.send(embed=self._sendvoted(votes))
        else:
            pass

        # await ctx.author.send('👋')

    def _sendvoted(self, votes):
        description = 'You have voted: \n\n'
        for vote in votes:
            description += vote[0] + '\n'
        
        embed = discord.Embed(title='on poll "'+votes[0][1]+'"',color=discord.Color.green(),description=description)
        return embed

def setup(client):
    client.add_cog(poll(client))