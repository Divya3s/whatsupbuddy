# importing libraries 
from flask import Flask 
from flask_mail import Mail, Message 

app = Flask(__name__) 
mail = Mail(app) # instantiate the mail class 

# configuration of mail 
app.config['MAIL_SERVER']='smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'whatsupbuddy333@outlook.com'
app.config['MAIL_PASSWORD'] = '6EtHXMEATDSUy6J'
app.config['MAIL_USE_TLS'] = False
#app.config['MAIL_USE_SSL'] = True
mail = Mail(app) 

# message object mapped to a particular URL 5,&%6M@wW~xX.e3 ‘/’ 
@app.route("/") 
def index(): 
    msg = Message( 
				'Hello', 
				sender ='whatsupbuddy333@gmail.com', 
				recipients = ['intelligentechn@gmail.com'] 
			) 
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg) 
    return 'Sent'

if __name__ == '__main__': 
    app.run(debug = True) 
