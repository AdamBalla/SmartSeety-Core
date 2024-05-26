# IoT core application

The python script(s) running on the Raspberry pi.

## How to run
Because pipenv is broken on our raspberry, I installed all dependencies system-wide. The Pipenv file is only for development purposes.

    python3 app.py
	
## How to install new dependencies system-wide
    python3 -m pip install yourpackage
	
Please note that the command pip3 is broken, you have to invoke pip this way.

## Internet
Our beloved raspberry CANNOT handle Wifi + ethernet at the same time. 

* If you need internet access -> unplug ethernet, there won't be SSH access.
* If you need SSH access -> plug the ethernet, there won't be internet.