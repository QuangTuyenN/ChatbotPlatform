import os
import yaml

from kubernetes import config, dynamic
from kubernetes.client import api_client


def create_bot_kube(bot_id):
    client = dynamic.DynamicClient(api_client.ApiClient(
        configuration=config.load_incluster_config()))
    rasa_port = int(os.environ.get("RASA_PORT", 5005))
    bot_pvc_storage_class = (os.environ.get(
        "BOT_PVC_STORAGE_CLASS", "longhorn"))
    namespace = os.environ.get("BOT_NAME_SPACE", "chat")
    rasa_img = os.environ.get("RASA_IMAGE", "")
    rasa_model_path = os.environ.get("RASA_MODEL_PATH", "/app/models")
    # rasa_cpu_limit = os.environ.get("RASA_CPU_LIMIT", "1.0")
    rasa_mem_limit = os.environ.get("RASA_MEM_LIMIT", "1.5Gi")
    rasa_cpu_request = os.environ.get("RASA_CPU_REQUEST", "500Mi")
    rasa_mem_request = os.environ.get("RASA_MEM_REQUEST", "1.5Gi")
    # rasa_replicas = os.environ.get("RASA_REPLICAS", "1")
    rasa_volume = os.environ.get("RASA_VOLUME", "512Mi")
    host_ingress_bot = os.environ.get(
        "HOST_INGRESS_BOT", "cbpapi.prod.dev")

    bot_pvc_yaml = yaml.safe_load(f"""
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: bot-{bot_id}
    spec:
      accessModes:
        - ReadWriteMany
      storageClassName: {bot_pvc_storage_class}
      resources:
        requests:
          storage: {rasa_volume}
    """)

    bot_deploy_yaml = yaml.safe_load(f"""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      labels:
        app: bot-{bot_id}
      name: bot-{bot_id}
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: bot-{bot_id}
      template:
        metadata:
          labels:
            app: bot-{bot_id}
        spec:
          nodeSelector:
            kubernetes.io/hostname: master1
          containers:
          - name: bot-{bot_id}
            image: {rasa_img}
            ports:
            - containerPort: {rasa_port}
            command: ["rasa", "run", "--enable-api", "--cors", "*"]
            volumeMounts:
            - name: model-volume
              mountPath: {rasa_model_path}
            - name: rasa-config
              mountPath: "/app/endpoints.yml"
              subPath: endpoints.yml
            - name: rasa-config
              mountPath: "/app/credentials.yml"
              subPath: credentials.yml
          volumes:
            - name: model-volume
              persistentVolumeClaim:
                claimName: bot-{bot_id}
            - name: rasa-config
              configMap:
                name: rasa-config
    """)
    # """
    # resources:
    #   limits:
    #     cpu: {rasa_cpu_limit}
    #     memory: {rasa_mem_limit}
    #   requests:
    #     cpu: {rasa_cpu_request}
    #     memory: {rasa_mem_request}

    # - name: endpoints
    #   configMap:
    #     name: rasa-endpoints
    # - name: credentials
    #   configMap:
    #     name: rasa-credentials
    # """

    bot_svc_yaml = yaml.safe_load(f"""
    apiVersion: v1
    kind: Service
    metadata:
      name: bot-{bot_id}
    spec:
      ports:
      - port: {rasa_port}
        targetPort: {rasa_port}
      selector:
        app: bot-{bot_id}
    """)

    bot_ingress_yaml = yaml.safe_load(f"""
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: bot-{bot_id}
      annotations:
        nginx.ingress.kubernetes.io/rewrite-target:  /$2

    spec:
      ingressClassName: nginx
      rules:
      - host: {host_ingress_bot}
        http:
          paths:
          - path: /webchat/{bot_id}(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: bot-{bot_id}
                port:
                  number: {rasa_port}
    """)

    api_pvc = client.resources.get(
        api_version="v1", kind="PersistentVolumeClaim")
    api_deploy = client.resources.get(api_version="apps/v1", kind="Deployment")
    api_service = client.resources.get(api_version="v1", kind="Service")
    api_ingress = client.resources.get(
        api_version="networking.k8s.io/v1", kind="Ingress")

    pvc = api_pvc.create(body=bot_pvc_yaml, namespace=namespace)
    print(f"PVC created. status={pvc.metadata.name}")

    deployment = api_deploy.create(body=bot_deploy_yaml, namespace=namespace)
    print(f"Deployment created. status={deployment.metadata.name}")

    service = api_service.create(body=bot_svc_yaml, namespace=namespace)
    print(f"Service created. status={service.metadata.name}")

    ingress_deploy = api_ingress.create(
        body=bot_ingress_yaml, namespace=namespace)
    print(f"Ingress created. status={ingress_deploy.metadata.name}")
