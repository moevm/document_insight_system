#!/bin/bash

# Usage

# sudo scripts/setup_apache_config.sh some_conf_from_apache_conf_dir.conf [ssl]

config=${1}
ssl_mod=${2:-''}

site_name="`basename ${config} .conf`"
cp apache_conf/${config} /etc/apache2/sites-available/${config}
ln -s /etc/apache2/sites-available/${config} /etc/apache2/sites-enabled/${config}

a2ensite ${site_name}

a2enmod proxy proxy_http proxy_wstunnel rewrite ${ssl_mod}

service apache2 restart
