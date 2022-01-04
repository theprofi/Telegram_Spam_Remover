import cherrypy
from telegram.ext import Updater
from pymodules import Admin, Group, CredsManager
import socket

BOT = Updater("631236712:AAHrd7Wzq3xsJh_n6bS4nrwbV0hdw9ZoN1k").bot

"""==================================
HTML CODES OF ALL THE PAGES
=================================="""
# The page where the admin chooses the group to manage
HTML_OF_CHOOSE_GROUP = '''<html>
<head>
<link href="/web-files/style-others.css" rel="stylesheet" >
</head>
<body>
<div class="login">
<div class="login-screen">
<div class="app-title">
<h2>Hello, %(username)s<br>
Choose a group among the groups that you've created to edit it's settings:
</h2>
</div>

<div class="login-form">
%(groups_btns_html)s   
<br>
<form method="post" action="logout">
<div><a href="logout" style="text-decoration:underline;color:black;font-size:11px">logout</a></div>
</form>
</div>

</div>
</div>

</body>
</html>             
'''
HTML_OF_CHOOSE_GROUP_BTN = '''
<form method="post" action="manage">
<input type="text" name="chat_id" value="%s" hidden>
<input type="text" name="group_title" value="%s" hidden>
<input type="submit" value="%s" class="btn btn-primary btn-large btn-block" >
</form>
'''
HTML_OF_NO_GROUPS_CREATED = \
    "<span style=\"color:red\">You haven't added the bot to any of the groups you created</span><br>"
# The page where the admin logins
HTML_OF_LOGIN = '''
<html>
<head>
<link href="/web-files/style-login.css" rel="stylesheet" >
</head>
<body>
%(login_failed_html)s
<form action="index" method="POST">
<div class="login">
<div class="login-screen">
<div class="app-title">
<h2>Spam Remover<br>control panel</h2>
</div>

<div class="login-form">
<div class="control-group">
<input type="text" class="login-field" value="" placeholder="username" name="username">
<label class="login-field-icon fui-user" for="login-name"></label>
</div>

<div class="control-group">
<input type="password" class="login-field" value="" placeholder="password" name="password">
<label class="login-field-icon fui-lock" for="login-pass"></label>
</div>

<input type="submit" value="Log in" class="btn btn-primary btn-large btn-block" >
<br>
</div>
</div>
</div>
</form>
</body>
</html>
            '''
HTML_OF_LOGIN_FAILED = '<div class=\"login\"><div class=\"login-screen\">' \
                       '<div class=\"app-title\"><center style=\"color:red\"><strong>' \
                       'Failed login attempt</strong></center></div></div>'
# Error page
HTML_OF_ERROR = '''<center style="color:white"><strong>Some error occured.
You was redirected to the login page</strong></center>'''
# The page to manage a group
HTML_OF_MANAGE = ''' 
<html> 
<head>
<link href="/web-files/style-others.css" rel="stylesheet" >
</head>
	<div class="login">
		<div class="login-screen">
			<div class="app-title">
			<center>
            <h1 style="color:black">Edit settings for the group "<span style="color:#3498DB">%(group_title)s
            </span>"</h1>
            <form action="manage" method="POST">
            <input type="submit" value="Save all changes" class="btn" />
            <br>
            <div><a href="choose_group" style="text-decoration:underline;color:black;font-size:11px">
            back to group choice</a></div></center></div></div></div>
            
            </div></div></div>
            <div class="login">
		<div class="login-screen">
			<div class="app-title">
            <h3>Toggle spam removal in the group<br></h3>
            
            <input type="text" name="chat_id" value="%(chat_id)s" hidden>
            <input type="text" name="group_title" value="%(group_title)s" hidden>
            %(radio_of_status)s<br><div style="font-size:12px">
            To make the automatic spam removal effective there should be at least 
            hundreds of spam and good message labeled</style>
            </div></div></div>
            
            
            <div class="login">
		<div class="login-screen">
			<div class="app-title">
            <h3>Toggle auto label of good messages in the group<br></h3>
            
            %(radio_of_auto_label)s<br><div style="font-size:12px">
            All the messages, except for those identified as spam and those you label as spam 
            will be labeled as good messages</style>
            </div></div></div>
            
            
            <div class="login">
		<div class="login-screen">
			<div class="app-title">
            <h3>Edit the database of the group</h3>
            </center>
            <table style="width:100%%">
                <tr style="width:100%%">
                <td style="font-size:1em;color:#777">
                Good messages (%(good_amount)s):
                
                </td>
                <td style="font-size:1em;color:#777">
                Spam messages (%(spam_amount)s):
                </td>
                </tr>
                <tr style="width:100%%">
                    <td>
                            <textarea type="text" name="new_data_good" 
                                style="height:500px;resize:vertical;width:100%%">%(good)s</textarea>
                    </td>

                    <td>
                        <textarea type="text" name="new_data_spam" 
                            style="height:500px;resize:vertical;width:100%%">%(spam)s</textarea>
                    </td>
                </tr>
            </table>
            <center>
            </form></body></html>
                    '''
