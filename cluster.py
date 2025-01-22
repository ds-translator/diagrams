from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, ECS
from diagrams.aws.network import ELB, VPC
from diagrams.aws.devtools import Codecommit  # Using Codecommit to symbolize repositories
from diagrams.onprem.container import Docker  # Using Docker to represent the Docker image build process
from diagrams.generic.blank import Blank  # Use a Blank node for custom labeling if needed
from diagrams.onprem.client import Client, User  # Representing the user and the web browser
from diagrams.onprem.ci import GithubActions
from diagrams.aws.security import IdentityAndAccessManagementIamAddOn
from diagrams.oci.security import IDAccess
from diagrams.onprem.iac import Terraform
from diagrams.oci.compute import BM
from diagrams.oci.devops import APIService
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.aws.management import AmazonManagedPrometheus as Prometheus, AmazonManagedGrafana as Grafana


with Diagram("AWS EKS Cluster", show=False):
    
    user = User("End User")
    browser = Client("Web Browser")    
    terraform = Terraform("IaC")
    devops_engineer = User("DevOps Engineer")



    # Repositories for the Frontend, Backend, and Terraform
    with Cluster("GitHub"):
        repo_frontend = Codecommit("Repo Frontend UI")
        repo_backend = Codecommit("Repo Backend Server")
        repo_infra = Codecommit("Repo Terraform Infrastructure")
        
        github_actions_frontend = GithubActions("test and build Frontend")
        github_actions_backend = GithubActions("test and build Backend")

    # Docker image build processes
    with Cluster("Docker Hub"):
        docker_image_frontend = Docker("Frontend Image (Nginx)")
        docker_image_backend = Docker("Backend Image (Python)")
        docker_image_stt = Docker("Whisper Image")
        docker_image_translate = Docker("Libretranslate Image")
        docker_image_tts = Docker("TTS Image")

    # Optional: Representing Load Balancer if necessary
    with Cluster("AWS"):
        cluster_entry = Blank("")
        vpc = VPC("AWS VPC")
        iam_role = IDAccess("IAM Role")
        iam_role >> terraform 
        devops_engineer >> iam_role

        with Cluster("Monitoring"):
            prometheus = Prometheus("Prometheus")
            grafana = Grafana("Grafana")
            # monitoring = Blank("Monitoring")


        with Cluster("EKS Cluster"):
            
            lb = ELB("Load Balancer")
        
            with Cluster("Nodegroup Frontend"):
                frontend = BM("Frontend with NginX")
            with Cluster("Nodegroup Backend"):
                backend = BM("Backend Server")    
            with Cluster("Nodegroup STT (GPU)"):
                whisper = BM("Whisper")
            with Cluster("Nodegroup Translation (GPU)"):
                libretranslate = BM("Libretranslate")
            with Cluster("Nodegroup TTS (GPU)"):
                tts = BM("TTS")

            with Cluster("Cluster services"):
                service_tts = APIService("TTS-Service")
                service_translate = APIService("Translation-Service")
                service_stt = APIService("STT-Service")   
                service_websocket = APIService("Websocket-Service") 
                service_http = APIService("HTTP-Service") 


    with Cluster("AWS Region 2"):
        backup_s3 = S3("Backup")

    # Link repositories to their related components
    repo_frontend >> github_actions_frontend >> docker_image_frontend >> frontend  # Frontend UI
    repo_backend >> github_actions_backend >> docker_image_backend >> backend  # Backend Server

    docker_image_stt >> whisper
    docker_image_translate >> libretranslate
    docker_image_tts >> tts

    repo_frontend >> backup_s3  # Frontend UI
    repo_backend >> backup_s3
    repo_infra >> backup_s3

    # Linking the Terraform infrastructure repo to the cluster indirectly
    devops_engineer >> repo_infra >> terraform >> cluster_entry  # Representing that the Terraform manages broader infrastructure

    # monitoring >> github_actions_frontend
    # monitoring >> github_actions_backend
    # monitoring >> terraform

    backend >> service_stt
    backend >> service_translate
    backend >> service_tts
    lb >> service_http
    lb >> service_websocket

    service_websocket >> backend
    service_http >> frontend
    

    
    user >> browser << Edge(label="HTTPS") >> vpc << Edge(label="Websockets") >> lb

    user >> browser << Edge(label="Websockets") >> vpc << Edge(label="HTTPS") >> lb

            
