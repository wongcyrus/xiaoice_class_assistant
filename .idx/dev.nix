{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-23.11"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.virtualenv
    pkgs.nodejs_20
    pkgs.nodePackages.firebase-tools
    pkgs.google-cloud-sdk
    pkgs.terraform
    pkgs.zip
    pkgs.unzip
  ];

  # Sets environment variables in the workspace
  env = {
    PYTHONUNBUFFERED = "1";
  };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
      "ms-python.vscode-pylance"
      "ms-python.black-formatter"
      "ms-python.flake8"
      "ms-python.pylint"
      "ms-toolsai.jupyter"
    ];

    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install global npm packages or setup venvs
        # npm-install = "npm install"; 
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a development server
        # start-server = "npm run dev";
      };
    };
  };
}
