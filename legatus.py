from logging import exception
import os

from urllib3 import Retry
import empireController as ec
import Communicator as com
import subprocess
from subprocess import PIPE
from flask import Flask, redirect, render_template, request, url_for, send_file

DOWNLOAD_DIR_PATH = os.path.join(os.path.dirname(__file__), 'download')

app = Flask(__name__)

def process_action(command):
    result = subprocess.run(command, shell=True, stdout=PIPE, stderr=PIPE)
    return(result.stdout.decode('utf-8').split('\n')[0])

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
    outfile = empire.getStagerByName(token, stagers)['options']['OutFile']['Value']
    try:
        outfile = os.path.basename(outfile)
    except:
        outfile = "empire.bin"
    try:
        createStagers = empire.generateStager(token, stagers, outfile)
        output = createStagers[0][0]
        description = createStagers[0][1]
        path = os.getcwd() + "/download/" + outfile
        with open(path, mode='w') as f:
            f.write(output)
    except:
        output = "Error"
        description = "Error"
    # filename = createStagers[0][2]
    # path = os.getcwd() + "/download" + filename

    return render_template('empire_stager.html', listener=listener, stagers=stagers, output=output, description=description, outputfile=outfile)

@app.route('/empire_stager_output',methods=['POST'])
def empire_stager_output():
    output = request.form.get('stagerOutput')
    filename = request.form.get('stagerFileName')
    path = os.getcwd() + "/download" + filename
    with open(path, mode='w') as f:
        f.write(output)
    return send_file(path, as_attachment=True, attachment_filename=filename)

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

@app.route('/docker')
def docker():
    cmd = "docker-compose -f docker/webssh/docker-compose.yml ps|grep Up|wc -l"
    webssh_flg = process_action(cmd)
    cmd = "docker-compose -f docker/mattermost-docker/docker-compose.yml ps|grep Up|wc -l"
    mattermost_flg = process_action(cmd)
    return render_template('docker.html',webssh=webssh_flg,mattermost=mattermost_flg)

@app.route('/docker/mattermost')
def docker_mattermost():
    cmd = "docker-compose -f docker/mattermost-docker/docker-compose.yml ps|grep Up|wc -l"
    flg = process_action(cmd)
    # 3: Up, 0: Down
    if flg == "3":
        cmd = "docker-compose -f docker/mattermost-docker/docker-compose.yml stop"
        process_action(cmd)
    else:
        cmd = "docker-compose -f docker/mattermost-docker/docker-compose.yml start"
        process_action(cmd)
    return redirect(url_for('docker'))

@app.route('/docker/webssh')
def docker_webssh():
    cmd = "docker-compose -f docker/webssh/docker-compose.yml ps|grep Up|wc -l"
    flg = process_action(cmd)
    # 1: Up, 0: Down
    if flg == "1":
        cmd = "docker-compose -f docker/webssh/docker-compose.yml stop"
        process_action(cmd)
    else:
        cmd = "docker-compose -f docker/webssh/docker-compose.yml start"
        process_action(cmd)
    return redirect(url_for('docker'))

@app.route('/bot', methods=['POST'])
def bot_replay():
    comm = com.Communicator()
    comm.ChatCommunication()
    return

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5566)