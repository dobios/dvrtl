{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python3.withPackages(ps: [ 
    ps.black  
    ps.build 
    ps.click 
    ps.colorama 
    ps.isort 
    ps.lexid 
    ps.looseversion 
    ps.mypy-extensions 
    ps.packaging 
    ps.pathspec 
    ps.pip-tools 
    ps.platformdirs 
    ps.pyproject-hooks 
    ps.toml 
    ps.tomli 
    ps.typing-extensions 
    ps.wheel
    ps.mypy
    ps.lark
  ]);

in
pkgs.mkShell {
  packages = [
    pythonEnv
  ];
}
