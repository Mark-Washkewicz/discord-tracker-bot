#ID-664976297230991410
#token-NjY0OTc2Mjk3MjMwOTkxNDEw.Xhe5mA.xSXC2dcBsihp4ohxATDFzwn5PzE
#permisions integer-67648
#https://discordapp.com/oauth2/authorize?client_id=664976297230991410&scope=bot&permissions=67648

import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import time
import asyncio
import pandas as pd
import sqlite3
from sqlite3 import Error
from sqlalchemy import create_engine
from vars import TOKEN


# TOKEN = 'NjY0OTc2Mjk3MjMwOTkxNDEw.Xhe5mA.xSXC2dcBsihp4ohxATDFzwn5PzE'
BOT_PREFIX = '!!'

user_dict  = {}
bot = commands.Bot(command_prefix=BOT_PREFIX)


@bot.event        
async def on_ready():
    print('logged in as :' +bot.user.name +'\n')
    discord.VoiceChannel


@bot.event
async def on_voice_state_update(user, before, after):
        print(f'{user}\n {before} \n {after}')
        num_mems = 0
        #print(user.guild.afk_channel)



        global user_dict
        if str(before.channel) == 'None' and str(after.channel) != 'None':
            
            user_dict[user.id] = datetime.now()
            #print(user_dict)
            print(1)
            #add to dict
        elif before.channel != after.channel and str(after.channel) != 'None':
            try:
                time_in = user_dict.pop(user.id)
                user_dict[user.id] = datetime.now()
                time_out = datetime.now()
                delta_time = time_out-time_in
                

                
                for mems in before.channel.members:
                    if not mems.bot:
                        num_mems += 1

                        
                #pop dict
                df = pd.DataFrame({'username':user.name, 'user_id':user.id, 'channel': str(before.channel), 'num_mems':num_mems, 'deafen':before.self_deaf, 'mute': before.self_mute, 'time_in': time_in , 'time_out':time_out, 'delta_time':delta_time.total_seconds()}, index = [0])
                
                #print(df.head())

                conn = sqlite3.connect('discord_track.db')
                df.to_sql(name='discord_track.db', con = conn, index = False, if_exists='append')
            except:
                #print('fail')
                user_dict[user.id] = datetime.now()

            print(2)
            #move to db and add new to dict
        elif str(after.channel) =='None':
            try:
                time_in = user_dict.pop(user.id)
                time_out = datetime.now()
                delta_time = time_out-time_in

                
                for mems in before.channel.members:
                    if not mems.bot:
                        num_mems += 1

                #pop dict
                df = pd.DataFrame({'username':user.name, 'user_id':user.id, 'channel': str(before.channel), 'num_mems':num_mems, 'deafen':before.self_deaf, 'mute': before.self_mute, 'time_in': time_in , 'time_out':time_out, 'delta_time':delta_time.total_seconds()}, index = [0])
                
               # print(df.head)

                conn = sqlite3.connect('discord_track.db')
                df.to_sql(name='discord_track.db', con = conn, index = False, if_exists='append')

            except:
                user_dict[user.id] = datetime.now()
                print('fail')
            #move to db

                print(3)
        #good
        elif (after.self_mute==False and after.self_deaf==False) and (before.self_mute==True or before.self_deaf == True):
            #add them to dict 
            try:
                time_in = user_dict.pop(user.id)
                user_dict[user.id] = datetime.now()
                time_out = datetime.now()
                delta_time = time_out-time_in

                
                for mems in before.channel.members:
                    if not mems.bot:
                        num_mems += 1

                df = pd.DataFrame({'username':user.name, 'user_id':user.id, 'channel': str(before.channel), 'num_mems':num_mems, 'deafen':before.self_deaf, 'mute': before.self_mute, 'time_in': time_in , 'time_out':time_out, 'delta_time':delta_time.total_seconds()}, index = [0])
                    
                #print(df.head)

                conn = sqlite3.connect('discord_track.db')
                df.to_sql(name='discord_track.db', con = conn, index = False, if_exists='append')
            except:
                user_dict[user.id] = datetime.now()
                print('fail')

        
        elif (before.self_mute==False and before.self_deaf==False) and (after.self_mute == True or after.self_deaf == True):
            #move from dict to df
            try:
                time_in = user_dict.pop(user.id)
                user_dict[user.id] = datetime.now()
                time_out = datetime.now()
                delta_time = time_out-time_in


                for mems in before.channel.members:
                    if not mems.bot:
                        num_mems += 1

                df = pd.DataFrame({'username':user.name, 'user_id':user.id, 'channel': str(before.channel), 'num_mems':num_mems, 'deafen':before.self_deaf, 'mute': before.self_mute, 'time_in': time_in , 'time_out':time_out, 'delta_time':delta_time.total_seconds()}, index = [0])
                    
                #print(df.head)

                conn = sqlite3.connect('discord_track.db')
                df.to_sql(name='discord_track.db', con = conn, index = False, if_exists='append')
            except:
                user_dict[user.id] = datetime.now()
                print('fail')

