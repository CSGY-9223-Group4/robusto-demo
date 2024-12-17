"""Client for our TUF repository to upload metadata to Rekor using rekor-cli."""

import re
import subprocess
import tempfile

class RekorClient:
    """
    RekorClient is a client for our TUF repository to upload metadata to Rekor using rekor-cli.
    It has convenience methods to upload metadata to Rekor and to retrieve logs from Rekor.
    """
    UPLOAD_MESSAGE = r"Created entry at index (\d+), available at: (\S+)"
    
    def __init__(self, tuf_repo_url, key_dir) -> None:
        """Initializes the RekorUploader object with the URL of the TUF repository."""

        # TODO: allow running against a self-hosted Rekor server
        # for now we will use the Sigstore managed Rekor server
        self.tuf_repo_url = tuf_repo_url
        self.key_dir = key_dir

        self.logs: tuple[int, str] = []

    def upload(self, root: bytes, metadata: bytes):
        """Uploads the metadata with given root public key to Rekor."""

        # Download root key into a temporary file
        with tempfile.TemporaryDirectory() as temp_dir:

            with open(f"{temp_dir}/root.json", "wb") as f:
                f.write(root)

            with open(f"{temp_dir}/metadata.json", "wb") as f:
                f.write(metadata)

            # Upload metadata to Rekor
            try:
                output = subprocess.run([
                    "rekor-cli",
                    "upload",
                    "--type",
                    "tuf",
                    "--artifact",
                    f"{temp_dir}/metadata.json",
                    "--public-key",
                    f"{temp_dir}/root.json",
                ],
                check=True, capture_output=True)

                print(f"Uploaded metadata to Rekor: {output.stdout.decode()}")

            except subprocess.CalledProcessError as e:
                print(f"Failed to upload metadata to Rekor: {e}")

        output = output.stdout.decode()
        match = re.search(self.UPLOAD_MESSAGE, output)

        self.logs.append((int(match.group(1)), match.group(2)))

    def get_logs(self) -> list[dict]:
        """Returns the logs from Rekor as a list of dictionaries."""

        return [
            {
                "Log Index": log[0],
                "Log URL": log[1],
            }
            for log in self.logs
        ]
