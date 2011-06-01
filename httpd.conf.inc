<VirtualHost *:80>
        ServerName isupme.psimonkey.org.uk
        ServerAlias isup.psimonkey.org.uk
        DocumentRoot /var/www/isup.psimonkey.org.uk/dummy
        CustomLog /var/log/httpd/access_log full
        ErrorLog /var/log/httpd/error_log
        WSGIScriptAlias / /var/www/isup.psimonkey.org.uk/apache.wsgi
        <Directory /var/www/isup.psimonkey.org.uk/>
                Order allow,deny
                Allow from all
        </Directory>
</VirtualHost>