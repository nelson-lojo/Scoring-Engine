from flask import Flask, render_template, send_from_directory, request
from json import dumps

app = Flask(__name__)

criteria = {
    "vulns" : [],
    "pens" : [],
    "forensics" : []
}

@app.route('/')
def greet():
    # welcome the user to the app and ask if they want a run down

@app.route('/<resource>')
def serve(resource):
    return send_from_directory("resources", resource)

@app.route('/tutorial')
def tut():
    # explain the pipeline of vulns, pens, and forensics
    # explain how to use the tool

@app.route('/<task>/<menu>')
def base(menu, task):
    try:
        assert menu in ["vulns", "pens", "forensics"], f"Menu must be {["vulns", "pens", "forensics"]}"
        assert task in ['add', 'rm', 'cat'], f"Task must be {['add', 'rm', 'cat']}"
    except e:
        return repr(e)

    if task == 'add':
        # present a creation menu
        if menu == 'vulns':
            # vulns
            #
        elif menu == 'pens':
            # pens
        # forensics
    elif task == 'rm':
        criteria[menu].remove(____)

    # if we get here, we're inspecting
    present(criteria[menu]) # and highlight the menu in the left

@app.route('/export')
def export():
    # export the criteria dict

@app.route('/state')
def state():
    return dumps(criteria)

if __name__ == "__main__":
    app.run(host=web['ip'], port=web['port'], debug=True)#, reloader=True) 
