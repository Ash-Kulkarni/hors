{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  name = "hors dev shell";
  packages = [
    pkgs.python313
    pkgs.uv
    pkgs.ruff
    pkgs.mypy
    pkgs.gum
    pkgs.gcc # 👈 add this line
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.gcc.cc.lib}/lib:$LD_LIBRARY_PATH"
    echo "Python version: $(python3 --version)"
    uv venv
    uv pip install -e .
  '';
}
