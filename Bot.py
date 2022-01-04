# !/usr/bin/env python
# -*- coding: utf-8 -*-

# tools.staticdir.root = "E:/Dropbox/Knowledge/CS/Ariel/My-courses/Y3/S2/Final-project/The_project"
# tools.staticdir.root = "C:/Users/Me/Dropbox/Knowledge/CS/Ariel/My-courses/Y3/S2/Final-project/The_project"


from telegram.ext import Updater, MessageHandler, Filters
from pymodules import Admin, Group, CredsManager

LINK_TO_WEB_UI = "https://127.0.0.1"
BOT_TOKEN = "631236712:AAHrd7Wzq3xsJh_n6bS4nrwbV0hdw9ZoN1k"
HELP_CMD = "This bot is intended to keep your groups spam free. In the beginning" \
           " you and other authorized users in the" \
           " group label messages as spam or not spam." \
           "\r\n\r\n" \
           "When there is enough messages labeled you can activate the bot" \
           " and it will remove spam messages based on the messages you have labeled. You can always label spam" \
           " messages the bot missed to improve it." \
           "\r\n\r\nTo start using the bot add it" \
           " with admin privileges to your supergroup (it must be a supergroup)," \
           " then when there is a new message label it for the bot:" \
           " reply to it with the text \"0\" if it's not spam" \
           " and \"1\" if it's spam. The more you label for the bot the more accurate it becomes in identifying spam." \
           " If you labeled a message as spam (meaning you replied with \"1\")" \
           " the bot will also remove" \
           " the message. Anyway the bot removes your label message " \
           "(the \"0\" or the \"1\" because it's intended only" \
           " for him).\r\n\r\n" \
           "By default the bot doesn't" \
           " remove automatically spam messages, you need to activate it for every group separately. \r\n" \
           "You should activate the automatic spam removal only when you labeled about hundreds of spam and good " \
           "messages." \
           "To edit the settings of a group, such as activating spam removal and " \
           "editing and viewing your labeled messages" \
           " you have to access the following link: " + LINK_TO_WEB_UI + "." \
           "\r\n\r\nLogin with your Telegram username and the last password you got from the command \"/genpw\"."


def is_bot_added_to_new_group(msg, bot, chat_id):
    return len(msg.new_chat_members) == 1 and msg.new_chat_members[0].id == bot.getMe().id \
           and not Group.is_group_exists(chat_id)


def get_group_creator_un(bot, chat_id):
    return [str(us.user.id) for us in bot.getChatAdministrators(chat_id=chat_id) if us.status == "creator"][0]


def private_chat_with_bot(bot, update):
    # Prepare all the variables from the API
    msg = update.message
    chat_id = msg.chat.id
    msg_txt = msg.text
    msg_sender = msg.from_user
    if msg_txt == "/help" or msg_txt == "/start":
        bot.sendMessage(text=HELP_CMD, chat_id=chat_id)
    elif msg_txt == "/genpw":
        if not Admin.is_admin_exists(msg_sender.username):
            bot.sendMessage(text="You haven't added the bot to any of the groups you created.", chat_id=chat_id)
        else:
            rand_pw = CredsManager.get_rand_letters_nums()
            Admin.Admin(msg_sender.username).update_pw(rand_pw)
            bot.sendMessage(text="Your new credentials to login to the web management platform:\r\n\r\n" +
                                 "Username:" + msg_sender.username + "\r\nPassword:" + rand_pw + "\r\n\r\n" +
                                 LINK_TO_WEB_UI + "\r\n/help for more information.", chat_id=chat_id)


def bot_worker(bot, update):
    # Prepare all the variables from the API
    msg = update.message
    chat_id = msg.chat.id
    msg_txt = msg.text
    msg_id = msg.message_id
    msg_sender = msg.from_user
    msg_hour = msg.date.strftime('%H')
    if chat_id == msg_sender.id:
        """====================
        ==== Bot is in a private chat ====
        ===================="""
        private_chat_with_bot(bot, update)
    elif is_bot_added_to_new_group(msg, bot, chat_id):
        """====================
        ==== Bot is added to a new group ====
        ===================="""
        creator_username = get_group_creator_un(bot, chat_id)
        Admin.add_group_to_creator(chat_id, creator_username)
        Group.add_group(chat_id, creator_username)
    else:
        """====================
        ==== Bot received a messages in one of the groups it's in ====
        ===================="""
        cur_chat = Group.Group(chat_id)
        replied_msg = msg.reply_to_message
        if replied_msg is not None and cur_chat.is_authorized(str(msg_sender.id)) and msg_txt in ["0", "1"]:
            replied_msg_hour = msg.reply_to_message.date.strftime('%H')
            if not cur_chat.is_auto_label() and msg_txt == "0" or msg_txt == "1":
                cur_chat.add_new_msg(
                    replied_msg_hour, replied_msg.from_user.username + " " + replied_msg.text, msg_txt)
                bot.deleteMessage(chat_id=chat_id, message_id=msg_id)
                if msg_txt == "1":
                    bot.deleteMessage(chat_id=chat_id, message_id=msg.reply_to_message.message_id)
        elif cur_chat.is_remove_activated() and cur_chat.is_spam(msg=msg_txt, time=msg_hour):
            bot.deleteMessage(chat_id=chat_id, message_id=msg_id)
        elif cur_chat.is_auto_label():
            cur_chat.add_new_msg(msg_hour, str(msg_sender.id) + " " + msg_txt, "0")


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.all, bot_worker))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
