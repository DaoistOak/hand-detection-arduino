{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    opencv4
    numpy
    pyserial
    pip
    setuptools
  ]);
in

pkgs.mkShell {
  name = "arduino-dev";

  # Tools and libraries available in your shell
  buildInputs = with pkgs; [
    arduino-cli     # CLI for compiling and uploading sketches
    arduino         # Classic Arduino IDE (1.x) – optional if you prefer GUI
    picocom         # Serial terminal
    screen          # Alternative serial monitor
    pythonEnv       # Python with our custom packages
    gtk3
    pkg-config
    gobject-introspection
    gst_all_1.gstreamer
    gst_all_1.gst-plugins-base
    gst_all_1.gst-plugins-good
    gst_all_1.gst-plugins-bad
    gst_all_1.gst-plugins-ugly
  ];

  # Useful IDE/editor environment variables (adjust as needed)
  # e.g., set serial port rate for monitor
  shellHook = ''
    export SERIAL_PORT="/dev/ttyACM0"
    export SERIAL_RATE="9600"
    export PYTHONPATH="${pkgs.python3Packages.opencv4}/lib/python3.9/site-packages:$PYTHONPATH"
    export GST_PLUGIN_PATH="${pkgs.gst_all_1.gst-plugins-base}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-good}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-bad}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-ugly}/lib/gstreamer-1.0"
    
    # Create a virtual environment for MediaPipe and other packages
    if [ ! -d "venv" ]; then
      echo "Creating virtual environment..."
      python -m venv venv
      source venv/bin/activate
      pip install mediapipe opencv-python numpy pyserial
    else
      source venv/bin/activate
    fi
    
    echo "🔧 Arduino environment ready!"
    echo "Use: arduino-cli compile --fqbn <board> sketch"
    echo "     arduino-cli upload -p \$SERIAL_PORT --fqbn <board> sketch"
    echo "     picocom \$SERIAL_PORT -b \$SERIAL_RATE"
  '';
}
