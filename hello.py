from flask import Flask
from flask.ext.script import Manager
from flask import redirect

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
	return redirect('http://www.baidu.com')

if __name__=='__main__':
    manager.run()
    

        
