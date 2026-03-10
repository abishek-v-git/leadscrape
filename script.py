import os
os.chdir('/home/ubuntu/contact_search')
os.system("git reset --hard")
os.system("git pull")
os.system ('sudo chown :www-data ~/contact_search/')
os.system('sudo chmod 777 -R  ~/contact_search/')
os.system ('sudo systemctl restart apache2')
os.system ('cat /etc/apache2/envvars')