@bot.command(pass_context = True)
async def data(ctx):
    await(update(ctx))
    channel = ctx.message.channel

    df1 = pd.read_sql('''SELECT username,
        user_id,
        channel,
        num_mems,
        deafen,
        mute,
        time_in,
        time_out,
        delta_time
        FROM [discord_track.db];''', con = sqlite3.connect('discord_track.db'))


    df_usernames = df1[['username', 'user_id']]
    df_usernames = df_usernames.drop_duplicates('user_id')

    df2 = df1.loc[(df1['channel']!=str(ctx.message.guild.afk_channel)) & (df1['deafen']== 0) & (df1['mute'] == 0) & (df1['num_mems']!=0) ] 
        
    df2 = df2[['delta_time', 'user_id']]
    df2 = df2.groupby(['user_id']).sum()

    df2 = df2.merge(df_usernames, left_on='user_id', right_on ='user_id')
    df2 = df2.sort_values(by=['delta_time'], ascending = False)
    out_string =''
    
    for index, row in df2.iterrows():
        out_string = out_string + row['username'] + ': ' + str     ('%.2f' %(row['delta_time']/60)) +' minutes\n'

    await channel.send(out_string) 



@bot.command(pass_context = True)
async def set(ctx): #voice_channel_id
    #First getting the voice channel object
    all_voice_channel = ctx.message.guild.voice_channels

    for voice_channels in all_voice_channel:
        for members in voice_channels.members:
                try:
                    user_dict[members.id]
                except:
                    user_dict[members.id] = datetime.now()

    #print(user_dict)
    

    await ctx.message.channel.send('voice chat members have been set!')



#@bot.command(pass_context = True)
async def update(ctx): #voice_channel_id
    #First getting the voice channel object
    all_voice_channel = ctx.message.guild.voice_channels

    for voice_channels in all_voice_channel:
        for members in voice_channels.members:
            try:
                time_in=user_dict.pop(members.id)
                user_dict[members.id] = datetime.now()
                time_out = datetime.now()
                delta_time = time_out-time_in

                df = pd.DataFrame({'username':members.name, 'user_id':members.id, 'channel': str(members.voice.channel), 'num_mems':num_mems, 'deafen':members.voice.self_deaf, 'mute': members.voice.self_mute, 'time_in': time_in , 'time_out':time_out, 'delta_time':delta_time.total_seconds()}, index = [0])

                conn = sqlite3.connect('discord_track.db')
                df.to_sql(name='discord_track.db', con = conn, index = False, if_exists='append')


            except:
                print('user not in dict')

            #print(members.id, members.voice )
    

    await ctx.message.channel.send('updated!')
    #return await bot.say(embed = embed)        

#client.loop.create_task(update_stats)
bot.run(TOKEN)

