from flask import jsonify, request, abort

from app import app
from cluster import Cluster
from state import State

state = State()
cluster = Cluster(state)


@app.route('/')
@app.route('/index')
def index():
    return jsonify(test="Test")


@app.route('/cluster/show')
def show_cluster_status():
    global cluster
    return jsonify(cluster.cluster_show())


@app.route('/cluster/check', methods=['POST'])
def choose_node_role():
    global cluster
    if not request.json['hostname']:
        abort(400)
    if not cluster.check_cluster_exists():
        resp = 0
    elif cluster.master_show() and request.json['hostname'] not in cluster.master_show():
        resp = 1
    elif cluster.check_master(request.json['hostname']):
        resp = 2
    else:
        resp = 3
    return jsonify(response=resp)


@app.route('/cluster/create', methods=['POST'])
def create_cluster():
    global cluster
    if not request.json['hostname']:
        abort(400)
    return jsonify(created=cluster.cluster_create(request.json['hostname']))


@app.route('/master/show')
def show_master():
    global cluster
    return jsonify(cluster.master_show())


@app.route('/master/demote')
def demote_master():
    global cluster
    return jsonify(demoted=cluster.master_demote())


@app.route('/failover')
def failover():
    global cluster
    return jsonify(done=cluster.failover())


@app.route('/slave/add', methods=['POST'])
def add_slave():
    global cluster
    if not request.json['hostname']:
        abort(400)
    return jsonify(added=cluster.slave_add(request.json['hostname']))
