import paramiko
import os

SFTP_HOST = "localhost"
SFTP_PORT = 22
SFTP_USER = "sftpaplikace"
SFTP_PASSWORD = "sftpaplikace"

UPLOAD_BASE_PATH = "/app/uploads"
UPLOAD_PUBLIC_URL = "/app/uploads"


def upload_file_sftp(local_path, remote_path):
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)

    remote_dir = os.path.dirname(remote_path)
    _ensure_remote_dir(sftp, remote_dir)

    sftp.put(local_path, remote_path)

    sftp.close()
    transport.close()


def download_file_sftp(remote_path):
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)

    with sftp.file(remote_path, "rb") as f:
        file_bytes = f.read()

    sftp.close()
    transport.close()

    return file_bytes


def _ensure_remote_dir(sftp, remote_dir):
    """Vytvoří adresáře rekurzivně"""
    parts = remote_dir.strip("/").split("/")
    path = ""
    for part in parts:
        path += f"/{part}"
        try:
            sftp.stat(path)
        except FileNotFoundError:
            sftp.mkdir(path)
