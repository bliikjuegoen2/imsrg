# shell.nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "cpp-dev-shell";

  buildInputs = with pkgs; [
    gcc # Compiler
    gnumake # Make
    cmake # Optional, if the project uses CMake
    gsl # GNU Scientific Library
    openblas # BLAS implementation
    boost # Boost libraries
    armadillo # Linear algebra
    pkg-config # For auto-discovering compile flags
    zlib
    (python312.withPackages (ps: with ps; [ pybind11 ]))
  ];

  shellHook = ''
    echo "💻 Ready to build your C++ fork with Boost, Armadillo, etc."
  '';
}
