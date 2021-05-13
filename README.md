# Pi Id Card
This package will install a small Python script wich runs to inform about some system facts on an i2c OLED-Display.

## build package

    native:# dpkg-deb --build piidcard_1.0-2
    docker:# docker run -it -v $PWD:/mnt --workdir /mnt debian dpkg-deb --build piidcard_1.0-2

## install package

sudo dpkg -i piidcard_1.0-2.deb

## start/stop Service
    systemctl start piidcard
    systemctl stop piidcard
