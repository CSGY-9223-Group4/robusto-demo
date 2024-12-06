# Robusto Demo for Lab4


## Create a virtualenv (recommended)

```bash
# Create the virtual environment
python -m venv robusto-venv

# Activate the virtual environment
# This will add the prefix "(robusto-venv)" to your shell prompt
source robusto-venv/bin/activate
```

## Install the dependencies

```
pip install -r requirements.in
```


## Run the demo

```
./run-demo
```


## Notes

* The `./tuf-ite2/` repository has been largely copied from the [TUF Example
  Repository](https://github.com/theupdateframework/python-tuf/tree/develop/examples)
    * The code has been modified to work as per [In-toto specification
      ITE-2](https://github.com/in-toto/ITE/blob/master/ITE/2/README.adoc)
* Currently this demo only works with TUF repo running on
  `http://127.0.0.1:8001`. You will need to update `./upload` and `./download`
  if you want it to work with a different port.
* The demo works in a bash/zsh environment. It may not work in other
  environments.
* This repository assumes that packages are `.tar.gz` files. The `final_product`
  directory should have a unique `.tar.gz` which will be used as the package
  name and subsequently the target name in the TUF repository.
* As per ITE-2 the layouts are named as `*.core.layout` as the layouts are not
  dependent on the package name. This demo assumes that the layout is unique per
  package because we are reusing the in-toto-demo layout which is highly
  specific to the package. So instead of `1.core.layout` we have `root.layout`
  for this demo.

## Workflow

If you go through the run-demo script, you will see that it does the following:

1.  Basic cleanup from previous runs if any
1.  Uses `./migrate` to setup the packages and in-toto-metadata as per ITE-2.
    This is done because the `./tuf-ite2/uploader/uploader` script uses the
    filepaths same as the targetpaths. After running this script, the directory
    should look like this:

      ```bash
      tree -a targets-ite2
      #  targets-ite2
      #  ├── 2cf178c1aa2f99b093243b032f299d8dd72abf5081bc608718b2003977a12bc7.layout.custom
      #  ├── b4df3c864becf593a939414e5cfb85a7d9406b5f8bb645d248a35163c9afd3f9.package.custom
      #  ├── in-toto-metadata
      #  │   ├── b4df3c864becf593a939414e5cfb85a7d9406b5f8bb645d248a35163c9afd3f9
      #  │   │   ├── clone.bcccc170.link
      #  │   │   ├── package.8a0ba954.link
      #  │   │   └── update-version.bcccc170.link
      #  │   └── root.layout
      #  ├── in-toto-pubkeys
      #  │   └── alice.pub
      #  └── packages
      #      └── demo-project.tar.gz
      ```

    *   It adds two `.custom` files in the root of `./targets-ite2/` directory
        which are used as custom metadata for the layout and the package target
        in the TUF repository.
    *   `sha256(<package-name>).package.custom` is the custom metadata for the
        package target.
    *   `sha256(<layout-name>).layout.custom` is the custom metadata for the
        layout target.
    *   The hashes are calculated using the `sha256` hash function.

     ```bash
     echo -n "demo-project.tar.gz" | sha256sum | awk '{print $1}'
     # b4df3c864becf593a939414e5cfb85a7d9406b5f8bb645d248a35163c9afd3f9
     echo -n "root.layout" | sha256sum | awk '{print $1}'
     # 2cf178c1aa2f99b093243b032f299d8dd72abf5081bc608718b2003977a12bc7
     ```

1.  Uses `./tuf-ite2/repository/repo` to start the TUF repository server.
    *   In this step, the TUF repository is first initialized with default root
        roles.
    *   In the init step, manual commands have been used to delegate a role to
        `packages-and-in-toto-metadata-signer`, add layouts and corresponding
        public keys required to verify the layout.
    *   While adding the layout, it reads the custom metadata required for the
        layout as per ITE-2 from `./targets-ite2/`. The layouts to be added as
        targets are hard-coded in the constructor of `SimpleRepository`. It uses
        the custom metadata of the layouts to find out the public keys required
        to verify the corresponding layout and adds them as targets too.
    *   Once the repo has been initialized, the TUF metadata should look like
        this:
         
      ```bash
      ./tuf-repo-data/get-repo-state
      # Error: packages-and-in-toto-metadata-signer metadata not found.
      # 404
      ls -lAh tuf-repo-data/metadata
      # total 68K
      # -rw-r--r-- 1 killua killua 1.7K Dec  5 22:36 1.root.json
      # -rw-r--r-- 1 killua killua  444 Dec  5 22:36 1.snapshot.json
      # -rw-r--r-- 1 killua killua  402 Dec  5 22:36 1.targets.json
      # -rw-r--r-- 1 killua killua  448 Dec  5 22:36 1.timestamp.json
      # -rw-r--r-- 1 killua killua  444 Dec  5 22:36 2.snapshot.json
      # -rw-r--r-- 1 killua killua 1.1K Dec  5 22:36 2.targets.json
      # -rw-r--r-- 1 killua killua  450 Dec  5 22:36 2.timestamp.json
      # -rw-r--r-- 1 killua killua  446 Dec  5 22:36 3.snapshot.json
      # -rw-r--r-- 1 killua killua 1.4K Dec  5 22:36 3.targets.json
      # -rw-r--r-- 1 killua killua  448 Dec  5 22:36 3.timestamp.json
      # -rw-r--r-- 1 killua killua  444 Dec  5 22:36 4.snapshot.json
      # -rw-r--r-- 1 killua killua 1.5K Dec  5 22:36 4.targets.json
      # -rw-r--r-- 1 killua killua  450 Dec  5 22:36 4.timestamp.json
      # -rw-r--r-- 1 killua killua 1.7K Dec  5 22:36 root.json
      # -rw-r--r-- 1 killua killua  444 Dec  5 22:36 snapshot.json
      # -rw-r--r-- 1 killua killua 1.5K Dec  5 22:36 targets.json
      # -rw-r--r-- 1 killua killua  450 Dec  5 22:36 timestamp.json
      ```
    *   You see an error because the `packages-and-in-toto-metadata-signer` role
        has only been delegated in the repo init step. There was no addition of
        metadata for that role. This is being done in the upload step.
    *   I have saved these files in `./tuf-repo-data/metadata-after-init/` for
        reference.
    
1.  Uses `./upload` which uses the `./tuf-ite2/uploader/uploader` script to
    upload targets from the `./targets-ite2` directory for the
    `packages-and-in-toto-metadata-signer` role.
    *   For the package it passes the custom metadata required as per ITE-2 from the
        `./targets-ite2/` directory.
    *   Then it adds the links for the package. The links are in a unique
        directory for the package in the `./targets-ite2/in-toto-metadata/`
    *   After uploading all the targets the TUF metadata should look like this:

      ```bash
      ./tuf-repo-data/get-repo-state
      ls -Alh tuf-repo-data/metadata
      # total 120K
      # -rw-r--r-- 1 killua killua 1001 Dec  6 09:54 1.packages-and-in-toto-metadata-signer.json
      # -rw-r--r-- 1 killua killua 1.7K Dec  6 09:54 1.root.json
      # -rw-r--r-- 1 killua killua  444 Dec  6 09:54 1.snapshot.json
      # -rw-r--r-- 1 killua killua  402 Dec  6 09:54 1.targets.json
      # -rw-r--r-- 1 killua killua  450 Dec  6 09:54 1.timestamp.json
      # -rw-r--r-- 1 killua killua 1.3K Dec  6 09:54 2.packages-and-in-toto-metadata-signer.json
      # -rw-r--r-- 1 killua killua  444 Dec  6 09:54 2.snapshot.json
      # -rw-r--r-- 1 killua killua 1.1K Dec  6 09:54 2.targets.json
      # -rw-r--r-- 1 killua killua  450 Dec  6 09:54 2.timestamp.json
      # -rw-r--r-- 1 killua killua 1.5K Dec  6 09:54 3.packages-and-in-toto-metadata-signer.json
      # -rw-r--r-- 1 killua killua  444 Dec  6 09:54 3.snapshot.json
      # -rw-r--r-- 1 killua killua 1.4K Dec  6 09:54 3.targets.json
      # -rw-r--r-- 1 killua killua  450 Dec  6 09:54 3.timestamp.json
      # -rw-r--r-- 1 killua killua 1.7K Dec  6 09:54 4.packages-and-in-toto-metadata-signer.json
      # -rw-r--r-- 1 killua killua  448 Dec  6 09:54 4.snapshot.json
      # -rw-r--r-- 1 killua killua 1.5K Dec  6 09:54 4.targets.json
      # -rw-r--r-- 1 killua killua  448 Dec  6 09:54 4.timestamp.json
      # -rw-r--r-- 1 killua killua  519 Dec  6 09:54 5.snapshot.json
      # -rw-r--r-- 1 killua killua  448 Dec  6 09:54 5.timestamp.json
      # -rw-r--r-- 1 killua killua  519 Dec  6 09:54 6.snapshot.json
      # -rw-r--r-- 1 killua killua  448 Dec  6 09:54 6.timestamp.json
      # -rw-r--r-- 1 killua killua  519 Dec  6 09:54 7.snapshot.json
      # -rw-r--r-- 1 killua killua  450 Dec  6 09:54 7.timestamp.json
      # -rw-r--r-- 1 killua killua  521 Dec  6 09:54 8.snapshot.json
      # -rw-r--r-- 1 killua killua  446 Dec  6 09:54 8.timestamp.json
      # -rw-r--r-- 1 killua killua 1.7K Dec  6 09:54 packages-and-in-toto-metadata-signer.json
      # -rw-r--r-- 1 killua killua 1.7K Dec  6 09:54 root.json
      # -rw-r--r-- 1 killua killua  521 Dec  6 09:54 snapshot.json
      # -rw-r--r-- 1 killua killua 1.5K Dec  6 09:54 targets.json
      # -rw-r--r-- 1 killua killua  446 Dec  6 09:54 timestamp.json
      ```
    *   The `packages-and-in-toto-metadata-signer` role has been added to the
        metadata.
    *   I have saved these files in `./tuf-repo-data/metadata-after-upload` for
        reference.

1.  Uses `./download` to download the packages from the TUF repository to
    `./downloads/` directory. This script uses `./tuf-ite2/client/client` script
    to download the package.
    *   The `./tuf-ite2/client/client` downloads each TUF target with TUF
        verification. If it encounters any target that has custom metadata then
        it downloads all the files mentioned in the custom metadata recursively.
        It stops if it encounters a target that has no custom metadata or if it
        encounters a target that has already been downloaded.
    *   It makes a separate directory for the downloaded package as
        `./downloads/<package-name>/` and then moves the files downloaded using
        `./tuf-ite2/client/client` to this directory.
    *   After downloading all targets it verifies the in-toto metadata for the
        downloaded package. Look out for in-toto verification return value in
        the output.
    *   The `./downloads/` directory should look like this:

      ```bash
      tree -a downloads
      downloads
      └── demo-project
          ├── alice.pub
          ├── clone.bcccc170.link
          ├── demo-project
          │   └── foo.py
          ├── demo-project.tar.gz
          ├── package.8a0ba954.link
          ├── root.layout
          ├── untar.link
          └── update-version.bcccc170.link

      2 directories, 8 files
      ```

## Lab4 Tasks

For this lab I have removed the below functionality from the above workflow
that you have to complete:

1.  The repo init step. This repo init was present in
    `./tuf-ite2/repository/_simplerepo.py`.
    * Look for `# Lab4: <task>` in the code to find the places where you need to
      implement the missing functionality. I have also provided helpful comments
      in the code to guide you through the implementation.
1.  The `./upload` script
1.  The recursive download of targets in the `./tuf-ite2/client/client` script.

The tasks are in decreasing order of difficulty.

For reference I have provided the below files:

1.  `./tuf-repo-data/metadata-after-init/` which contains the metadata after the
    repo init step for my demo.
1.  `./tuf-repo-data/metadata-after-upload/` which contains the metadata after
    the upload step for my demo.
1.  To check if your TUF metadata is getting uploaded as expected, I have also
    provided a helper script `./tuf-repo-data/get-repo-state` which will
    download all the TUF metadata from the TUF repository to
    `./tuf-repo-data/metadata/` directory. You can match the metadata files with
    the reference metadata files that I have provided.
1.  `./final_product` which contains the in-toto demo output files I used. You
    have to replace these files with your part1 output files. Make sure you **do
    not** put `./final_product/demo-project` directory and
    `./final_product/untar.link` into the `./final_product` directory as these
    should not be pushed to the TUF repository.
1.  `./targets-ite2-saurabh/` which contains the targets and in-toto metadata
    after running the `./migrate` script for my demo. You have to run the
    `./migrate` after putting your files in `./final_product` to set up
    `./targets-ite2/` for your demo.

Your aim is to implement the missing functionality so that the demo works as
expected. To check if your work is correct, you can run the demo using the
`./run-demo` script. If the demo runs without any errors then your work is
correct. The `./download` script is doing the in-toto verification after
downloading the TUF targets. If there is anything missing then in-toto
verification will fail.

