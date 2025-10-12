# fatresort

Actually I recommend using https://github.com/lhrios/yafs or the GUI version https://www.luisrios.eti.br/public/en_us/projects/visual_yafs/
To install it with recent java you need javaFX. Install it with 

`sudo apt install openjfx`

Then you can run the GUI with 

`java --module-path /usr/share/openjfx/lib --add-modules javafx.controls,javafx.fxml -jar visual_yafs.jar`

If you entcounter the error `/tmp/visual_yafs/2019_11_03/yafs/yafs`file or directory not found, install 32bit libraries

`sudo apt install libc6:i386 libstdc++6:i386 zlib1g:i386`
