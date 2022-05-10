import empireController as ec
import Communicator as com
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route('/' , methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/empire_home',methods=['GET','POST'])
def empire_home():
    empire = ec.EmpireController()
    if request.method == 'POST':
        token = request.form.get('token')
        return redirect(url_for('empire_home', token=token))
    else:
        token = empire.getEmpireToken()
        agents = empire.getCurrentAgents(token)
        if agents[0][0] == '' and len(agents) == 1:
            i = 0
        else:
            i = len(agents)
        if token == '':
            return render_template(url_for('empire_home'))
        else:
            stagers = empire.getAllStager(token)
            listeners = empire.getCurrentListeners(token)
            if listeners[0][0] == '':
                flg = empire.createHTTPListener(token)
                if flg:
                    listeners = empire.getCurrentListeners(token)
                else:
                    listeners = ['','']
            return render_template('empire_home.html', token=token, stagers=stagers, listeners=listeners[0], i=i)

@app.route('/empire_stager',methods=['POST'])
def empire_stager():
    empire = ec.EmpireController()
    token = empire.getEmpireToken()
    stagers = request.form.get('setStager')
    listener = request.form.get('setListener')
    createStagers = empire.generateStager(token,stagers)
    output = createStagers[0][0]
    description = createStagers[0][1]
    return render_template('empire_stager.html', listener=listener, stagers=stagers, output=output, description=description)

@app.route('/empire_agent')
def empire_agent():
    empire = ec.EmpireController()
    token = empire.getEmpireToken()
    agents = empire.getCurrentAgents(token)
    if agents[0][0] == '':
        i = 0
    else:
        i = len(agents)
    return render_template('empire_agent.html', agents=agents, i=i)


@app.route('/bot', methods=['POST'])
def bot_replay():
    comm = com.Communicator()
    comm.ChatCommunication()
    return

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5566)