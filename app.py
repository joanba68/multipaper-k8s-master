from kubernetes import client, config
from flask import Flask, jsonify, request
import logging

DEFAULT_NAMESPACE = "multipaper"
DEFAULT_DEPLOYMENT_NAME = "multipaper-server"

config.load_incluster_config()
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

app = Flask(__name__)

logger = logging.getLogger(__name__)


# {"pod_name": "", "namespace": "default", update_replicas: False, deployment_name: ""}
@app.route('/delete_pod', methods=['POST'])
def delete_pod():
    try:
        data = request.get_json()
        pod_name = data["pod_name"]
        namespace = data.get("namespace", DEFAULT_NAMESPACE)
        update_replicas = data.get("update_replicas", True)
        deployment_name = data.get("deployment_name", DEFAULT_DEPLOYMENT_NAME)
        v1.delete_namespaced_pod(pod_name, namespace)
        if update_replicas:
            deployment = apps_v1.read_namespaced_deployment_scale(
                deployment_name, namespace)
            deployment.spec.replicas -= 1
            apps_v1.patch_namespaced_deployment_scale(
                deployment_name, namespace, deployment)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error("Error deleting pod: " + str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


# {"namespace": "default", "deployment_name": ""}
@app.route('/scale_up', methods=['POST'])
def scale_up():
    try:
        data = request.get_json()
        num_replicas = data.get("num_replicas", 1)
        namespace = data.get("namespace", DEFAULT_NAMESPACE)
        deployment_name = data.get("deployment_name", DEFAULT_DEPLOYMENT_NAME)
        deployment = apps_v1.read_namespaced_deployment_scale(
            deployment_name, namespace)
        deployment.spec.replicas += num_replicas
        apps_v1.patch_namespaced_deployment_scale(
            deployment_name, namespace, deployment)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error("Error scaling up: " + str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
