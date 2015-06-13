# Klausuromat

`Klausuromat` is a tool written in Python 3 that automatically generates source code reading exercises for the C programming language.

## Installation

Setup on a fresh Ubuntu 14.04 LTS Server:

1. Install the tools and copy files to the final locations
   ```sh
   $ sudo apt-get install git apache2 libapache2-mod-python gcc
   $ sudo service apache2 start
   $ cd /usr/lib/cgi-bin/
   $ sudo git clone https://github.com/seecurity/klausuromat/
   $ sudo cp -R klausuromat/include /var/www/html/
   ```

2. Open the file [settings.json](/settings.json) and edit the log-files according to your needs. The include directory should be set to
   ``../../include``.

3. Set the rights:
   ```sh
   $ sudo chown -hR www-data:www-data klausuromat
   $ sudo chown -hR www-data:www-data /var/www/html/includes
   ```

4. Open the default web server config in your favorite editor, e.g.:
   ```sh
   $ nano /etc/apache2/sites-enabled/000-default.conf
   ```

   And append the following code into you main virtual host:
   ```
   ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
           <Directory /usr/lib/cgi-bin>
                   AllowOverride None
                   Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
                   Require all granted
           </Directory>
   ```

5. Start cgi and restart apache:
   ```sh
   $ sudo a2enmod cgi
   $ sudo service apache2 reload
   ```

6. Done. Your instance of `klausuromat` is now reachable at ``http://yourIP/cgi-bin/klausuromat/gen.py``.
   You may want to tell your web server to open ``gen.py`` in that directory as index file.
