{ pkgs }: {
  deps = [
    pkgs.python39Full
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libuuid
      pkgs.zlib
      pkgs.stdenv.cc.cc.lib
      pkgs.xorg.libX11
    ];
    PYTHONHOME = "${pkgs.python39Full}";
    PYTHONBIN = "${pkgs.python39Full}/bin/python3.9";
    LANG = "en_US.UTF-8";
    STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
    PRYBAR_PYTHON_BIN = "${pkgs.replitPackages.prybar-python310}/bin/prybar-python310";
  };
} 