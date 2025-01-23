from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, ECS
from diagrams.aws.network import ELB, VPC
from diagrams.aws.devtools import Codecommit
from diagrams.onprem.container import Docker
from diagrams.generic.blank import Blank
from diagrams.onprem.client import Client, User, Users
from diagrams.onprem.ci import GithubActions
from diagrams.aws.security import IdentityAndAccessManagementIamAddOn
from diagrams.oci.security import IDAccess
from diagrams.onprem.iac import Terraform
from diagrams.oci.compute import BM
from diagrams.oci.devops import APIService
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.aws.management import AmazonManagedPrometheus as Prometheus, AmazonManagedGrafana as Grafana

class Services:
    def __init__(self):
        self.http = APIService("HTTP")
        self.websocket = APIService("Websocket")
        self.stt = APIService("STT")
        self.translate = APIService("Translate")
        self.tts = APIService("TTS")

class Nodegroups:
    def __init__(self):
        self.frontend = APIService("Frontend (Nginx)")
        self.backend = APIService("Backend (Python)")
        self.whisper = APIService("Whisper")
        self.libretranslate = APIService("Libretranslate")
        self.tts = APIService("TTS")   

class Images:
    def __init__(self):
        self.frontend = Docker("Frontend Image (Nginx)")
        self.backend = Docker("Backend Image (Python)")
        self.stt = Docker("Whisper Image")
        self.translate = Docker("Libretranslate Image")
        self.tts = Docker("TTS Image")

class Repos:
    def __init__(self):
        self.frontend = Codecommit("Repo Frontend UI")
        self.backend = Codecommit("Repo Backend Server")
        self.infra = Codecommit("Repo Terraform Infrastructure")

with Diagram("AWS EKS Cluster", show=False):
    
    user = Users("End Users")
    browser = Client("Web Browser")    
    terraform = Terraform("IaC")
    devops_engineer = Users("DevOps Engineers")
    developers = Users("Developers")

    with Cluster("GitHub"):
        repos = Repos()
        
        github_actions_frontend = GithubActions("test and build Frontend")
        github_actions_backend = GithubActions("test and build Backend")

    with Cluster("Docker Hub"):
        images = Images()
        
        images.frontend >> Edge(style='invis') \
        >> images.backend >> Edge(style='invis') \
        >> images.stt >> Edge(style='invis') \
        >> images.translate >> Edge(style='invis') \
        >> images.tts

    with Cluster("AWS"):
        cluster_entry = Blank("")
        vpc = VPC("AWS VPC")
        iam_role = IDAccess("IAM Role")
        iam_role >> terraform 
        devops_engineer >> iam_role

        with Cluster("Monitoring"):
            prometheus = Prometheus("Prometheus")
            grafana = Grafana("Grafana")
    
        with Cluster("EKS Cluster"):
            
            lb = ELB("Load Balancer")
        
            ng = Nodegroups()
            
            ng.frontend >> Edge(style='invis') \
            >> ng.backend >> Edge(style='invis') \
            >> ng.whisper >> Edge(style='invis') \
            >> ng.libretranslate >> Edge(style='invis') \
            >> ng.tts >> Edge(style='invis')

            with Cluster("Cluster services"):
                services = Services()

            services.http >> Edge(style='invis') \
            >> services.websocket >> Edge(style='invis') \
            >> services.stt >> Edge(style='invis') \
            >> services.translate >> Edge(style='invis') \
            >> services.tts >> Edge(style='invis')

    with Cluster("AWS Region 2"):
        backup_s3 = S3("Backup")

    repos.frontend >> github_actions_frontend >> images.frontend >> ng.frontend  # Frontend UI
    repos.backend >> github_actions_backend >> images.backend >> ng.backend  # Backend Server

    images.stt >> ng.whisper
    images.translate >> ng.libretranslate
    images.tts >> ng.tts

    repos.frontend >> backup_s3  # Frontend UI
    repos.backend >> backup_s3
    repos.infra >> backup_s3

    # Linking the Terraform infrastructure repo to the cluster indirectly
    devops_engineer >> repos.infra >> terraform >> cluster_entry  # Representing that the Terraform manages broader infrastructure

    # monitoring >> github_actions_frontend
    # monitoring >> github_actions_backend
    # monitoring >> terraform

    ng.backend >> services.stt
    ng.backend >> services.translate
    ng.backend >> services.tts
    lb >> services.http
    lb >> services.websocket

    # service_websocket >> backend
    # service_http >> frontend
    
    developers >> repos.frontend
    developers >> repos.backend
    
    user >> browser << Edge(label="HTTPS") >> vpc << Edge(label="Websockets") >> lb

    user >> browser << Edge(label="Websockets") >> vpc << Edge(label="HTTPS") >> lb

            