HTML_OF_RADIO_TURNOFF_CHECKED = '''
       <input type = "radio" name = "rem_status" value = "Turn off" checked> Turn off (current status)</input>
           <input type = "radio" name = "rem_status" value = "Turn on"> Turn on</input>'''
HTML_OF_RADIO_TURNON_CHECKED = '''
               <input type = "radio" name = "rem_status" value = "Turn off">Turn off</input>
                   <input type = "radio" name = "rem_status" value = "Turn on" checked>Turn on (current status)</input>'''
HTML_OF_RADIO_TURNON_AUTOLABEL_CHECKED = '''
               <input type = "radio" name = "auto_label_status" value = "Turn off">Turn off</input>
                   <input type = "radio" name = "auto_label_status" value = "Turn on" checked>Turn on (current status)</input>'''
HTML_OF_RADIO_TURNOFF_AUTOLABEL_CHECKED = '''
       <input type = "radio" name = "auto_label_status" value = "Turn off" checked> Turn off (current status)</input>
           <input type = "radio" name = "auto_label_status" value = "Turn on"> Turn on</input>'''


class WebInterface(object):
    @cherrypy.expose
    def index(self, username=None, password=None):
        # Check if the user is logged in
        username_from_sess = cherrypy.session.get('username', None)
        if username_from_sess is not None:
            raise cherrypy.HTTPRedirect('choose_group')
        # Do a login
        if username is not None and CredsManager.verify_entered_creds(username, password):
            cherrypy.session['username'] = username
            raise cherrypy.HTTPRedirect('choose_group')
        # Show the login page
        elif username is None:
            return HTML_OF_LOGIN % {"login_failed_html": ""}
        # Show the login page with error
        else:
            return HTML_OF_LOGIN % {"login_failed_html": HTML_OF_LOGIN_FAILED}

    @cherrypy.expose
    def default(self, *args):
        # Show the login page with an error message above
        return HTML_OF_ERROR + self.index()

    @cherrypy.expose
    def logout(self):
        # Delete the session cookie and show the login page
        cherrypy.session.delete()
        raise cherrypy.HTTPRedirect('index')

    @cherrypy.expose
    def manage(self, new_data_good=None, new_data_spam=None, chat_id=None, group_title=None, rem_status=None,
               auto_label_status=None):
        # Check if the user is logged in
        username = cherrypy.session.get('username', None)
        if username is None:
            return HTML_OF_ERROR + self.logout()
        # Verify we know which group the user wants to edit
        if chat_id is None or group_title is None:
            raise cherrypy.HTTPRedirect('choose_group')
        cur_group = Group.Group(chat_id)
        '''==================
        Change the settings by users input 
        =================='''
        # If the user changed the data base update it
        if new_data_good is not None and new_data_spam is not None:
            cur_group.set_new_db(new_data_good, new_data_spam)
        good, spam = cur_group.get_good_and_spam()
        # If the user toggled the spam removal status
        if rem_status == "Turn off":
            cur_group.deactivate_spam_remove()
        elif rem_status == "Turn on":
            cur_group.activate_spam_remove()
        # If the user toggled the auto label status
        if auto_label_status == "Turn off":
            cur_group.deactivate_auto_label()
        elif auto_label_status == "Turn on":
            cur_group.activate_auto_label()
        '''==================
        End of code for changing settings
        =================='''
        # Show the editing panel
        return HTML_OF_MANAGE \
               % {"good_amount": good.count("\n") + 1 if len(good) > 1 else 0,
                  "spam_amount": spam.count("\n") + 1 if len(spam) > 1 else 0,
                  "good": good, "spam": spam, "chat_id": chat_id, "group_title": group_title,
                  "radio_of_status": HTML_OF_RADIO_TURNON_CHECKED if Group.Group(chat_id).is_remove_activated()
                  else HTML_OF_RADIO_TURNOFF_CHECKED,
                  "radio_of_auto_label": HTML_OF_RADIO_TURNON_AUTOLABEL_CHECKED if Group.Group(
                      chat_id).is_auto_label()
                  else HTML_OF_RADIO_TURNOFF_AUTOLABEL_CHECKED
                  }

    @cherrypy.expose
    def choose_group(self):
        # Check if the user is logged in
        username = cherrypy.session.get('username', None)
        if username is None:
            return HTML_OF_ERROR + self.logout()
        # Show the page to choose a group
        btns = ""
        for chatid in Admin.Admin(username).get_groups():
            btns += HTML_OF_CHOOSE_GROUP_BTN \
                    % (chatid, BOT.getChat(chatid).title, BOT.getChat(chatid).title)
        if btns == "":
            btns = HTML_OF_NO_GROUPS_CREATED
        return HTML_OF_CHOOSE_GROUP % {"groups_btns_html": btns, "username": username}


@cherrypy.expose
def err(status, message, traceback, version):
    return HTML_OF_ERROR + HTML_OF_LOGIN


def main():
    try:
        cherrypy.quickstart(WebInterface(), config="web-files/config.txt")
    except socket.timeout:
        cherrypy.quickstart(WebInterface(), config="web-files/config.txt")


if __name__ == "__main__":
    main()
